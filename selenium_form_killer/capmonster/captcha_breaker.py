from capmonstercloudclient import CapMonsterClient, ClientOptions

from capmonstercloudclient.requests.baseRequest import BaseRequest

from selenium_form_killer.log.logger import get_logger

logger = get_logger()


async def captcha_token(
    request_captcha: BaseRequest, api_key: str, client_timeout: int = 30
) -> dict[str, str]:
    client_options = ClientOptions(api_key=api_key, client_timeout=client_timeout)
    cap_monster_client = CapMonsterClient(options=client_options)
    logger.info("Solving captcha...")
    response = await cap_monster_client.solve_captcha(request_captcha)
    logger.info("Captcha solved!")
    return response
