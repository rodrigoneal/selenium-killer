import asyncio
from inspect import iscoroutinefunction, isgeneratorfunction, isasyncgenfunction
from typing import List, TypeVar, Generic, Dict, Callable, Union, Generator
from abc import ABC, abstractmethod
import httpx

SessionType = TypeVar("SessionType")
ClientType = TypeVar("ClientType")


async def runner(method):
    async for value in method:
        return value


class SeleniumKiller(Generic[SessionType, ClientType], ABC):
    def __init__(self, limit_call_same_method: int = 10, client: ClientType = None):
        self.lasts_methods: List[
            Callable[
                [SessionType, ClientType],
                Union[
                    Dict[
                        str,
                        Callable[
                            [SessionType, ClientType], Union[Dict[str, Callable], str]
                        ],
                    ],
                    str,
                ],
            ]
        ] = []
        self.limit_call_same_method = limit_call_same_method
        self._response: httpx.Response = None
        if client:
            self.session = client(event_hooks={"response": [self.async_response_hook]})
        else:
            self.session: ClientType = httpx.Client(
                event_hooks={"response": [self.response_hook]}
            )

    @abstractmethod
    def inicializar(
        self, session: SessionType
    ) -> Generator[
        Dict[str, Callable[[SessionType, ClientType], Union[Dict[str, Callable], str]]],
        None,
        None,
    ]:
        ...

    async def async_response_hook(self, response: httpx.Response) -> None:
        response.headers["Referer"] = str(response.url)
        self._response = response

    def response_hook(self, response: httpx.Response) -> None:
        response.headers["Referer"] = str(response.url)
        self._response = response

    def run(
        self,
    ) -> Union[
        Dict[str, Callable[[SessionType, ClientType], Union[Dict[str, Callable], str]]],
        str,
    ]:
        method_info = next(self.inicializar(session=self.session))
        while True:
            try:
                next_method = method_info["next"]
            except TypeError:
                return method_info
            if next_method:
                self.lasts_methods.append(next_method)
                if isgeneratorfunction(next_method):
                    method_info = next(
                        next_method(session=self.session, response=self._response)
                    )
                elif iscoroutinefunction(next_method):
                    method_info = asyncio.run(
                        next_method(session=self.session, response=self._response)
                    )
                elif isasyncgenfunction(next_method):
                    value = next_method(session=self.session, response=self._response)
                    method_info = asyncio.run(runner(value))
                else:
                    return next_method(session=self.session, response=self._response)
            else:
                return next_method
            contagem_metodos = {}
            for metodo in self.lasts_methods:
                if metodo not in contagem_metodos:
                    contagem_metodos[metodo] = 1
                else:
                    contagem_metodos[metodo] += 1
            if any(
                valor > self.limit_call_same_method
                for valor in contagem_metodos.values()
            ):
                raise ValueError("Metodo inválido")
