import json
import os
import httpx
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


@pytest.mark.skipif(os.getenv("API_KEY") is None, reason="API_KEY not found")
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
            ),
            api_key=token,
        )
        token = {"h-captcha-response": captcha["gRecaptchaResponse"]}
        killer.forms[0].inputs[1].value = cnpj
        await killer.forms[0].submit(token=token, follow_redirects=True)

        await killer.save_html("cnpj")

@pytest.mark.skipif(os.getenv("USERNAME") is None, reason="USERNAME not found")
async def test_se_faz_login_e_salva_no_cabecalho():
    SeleniunKiller = SeleniumKiller.from_auth_data(
        "https://apiredigital.redasset.com.br/api/login",
        {
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
            "grant_type": "password",
        },
    )
    async with SeleniunKiller as killer:
        json_data = {
            "dat_vencimento_ini": "2024-04-01",
            "dat_vencimento_fin": "2024-04-30",
            "nro_cpf_cnpj": "",
            "nro_titulo": "",
            "cod_cedente": "41208",
            "opcao": 4,
        }
        await killer.post(
            "https://apiredigital.redasset.com.br/api/operacao/pesquisaBoletos", json=json_data
        )
        json_data = killer.response.json()[0]
        await killer.post('https://apiredigital.redasset.com.br/api/operacao/imprimirBoletos',json=[json_data])
        url = killer.response.json()["mensagem"]
        await killer.get(url)
        await killer.save_file("boleto.pdf")
        assert killer.response
