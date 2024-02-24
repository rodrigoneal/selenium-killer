import asyncio
from copy import deepcopy
from typing import Annotated, Literal, Optional
from typing_extensions import Doc
import httpx

import requests

from selenium_killer.base.killer_base import KillerBase
from selenium_killer.forms.input import Form, FormInput
from selenium_killer.util.util import get_base_url, join_url_action


class SeleniumKiller(KillerBase):

    def __init__(self) -> None:
        self.url_base: str = None
        self.headers: Annotated[Optional[str], Doc("Cabecalhos da requisição")] = None
        self.data: Annotated[Optional[str], Doc("Dados da requisição")] = None
        self.cookies: Annotated[Optional[str], Doc("Cookies da requisição")] = None
        self._last_response = None
        self._forms: list[Form] = None
        self.status_code: Annotated[Optional[int], Doc("Status code da requisição")] = (
            None
        )
        self.session = httpx.AsyncClient()

    async def __aenter__(self):
            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    @property
    def forms(self) -> str:
        return deepcopy(self._forms)

    @forms.setter
    def forms(self, value: str) -> None:
        self._forms = value

    async def _requests(
        self, method: Literal["GET", "POST"], url: str, **kwargs
    ) -> requests.Response:
        return await self.session.request(method=method, url=url, **kwargs)

    async def send_request(
        self, method: Literal["GET", "POST"], url: str, **kwargs
    ) -> requests.Response:
        
        response = await self._requests(method=method, url=url, **kwargs)
        self.headers = response.headers
        self.cookies = response.cookies
        self.status_code = response.status_code
        self._last_response = response
        self.forms = self.extract_forms()
        self.url_base = get_base_url(str(response.url))
        return self

    async def get(
        self,
        url: str,
        headers: Optional[dict] = dict(),
        cookies: Optional[dict] = dict(),
        params: Optional[dict] = dict(),
        use_referer: bool = True,
        **kwargs,
    ) -> requests.Response:
        await self.make_request(
            method="GET",
            url=url,
            headers=headers,
            cookies=cookies,
            params=params,
            use_referer=use_referer,
            **kwargs,
        )

        return self

    def _prepare_form_to_request(
        self, form: Form, fields_delete: Optional[list[FormInput]]
    ) -> None:
        data = {"data": {}}
        data["method"] = form.method.upper()
        if form.url_base:
            data["url"] = join_url_action(form.url_base, form.action)
        else:
            data["url"] = join_url_action(self.url_base, form.action)
        for input_form in form.inputs:
            for field in fields_delete or []:
                if input_form.name == field.name:
                    continue
            data["data"][input_form.name] = input_form.value
        return data

    def post(
        self,
        url: Optional[str] = None,
        headers: Optional[dict[str, str]] = {},
        cookies: Optional[dict[str, str]] = {},
        data: Optional[dict[str, str]] = {},
        params: Optional[dict[str, str]] = {},
        use_referer: bool = True,
        inputs: Optional[list[FormInput] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional[Form] = False,
        exclude_forms: Optional[list[FormInput]] = None,
        **kwargs,
    ):
        return self.make_request(
            method="POST",
            url=url,
            headers=headers,
            cookies=cookies,
            data=data,
            params=params,
            use_referer=use_referer,
            inputs=inputs,
            token=token,
            form=form,
            exclude_forms=exclude_forms,
            **kwargs,
        )

    async def make_request(
        self,
        method: Literal["GET", "POST"],
        url: Optional[str] = None,
        headers: Optional[dict[str, str]] = {},
        cookies: Optional[dict[str, str]] = {},
        data: Optional[dict[str, str]] = {},
        params: Optional[dict[str, str]] = {},
        use_referer: bool = True,
        inputs: Optional[list[FormInput] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional[Form] = False,
        exclude_forms: Optional[list[FormInput]] = None,
        **httpx_options: dict[str, str],
    ) -> requests.Response:
        if use_referer and self.last_response:
            self.last_response.headers["Referer"] = str(self.last_response.url)
        if inputs:
            if not isinstance(inputs, list):
                inputs = [FormInput(**input) for input in inputs.items()]
            for input in inputs:
                data[input.name] = input.value
        if token:
            data.update(token)
        if form:
            request_data = self._prepare_form_to_request(form, exclude_forms)
            request_data["data"].update(data)
            request_data["data"].update(token)
            request_data.update(httpx_options)
            await self.send_request(**request_data)
            return self

        await self.send_request(
            method=method,
            url=url,
            headers=headers,
            cookies=cookies,
            data=data,
            params=params,
            **httpx_options,
        )
        return self


# <Cookies[<Cookie ASPSESSIONIDSUTQTRRS=BJEHECABAFOOMGIJHBEPFEOJ for solucoes.receita.fazenda.gov.br />, <Cookie TS017f82c2=01fef04d4ef3078714bd3a2e7cca8cdf506536966e40521faf56568b573163eb16f195634400b061f10133f1804593179f1575f1341fa8e35e33c8810a585480754ec78f3f for solucoes.receita.fazenda.gov.br />]>
