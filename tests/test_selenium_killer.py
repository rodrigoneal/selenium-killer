import httpx
import pytest

from selenium_form_killer import SeleniumKiller


@pytest.fixture
def html():
    return """ 
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Test Soup</title>
    </head>
    <body>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </body>
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
