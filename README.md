# Selenium Killer

## Introdução

O Selenium Killer é uma biblioteca que permite usar o httpx para realizar requisições e capturar os dados de um site. Assim você pode usar a biblioteca para automatizar tarefas como: 

- Capturar os dados de um site
- Realizar requisições POST
- Realizar requisições GET
- Enviar formulários

Ele surge como uma necessidade de automação, pois abrir navegador é um processo caro e demorado.

O Selenium Killer não tem renderização por javascript. Logo para tarefas que exigem interação por javascript, você deve usar o Selenium ou alguma biblioteca parecida.

## Como Usar


O coração do Selenium Killer é a classe `SeleniumKiller` que contém as funções `get`, `post` e `forms`.

## Exemplos
Importar e instanciar
```python
from selenium_killer.killer import SeleniumKiller
killer = SeleniumKiller()
```
A selenium killer é baseada no padrão factory pattern. Sempre retornando uma nova instancia do mesmo objeto.

Exemplo de uso
```python
killer = SeleniumKiller()
killer.get('https://google.com')
killer.forms
killer.post('https://google.com')
```

## Uso

Vamos fazer um requisição para o site https://google.com e capturar os dados de um formulário:

```python
killer = SeleniumKiller()
await killer.get('https://google.com')
forms = killer.forms
forms[0].submit()
forms[0].fields
```