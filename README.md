# Selenium Killer

## Introdução

O Selenium Killer é uma biblioteca que permite usar o httpx para realizar requisições e capturar os dados de um site. Assim voce pode usar a biblioteca para automatizar tarefas como: 

- Capturar os dados de um site
- Realizar requisições POST
- Realizar requisições GET
- Enviar formulários

## Como Usar


Use o Selenium Killer como um contexto com o `async with`.

o `async with` permite que o Selenium Killer seja usado dentro de um contexto assíncrono fechando a conexão quando o contexto for concluído.

O selenium killer factory retornando sempre uma instância de SeleniumKiller.

## Exemplo
```python
from seleniumkiller import SeleniumKiller

async def main():
    async with SeleniumKiller() as killer:
        await killer.get('https://www.google.com.br/')
        await killer.save_html('teste')
```
Mantendo todos os dados da requisição anterior, você pode fazer formularios mais facilmente pois os cookies e os cabecalhos da requisição são mantidos.

```python
from seleniumkiller import SeleniumKiller

async def main():
    async with SeleniumKiller() as killer:
        await killer.get('https://www.google.com.br/')
        killer.last_response.cookies
        killer.last_response.headers
```

## Formulários

Quando você enviar um get ou um post, o selenium killer vai capturar todos os formulários da página e retornar uma lista com todos os formulários da pagina.

```python
from seleniumkiller import SeleniumKiller

async def main():
    async with SeleniumKiller() as killer:
        await killer.get('https://www.google.com.br/')
        killer.forms
```
retorna um instancia de `Form`.

### Form

Formularios da pagina.

Form -> inputs: list["FormInput"],
        action: str,
        method: str,
        id: Optional[str] = None,
        name: Optional[str] = None,
        captcha: Optional[str] = None,
        button: Optional[dict[str, str]] = None,
        url_base: Optional[str] = None,

    inputs: inputs da pagina.
    action: url do action form.
    method: metodo do form.
    id: id do form.
    name: nome do form.
    captcha: captcha do form.
    button: botão do form.
    url_base: url base do form.

### Disclaimer
As vezes a base da pagina é diferente do que a base da requisição. Por isso você pode passar a base_url para facilitar a chamada do form.