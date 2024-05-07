import httpx
import pytest

from selenium_form_killer import SeleniumKiller


@pytest.fixture
def html():
    return """
    <html>
    <head>
    </head>
    <body>
        <h1>Teste selenium killer</h1>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <form action="http://www.google.com/search" method="get">
            <input type="text" name="q" />
            <input type="text" class="captcha" data-sitekey="123456789" />
            <input type="submit" />
        </form>
    </body>
    """


@pytest.fixture
def html_google():
    return """
    <html><head><title>Pesquisa - Google</title></head>
    <body><div id="res"><center><h3>Pesquisa Google</h3>
    <b>Pesquisa relacionada</b><br>
    <a href="https://www.google.com.br/search?q=selenium+killer" target="_blank">Selenium Killer</a>
    </center></div></body></html>
    """


@pytest.fixture
def killer():
    killer = SeleniumKiller()
    yield killer


def test_selenium_killer(killer):
    assert killer


@pytest.mark.respx(base_url="https://foo.bar")
def test_from_auth_data_success(respx_mock):
    respx_mock.post("/auth").mock(
        return_value=httpx.Response(200, json={"access_token": "test"})
    )
    killer = SeleniumKiller.from_auth_data(
        "https://foo.bar/auth", {"username": "test", "password": "test"}
    )
    assert killer.headers["Authorization"].startswith("Bearer test")


@pytest.mark.respx(base_url="https://foo.bar")
async def test_from_auth_data_failure(respx_mock):
    respx_mock.post("/auth").mock(return_value=httpx.Response(401))
    with pytest.raises(httpx.HTTPStatusError):
        SeleniumKiller.from_auth_data(
            "https://foo.bar/auth", {"username": "test", "password": "test"}
        )


@pytest.mark.respx(base_url="https://foo.bar")
async def test_from_auth_data_custom_key_token(respx_mock):
    respx_mock.post("/auth").mock(
        return_value=httpx.Response(200, json={"token": "test"})
    )
    killer = SeleniumKiller.from_auth_data(
        "https://foo.bar/auth",
        {"username": "test", "password": "test"},
        key_token="token",
    )
    assert killer.headers["Authorization"].startswith("Bearer ")


def test_soup(killer, html):
    soup = killer.soup(html)
    assert soup.find("li").text == "Item 1"


def test_find(killer, html):
    return killer.find("li", html=html).text == "Item 1"


def test_find_all(killer, html):
    return len(killer.find_all("li", html=html)) == 2


@pytest.mark.respx(base_url="https://foo.bar")
async def test_se_faz_get(killer, respx_mock, html):
    respx_mock.get("/zoo").mock(return_value=httpx.Response(200, html=html))
    await killer.get("https://foo.bar/zoo")
    assert killer.response.status_code == 200


@pytest.mark.respx(base_url="https://foo.bar")
async def test_se_faz_post(killer, respx_mock, html):
    respx_mock.post("/zoo").mock(return_value=httpx.Response(200, html=html))
    await killer.post("https://foo.bar/zoo")
    assert killer.response.status_code == 200


@pytest.mark.respx(base_url="https://foo.bar")
async def test_se_pega_o_form(killer, respx_mock, html):
    respx_mock.get("/zoo").mock(return_value=httpx.Response(200, html=html))
    await killer.get("https://foo.bar/zoo")
    assert len(killer.forms) == 1


@pytest.mark.respx(base_url="https://foo.bar")
async def test_se_pega_o_form_input_e_captcha(killer, respx_mock, html):
    respx_mock.get("/zoo").mock(return_value=httpx.Response(200, html=html))
    await killer.get("https://foo.bar/zoo")
    assert killer.forms[0].captcha
    assert killer.forms[0].inputs[0]


async def test_se_pega_o_form_faz_submit(killer, respx_mock, html, html_google):
    respx_mock.get("https://foo.bar/zoo").mock(
        return_value=httpx.Response(200, html=html)
    )
    await killer.get("https://foo.bar/zoo")
    respx_mock.get("http://www.google.com/search").mock(
        return_value=httpx.Response(200, html=html_google)
    )
    await killer.forms[0].submit()
    assert "Selenium Killer" in killer.response.text


async def test_se_renderiza_pagina(killer: SeleniumKiller):
    await killer.get("https://aguasdorio.com.br/comunicados/")
    await killer.render(timeout=0, debug=True)
    await killer.save_html("render")
