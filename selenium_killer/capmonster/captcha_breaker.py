import os
from capmonstercloudclient import CapMonsterClient, ClientOptions

from capmonstercloudclient.requests.baseRequest import BaseRequest
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")


async def captcha_token(request_captcha: BaseRequest) -> str:
    client_options = ClientOptions(api_key=API_KEY, client_timeout=30)
    cap_monster_client = CapMonsterClient(options=client_options)
    responses = await cap_monster_client.solve_captcha(request_captcha)

    return responses["gRecaptchaResponse"]
