import os
import pytest


from selenium_form_killer import SeleniumKiller
from selenium_form_killer.capmonster.captcha_breaker import captcha_token
from capmonstercloudclient.requests import HcaptchaProxylessRequest
from dotenv import load_dotenv




load_dotenv()


@pytest.fixture
def killer():
    killer = SeleniumKiller()
    yield killer


def test_selenium_killer(killer):
    assert killer


async def test_form_submit():
    async with SeleniumKiller() as killer:
        await killer.get("https://www.google.com")
        killer.forms[0].inputs[5].value = "Brasil"
        await killer.forms[0].submit(
            method="GET",
            follow_redirects=True,
            input_query_params=[5],
            input_data=None,
        )
        assert (
            str(killer.response.request.url) == "https://www.google.com/search?q=Brasil"
        )


async def test_se_cria_um_contexto():
    token = os.getenv("API_KEY")
    cnpj = os.getenv("CNPJ")
    async with SeleniumKiller() as killer:
        await killer.get(
            "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_Solicitacao.asp"
        )
        captcha = await captcha_token(
            HcaptchaProxylessRequest(
                websiteKey=killer.forms[0].captcha, websiteUrl=str(killer.response.url)
            ),api_key=token
        )
        token = {"h-captcha-response": captcha['gRecaptchaResponse']}
        killer.forms[0].inputs[1].value = cnpj
        await killer.forms[0].submit(
            token=token,
            follow_redirects=True
        )

        await killer.save_html("cnpj")
    

