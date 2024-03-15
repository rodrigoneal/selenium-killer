from httpx import Client
import httpx
import pytest
from selenium_form_killer.killer import SeleniumKiller


def test_se_chama_a_proxima_funcao():
    class Teste(SeleniumKiller):
        def inicializar(self, session):
            yield {"next": self.parser}

        def parser(self,session, response):
            return "response"

    obj = Teste()
    assert obj.run() == "response"


def test_se_se_raise_value_erro_se_ficar_em_loop():
    class Teste(SeleniumKiller):
        def inicializar(self, session):
            yield {"next": self.parser}

        def parser(self, session, response):
            yield {"next": self.parser}

    obj = Teste(limit_call_same_method=1)
    with pytest.raises(ValueError):
        obj.run()

def test_se_faz_uma_requisicao():
    class Teste(SeleniumKiller):
        def inicializar(self, session):            
            yield {"next": self.parser}


        def parser(self, session: Client, response):
            response = session.get("https://www.google.com.br/")
            return response.status_code

    obj = Teste()
    assert obj.run() == 200

def test_se_pega_response_da_requisicao():
    class Teste(SeleniumKiller):
        def inicializar(self, session):            
            yield {"next": self.parser}

        def parser(self, session: Client, response):
            session.get("https://www.google.com.br/")
            yield {"next": self.response}
        
        def response(self, session: Client, response):
            return str(response.url)

    obj = Teste()
    assert obj.run() == "https://www.google.com.br/"

def test_se_pega_a_referencia_da_chamada_anterior():
    class Teste(SeleniumKiller):
        def inicializar(self, session):            
            yield {"next": self.google}

        def google(self, session: Client, response):
            session.get("https://www.google.com.br/")
            yield {"next": self.facebook}
        
        def facebook(self, session: Client, response):
            session.get("https://www.facebook.com/")
            yield {"next": self.response}
        
        def response(self, session: Client, response):
            return response.headers["Referer"]

    obj = Teste()
    assert obj.run() == "https://www.facebook.com/"

def test_se_funciona_com_assincrono():
    class Teste(SeleniumKiller):
        def __init__(self, limit_call_same_method: int = 10, client = httpx.AsyncClient):
            super().__init__(limit_call_same_method, client)
        def inicializar(self, session):            
            yield {"next": self.parser}

        async def parser(self, session: Client, response):
            await session.get("https://www.google.com.br/")
            yield {"next": self.response}
        
        async def response(self, session: Client, response):
            return str(response.url)

    obj = Teste()
    assert obj.run() == "https://www.google.com.br/"