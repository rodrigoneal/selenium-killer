import asyncio
from typing import Annotated, Optional

import httpx
from bs4 import BeautifulSoup
from typing_extensions import Doc

from selenium_killer.forms.input import Form, FormInput


class KillerBase:
    client: Annotated[httpx.Client, Doc("Classe httpx.Client")] = httpx.Client()

    def __init__(self) -> None:
        self.headers: Annotated[Optional[str], Doc("Cabecalhos da requisição")] = None
        self.data: Annotated[Optional[str], Doc("Dados da requisição")] = None
        self.cookies: Annotated[Optional[str], Doc("Cookies da requisição")] = None
        self._last_response = None
        self.status_code: Annotated[Optional[int], Doc("Status code da requisição")] = (
            None
        )

    def _forms_soup(self, html: Optional[str] = None) -> BeautifulSoup:
        html = html or self.last_response.text
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all("form")

    def extract_inputs(self, formulario: BeautifulSoup) -> list[FormInput]:
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

    def extract_captcha(self, formulario: BeautifulSoup) -> str:
        captchas = formulario.find_all(
            class_=lambda value: value and "captcha" in value
        )
        for captcha in captchas:
            if captcha.get("data-sitekey"):
                return captcha.get("data-sitekey")

    def extract_actions(self, formulario: BeautifulSoup) -> list[str]:
        form_action = {"action": None, "id": None, "name": None, "method": None}
        form_action["action"] = formulario.get("action")
        form_action["id"] = formulario.get("id")
        form_action["name"] = formulario.get("name")
        form_action["method"] = formulario.get("method")
        return form_action

    def extract_forms(self, html: Optional[str] = None) -> list[Form]:
        forms = []
        for formulario in self._forms_soup(html):
            _captcha = self.extract_captcha(formulario)
            extract_actions = self.extract_actions(formulario)
            _inputs = self.extract_inputs(formulario)
            forms.append(
                Form(inputs=_inputs, captcha=_captcha, button=None, **extract_actions)
            )
        return forms

    def _save_html(self, path: str, enconding: str = "utf-8") -> None:
        if path.endswith(".html"):
            path = path[:-5]
        with open(path + ".html", "w", encoding=enconding) as f:
            f.write(self.last_response.text)

    async def save_html(self, path: str, enconding: str = "utf-8") -> None:
        await asyncio.to_thread(self._save_html, path, enconding)

    @property
    def last_response(self) -> httpx.Response:
        return self._last_response

    def __repr__(self) -> str:
        if self.last_response:
            return str(
                f"<SeleniumKiller: url={str(self.last_response.url)} status={self.last_response} >"
            )
        return str("<SeleniumKiller: None>")
