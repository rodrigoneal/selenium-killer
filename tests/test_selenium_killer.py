from pathlib import Path

import pytest

from selenium_killer import SeleniumKiller


@pytest.fixture
def killer():
    killer = SeleniumKiller()
    yield killer


def test_selenium_killer(killer):
    assert killer


def test_selenium_killer_get(killer):
    assert killer.get(
        "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/emitir"
    )


def test_save_html(killer):
    killer.get(
        "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp"
    )
    killer.save_html("teste")
    path = Path("teste.html")
    assert path.exists()
    path.unlink()


def test_selenium_killer_post(killer):
    assert killer.post(
        "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/emitir"
    )


def test_selenium_killer_extract_captcha(killer):
    killer.get(
        "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp"
    )
    assert killer.extract_captcha()


def test_selenium_killer_extract_inputs(killer):
    killer.get(
        "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp"
    )
    assert killer.extract_inputs()


def test_selenium_killer_url_base(killer):
    killer.get(
        "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp"
    )
    assert killer.url_base == "https://solucoes.receita.fazenda.gov.br"
