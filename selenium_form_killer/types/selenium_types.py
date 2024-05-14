from abc import ABC
from typing import Any, Optional, Sequence
from typing_extensions import Literal, Self
from bs4 import BeautifulSoup
import httpx

from selenium_form_killer.log.logger import get_logger
from selenium_form_killer.types.generic_types import ActionTypes


class SeleniumKillerABC(ABC):
    def __init__(
        self,
        headers: dict[str, str] = {},
        verbose: bool = False,
        **client_options: dict[str, Any],
    ) -> None:
        self.url_base: Optional[str] = None
        self.headers: Optional[dict[str, str]] = headers or {}
        self.data: Optional[str] = None
        self.cookies: Optional[str] = None
        self._response: httpx.Response = None
        self._forms: list[FormABC]
        self.status_code: Optional[int] = None
        self.session = httpx.AsyncClient(
            headers=headers,
            **client_options,
        )
        self.logger = get_logger(verbose)

    @classmethod
    def from_auth_data(
        cls, url: str, payload: dict, key_token: Optional[str] = None
    ) -> "SeleniumKillerABC":
        pass

    def __soup(self, html: Optional[str] = None) -> BeautifulSoup:
        pass

    def find(self, *args, html: Optional[str] = None, **kwargs) -> BeautifulSoup:
        pass

    def find_all(
        self, *args, html: Optional[str] = None, **kwargs
    ) -> list[BeautifulSoup]:
        pass

    def soup(self, html: Optional[str] = None) -> BeautifulSoup:
        pass

    async def __aenter__(self):
        self.logger.info("Entering async context")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.logger.info("Exiting async context")
        else:
            self.logger.critical(
                f"Exiting async context with exc_type:{exc_type}, exc_val:{exc_val}, exc_tb:{exc_tb}"
            )
        await self.session.aclose()
        self.logger.info("Session closed")

    def _forms_soup(self, html: Optional[str] = None) -> BeautifulSoup:
        pass

    @property
    def forms(self) -> list["FormABC"]:
        pass

    @forms.setter
    def forms(self, value: str) -> None:
        pass

    async def _requests(self, **kwargs) -> httpx.Response:
        pass

    async def send_request(
        self, method: Literal["GET", "POST"], url: str, **kwargs
    ) -> Self:
        pass

    
    async def get(
        self,
        url: str,
        headers: Optional[dict] = dict(),
        cookies: Optional[dict] = dict(),
        params: Optional[dict] = dict(),
        use_referer: bool = True,
        **kwargs,
    ) -> Self:
        pass

    
    def _prepare_form_to_request(
        self, form: "FormABC", fields_delete: Optional[list["FormInputABC"]]
    ) -> dict:
        pass

    
    def post(
        self,
        url: Optional[str] = None,
        headers: Optional[dict[str, str]] = {},
        cookies: Optional[dict[str, str]] = {},
        data: Optional[dict[str, str]] = {},
        params: Optional[dict[str, str]] = {},
        use_referer: bool = True,
        inputs: Optional[list["FormInputABC"] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional["FormABC"] = False,
        exclude_forms: Optional[list["FormInputABC"]] = None,
        **kwargs,
    ) -> Self:
        pass
    
    
    async def make_request(
        self,
        method: Literal["GET", "POST"],
        url: Optional[str] = None,
        headers: Optional[dict[str, str]] = {},
        cookies: Optional[dict[str, str]] = {},
        data: Optional[dict[str, str]] = {},
        params: Optional[dict[str, str]] = {},
        use_referer: bool = True,
        inputs: Optional[list["FormInputABC"] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional["FormABC"] = False,
        exclude_forms: Optional[list["FormInputABC"]] = None,
        **httpx_options: dict[str, str],
    ) -> httpx.Response:
        pass

    
    def extract_inputs(self, formulario: BeautifulSoup) -> list["FormInputABC"]:
        pass

    
    def extract_actions(self, formulario: BeautifulSoup) -> ActionTypes:
        pass

    
    def extract_captcha(self, formulario: BeautifulSoup) -> str | None:
        pass

     
    def extract_forms(self, html: Optional[str] = None) -> Sequence["FormABC"]:
        pass

    
    def extract_form(self, html: Optional[str] = None) -> "FormABC":
        pass

     
    async def save_html(self, name: str) -> None:
        pass

    
    def _save_file(self, path: str) -> None:
        pass

    
    async def save_file(self, path: str) -> None:
        pass


    @property
    def response(self) -> httpx.Response:
        pass

    @response.setter
    def response(self, response: httpx.Response) -> None:
        pass


class FormABC(ABC):
    def __init__(
        self,
        killer: "SeleniumKillerABC",
        inputs: list["FormInputABC"],
        action: str,
        method: str,
        id: Optional[str] = None,
        name: Optional[str] = None,
        captcha: Optional[str] = None,
        button: Optional[dict[str, str]] = None,
        url_base: Optional[str] = None,
    ) -> None:
        self.inputs = inputs
        self.action = action
        self.method = method
        self.id = id
        self.name = name
        self.button = button
        self.captcha = captcha
        self.url_base = url_base
        self.__killer = killer

    def pretty_print(self) -> None:
        pass

    def add_input(self, name: str, value: str, type: str = "text") -> None:
        pass

    def delete_input(self, name: str) -> None:
        pass

    def total_inputs(self) -> int:
        pass

    def get_input(self, name: str) -> "FormInputABC":
        pass

    def get_inputs_by_index(self, index: list[int]) -> list["FormInputABC"]:
        pass

    async def submit(
        self,
        url: Optional[str] = None,
        token: Optional[dict[str, str]] = {},
        method: str = None,
        input_data: str | list["FormInputABC"] | list[int] | None = "all",
        input_query_params: str | list["FormInputABC"] | list[int] | None = None,
        **kwargs,
    ) -> "SeleniumKillerABC":
        pass


class FormInputABC(ABC):
    def __init__(self, name: str, value: str, type: str = "text") -> None:
        self.type = type
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        pass

    def to_dict(self) -> dict:
        pass
