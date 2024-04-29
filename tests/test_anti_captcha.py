import os

import pytest
from selenium_form_killer.anti_captcha.anti_captcha import AntiCaptcha
from dotenv import load_dotenv


load_dotenv()

@pytest.mark.skipif(os.getenv("API_KEY") is None, reason="API_KEY not found")
async def test_captcha():
    anti_captcha = AntiCaptcha(os.getenv("API_KEY"))
    balance = await anti_captcha.get_balance()
    assert isinstance(balance, float)