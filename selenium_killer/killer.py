import asyncio
from typing import Annotated, Literal, Optional
from typing_extensions import Doc
from bs4 import BeautifulSoup
import httpx
import chardet

import requests

from selenium_killer.util.util import get_base_url, join_url_action


class _SeleniumKiller:

    def __init__(self) -> None:
        self.url_base: str = None
        self.headers: Annotated[Optional[str], Doc("Cabecalhos da requisição")] = None
        self.data: Annotated[Optional[str], Doc("Dados da requisição")] = None
        self.cookies: Annotated[Optional[str], Doc("Cookies da requisição")] = None
        self._response = None
        self._forms: list[Form] = None
        self.status_code: Annotated[Optional[int], Doc("Status code da requisição")] = (
            None
        )
        self.session = httpx.AsyncClient()


    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)
    
    def __soup(self, html: Optional[str] = None) -> BeautifulSoup:
        html = html or self._response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup
    def find(self, *args, html: Optional[str] = None, **kwargs):
        soup = self.__soup(html)
        return soup.find(*args, **kwargs)

    def find_all(self, *args, html: Optional[str] = None, **kwargs):
        soup = self.__soup(html)
        return soup.find_all(*args, **kwargs)
    
    def soup(self, html: Optional[str] = None):
        return self.__soup(html)
    async def __aenter__(self):
        print("Iniciando Selenium Killer")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    def _forms_soup(self, html: Optional[str] = None) -> BeautifulSoup:
        html = html or self._response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("form")

    @property
    def forms(self) -> list["Form"]:
        return self._forms

    @forms.setter
    def forms(self, value: str) -> None:
        self._forms = value

    async def _requests(
        self, **kwargs
    ) -> requests.Response:
        return await self.session.request(**kwargs)

    async def send_request(
        self, method: Literal["GET", "POST"], url: str, **kwargs
    ) -> requests.Response:
        response = await self._requests(method=method, url=url, **kwargs)
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = encoding
        self.headers = response.headers
        self.cookies = response.cookies
        self.status_code = response.status_code
        self.response = response
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
        self, form: "Form", fields_delete: Optional[list["FormInput"]]
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
        inputs: Optional[list["FormInput"] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional["Form"] = False,
        exclude_forms: Optional[list["FormInput"]] = None,
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
        inputs: Optional[list["FormInput"] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional["Form"] = False,
        exclude_forms: Optional[list["FormInput"]] = None,
        **httpx_options: dict[str, str],
    ) -> requests.Response:
        if use_referer and self.response:
            self.response.headers["Referer"] = str(self.response.url)
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

    def extract_inputs(self, formulario: BeautifulSoup) -> list["FormInput"]:
        inputs = formulario.find_all(["input", "textarea"])
        _inputs = []
        for input_tag in inputs:
            nome = input_tag.get("name")
            valor = input_tag.get("value", "")
            if input_tag.get("type"):
                _type = input_tag.get("type")
            else:
                _type = "text"
            _inputs.append(FormInput(name=nome, value=valor, type=_type))
        return _inputs

    def extract_actions(self, formulario: BeautifulSoup) -> list[str]:
        form_action = {"action": None, "id": None, "name": None, "method": None}
        form_action["action"] = formulario.get("action")
        form_action["id"] = formulario.get("id")
        form_action["name"] = formulario.get("name")
        form_action["method"] = formulario.get("method")
        return form_action

    def extract_captcha(self, formulario: BeautifulSoup) -> str:
        captchas = formulario.find_all(
            class_=lambda value: value and "captcha" in value
        )
        for captcha in captchas:
            if captcha.get("data-sitekey"):
                return captcha.get("data-sitekey")

    def extract_forms(self, html: Optional[str] = None) -> list["Form"]:
        forms = []
        for formulario in self._forms_soup(html):
            _captcha = self.extract_captcha(formulario)
            extract_actions = self.extract_actions(formulario)
            _inputs = self.extract_inputs(formulario)
            forms.append(
                Form(
                    killer = self,
                    inputs=_inputs,
                    captcha=_captcha,
                    button=None,
                    url_base=str(self.response.url),
                    **extract_actions,
                )
            )
        return forms

    def _save_html(self, path: str) -> None:
        if path.endswith(".html"):
            path = path[:-5]

        with open(path + ".html", "wb") as f:
            f.write(self.response.content)

    async def save_html(self, path: str) -> None:
        await asyncio.to_thread(self._save_html, path)

    @property
    def response(self) -> httpx.Response:
        return self._response

    @response.setter
    def response(self, response: httpx.Response) -> None:
        self._response = response

    def __repr__(self) -> str:
        if self.response:
            return str(
                f"<SeleniumKiller: url={str(self.response.url)} status={self.response} >"
            )
        return str("<SeleniumKiller: None>")



SeleniumKiller: _SeleniumKiller = _SeleniumKiller()


class Form:
    def __init__(
        self,
        killer: _SeleniumKiller,
        inputs: list["FormInput"],
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

    def __repr__(self) -> str:
        return str(f"<Form: {self.id=}>")

    async def submit(
        self,
        token: Optional[dict[str, str]] = {},
        method: str = None,
        input_data: str | list["FormInput"] | list[int] | None = "all",
        input_query_params: str | list["FormInput"] | list[int] | None = None,
        **kwargs,
    ) -> _SeleniumKiller:
        if not self.method and not method:
            raise ValueError(
                "method is required" + "Form: " + str(self) + "Not have method"
            )
        elif method:
            self.method = method

        if input_query_params == "all":
            params = {input.name: input.value for input in self.inputs}
            kwargs["params"] = params
        elif isinstance(input_query_params, list):
            if isinstance(input_query_params[0], int):
                inputs = [self.inputs[indice] for indice in input_query_params]
                params = {input.name: input.value for input in inputs}
                kwargs["params"] = params
            elif isinstance(input_data[0], FormInput):
                 kwargs["params"] = {input.name: input.value for input in self.inputs}
        
        if input_data == "all":
            pass
        elif isinstance(input_data, list):
            if isinstance(input_data[0], int):
                self.inputs = [self.inputs[indice] for indice in input_data]
            elif isinstance(input_data[0], FormInput):
                self.inputs = input_data
        elif not input_data:
            self.inputs = []
        kwargs["data"] = {input.name: input.value for input in self.inputs}

        if token:
            kwargs["data"].update(token)
        
        url = join_url_action(self.url_base, self.action)

        await self.__killer.send_request(
            method=self.method, url=url, **kwargs
        )
        return self.__killer


class FormInput:
    def __init__(self, name: str, value: str, type: str = "text") -> None:
        self.type = type
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return str(f"<FormInput: name:{self.name} type:{self.type} value:{self.value}>")

    def to_dict(self) -> dict:
        return {self.name: self.value}

