import asyncio
import os
from typing import Literal, Optional, Sequence
from urllib.parse import urlencode
import warnings

import chardet
import httpx
import requests
from bs4 import BeautifulSoup
from typing_extensions import override, Self

from selenium_form_killer.forms import Form, FormInput
from selenium_form_killer.types.generic_types import ActionTypes
from selenium_form_killer.types.selenium_types import (
    FormInputABC,
    SeleniumKillerABC,
)
from selenium_form_killer.util.util import get_base_url, join_url_action
from playwright.async_api import async_playwright


class SeleniumKiller(SeleniumKillerABC):
    def __init__(self, headers: dict[str, str] = {}, verbose: bool = False) -> None:
        super().__init__(headers=headers, verbose=verbose)

    @classmethod
    def from_auth_data(
        cls, url: str, payload: dict, key_token: Optional[str] = None
    ) -> "SeleniumKiller":
        """
        Faz uma solicitação POST para o URL fornecido com o payload e retorna uma nova instância de SeleniumKiller com o cabeçalho Authorization definido.

        Se o key_token não for fornecido, ele será padrão para "access_token".

        :param url: URL do endpoint
        :param payload: dados a serem enviados
        :param key_token: chave no JSON de resposta que contém o access_token

        """
        payload_data = urlencode(payload)
        key_token = key_token if key_token else "access_token"
        with httpx.Client() as client:  # Achei melhor não usar o proprio request do objeto para não sujar os cookies e etc.
            response = client.post(url, data=payload_data)
            response.raise_for_status()
            token = response.json()[key_token]
            headers = {"Authorization": f"Bearer {token}"}
            return cls(headers=headers, verbose=True)

    def find(self, *args, html: Optional[str] = None, **kwargs) -> BeautifulSoup:
        self.logger.info(f"find element with args: {args}, kwargs: {kwargs}")
        soup = self.soup(html)
        return soup.find(*args, **kwargs)

    def find_all(
        self, *args, html: Optional[str] = None, **kwargs
    ) -> list[BeautifulSoup]:
        self.logger.info(f"find elements with args: {args}, kwargs: {kwargs}")
        soup = self.soup(html)
        return soup.find_all(*args, **kwargs)

    def soup(self, html: Optional[str] = None) -> BeautifulSoup:
        html_text = html or self._response.text
        soup = BeautifulSoup(html_text, "html.parser")
        return soup

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

    @property
    def forms(self) -> list["Form"]:
        return self._forms

    @forms.setter
    def forms(self, value: str) -> None:
        self.logger.info(f"Forms: {value}")
        self._forms = value

    async def _requests(self, **kwargs) -> requests.Response:
        self.logger.info(
            f"Making request with kwargs: {kwargs}",
        )
        return await self.session.request(**kwargs)

    async def send_request(
        self, method: Literal["GET", "POST"], url: str, **kwargs
    ) -> requests.Response:
        response = await self._requests(method=method, url=url, **kwargs)
        encoding = chardet.detect(response.content)["encoding"]
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
    ) -> Self:
        self.logger.info(
            f"Making get request with url: {url}, headers:{headers}, cookies:{cookies}, params: {params}, use_referer: {use_referer}, kwargs: {kwargs}"
        )
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
    ) -> dict[str, str]:
        self.logger.info(
            f"Preparing form to request with form: {form}, fields_delete: {fields_delete}",
        )
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

    async def post(
        self,
        url: Optional[str] = None,
        headers: Optional[dict[str, str]] = {},
        cookies: Optional[dict[str, str]] = {},
        data: Optional[dict[str, str]] = {},
        params: Optional[dict[str, str]] = {},
        use_referer: bool = True,
        inputs: Optional[list["FormInput"] | dict[str, str]] = None,
        token: Optional[dict] = {},
        form: Optional["Form"] = None,
        exclude_forms: Optional[list["FormInput"]] = None,
        **kwargs,
    ) -> Self:
        self.logger.info(f"Making post request with url: {url} e kwargs: {kwargs}")

        return await self.make_request(
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

    async def render(self, timeout: int = 5, debug: bool = False) -> Self:
        """Renderiza a pagina que precisa de javascript para funcionar.
        Quando o modo debug for True o navegador vai desabilitar o headless.

        Keyword Arguments:
            timeout -- Tempo para aguardar a pagina a renderizar em segundos (default: {5})
            debug -- Habilita o modo debug (default: {False})

        Returns:
            self
        """
        _timeout = timeout * 1000
        self.logger.info(f"Renderizando a pagina com timeout: {timeout}")
        os_name = os.name
        if os_name == "nt":
            warnings.warn("A renderização no windows está muito lenta")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True if not debug else False,
                args=["--disable-web-security"],
                ignore_default_args=[
                    "--disable-extensions",
                    "--disable-default-apps",
                    "--disable-component-extensions-with-background-pages",
                ],
            )
            context = await browser.new_context(
                bypass_csp=True,
                java_script_enabled=True,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/105.0.5195.100 Mobile/15E148 Safari/604.1",
            )
            page = await context.new_page()
            if os_name == "nt":
                await page.set_content(
                    self.response.content.decode("utf-8"),wait_until="networkidle"
                )
            else:
                await page.set_content(
                    self.response.content.decode("utf-8"), timeout=_timeout
                )
            await page.wait_for_timeout(_timeout)
            html = await page.content()
            await browser.close()
            self._response = httpx.Response(
                content=html.encode("utf-8"), status_code=self.status_code, text=html
            )
            return self

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
    ) -> Self:
        if use_referer and self.response:
            self.logger.info(f"Using referer:{str(self.response.url)}")
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

    def extract_inputs(self, formulario: BeautifulSoup) -> list[FormInputABC]:
        inputs = formulario.find_all(["input", "textarea"])
        _inputs = []
        for input_tag in inputs:
            nome = input_tag.get("name")
            valor = input_tag.get("value", "")
            if input_tag.get("type"):
                _type = input_tag.get("type")
            else:
                _type = "text"
            form_input = FormInput(name=nome, value=valor, type=_type)
            self.logger.info(f"Extracting inputs: {form_input}")
            _inputs.append(form_input)
        return _inputs

    def extract_actions(self, formulario: BeautifulSoup) -> ActionTypes:
        form_action: ActionTypes = {
            "action": None,
            "id": None,
            "name": None,
            "method": None,
        }
        form_action["action"] = formulario.get("action")
        form_action["id"] = formulario.get("id")
        form_action["name"] = formulario.get("name")
        form_action["method"] = formulario.get("method")
        self.logger.info(f"Extracting actions from form:{form_action}")
        return form_action

    def extract_captcha(self, formulario: BeautifulSoup) -> str | None:
        captchas = formulario.find_all(
            class_=lambda value: value and "captcha" in value
        )
        for captcha in captchas:
            if data_site := captcha.get("data-sitekey"):
                self.logger.info(
                    f"Extracting captcha from form: {captcha} data-sitekey: {data_site}"
                )
                return data_site
            else:
                self.logger.error(
                    f"Extracting captcha from form: {captcha} not found data-sitekey"
                )
        return None

    @override
    def extract_forms(self, html: Optional[str] = None) -> Sequence["Form"]:
        self.logger.info("Extracting forms")
        forms = []
        for formulario in self.find_all("form", html=html):
            _captcha = self.extract_captcha(formulario)
            extract_actions = self.extract_actions(formulario)
            _inputs = self.extract_inputs(formulario)

            forms.append(
                Form(
                    killer=self,
                    inputs=_inputs,
                    captcha=_captcha,
                    button=None,
                    url_base=str(self.response.url),
                    **extract_actions,
                )
            )
        return forms

    async def save_html(self, name: str) -> None:
        path = name
        if not name.endswith(".html"):
            path = name + ".html"
        await asyncio.to_thread(self._save_file, path)

    def _save_file(self, path: str) -> None:
        self.logger.info(f"Saving file to: {path}")
        with open(path, "wb") as f:
            f.write(self.response.content)

    async def save_file(self, path: str) -> None:
        await asyncio.to_thread(self._save_file, path)

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
