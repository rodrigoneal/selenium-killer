import asyncio
import httpx


class AntiCaptcha:
    def __init__(self, api_key: str):
        self.__api_key = api_key

    @property
    def api_key(self):
        raise NotImplementedError("Tá loucão?")

    @api_key.setter
    def api_key(self, api_key):
        self.__api_key = api_key

    async def create_task(
        self,
        client: httpx.AsyncClient,
        *,
        img_base_64: str,
        phase: bool = False,
        case: bool = False,
        numeric: int = 0,
        math: bool = False,
        min_length: int = 0,
        max_length: int = 0,
    ) -> dict:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        json_data = {
            "clientKey": self.__api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": img_base_64,
                "phrase": phase,
                "case": case,
                "numeric": numeric,
                "math": math,
                "minLength": min_length,
                "maxLength": max_length,
            },
            "softId": 0,
        }

        return await client.post(
            "https://api.anti-captcha.com/createTask",
            json=json_data,
            headers=headers,
        )

    async def task_result(self, client: httpx.AsyncClient, task_id: str) -> dict:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        json_data = {
            "clientKey": self.__api_key,
            "taskId": task_id,
        }
        return await client.post(
            "https://api.anti-captcha.com/getTaskResult",
            json=json_data,
            headers=headers,
        )

    async def solver(
        self,
        img_base_64: str,
        phase: bool = False,
        case: bool = False,
        numeric: int = 0,
        math: bool = False,
        min_length: int = 0,
        max_length: int = 0,
        ready_wait: float = 30,
    ):
        async with httpx.AsyncClient(timeout=30) as client:
            task = await self.create_task(
                client=client,
                img_base_64=img_base_64,
                phase=phase,
                case=case,
                numeric=numeric,
                math=math,
                min_length=min_length,
                max_length=max_length,
            )
            result_task = task.json()["taskId"]
            time_to_wait = ready_wait * 2
            for _ in range(time_to_wait):
                result = await self.task_result(client=client, task_id=result_task)
                if result.json()["status"] == "ready":
                    return result.json()["solution"]["text"]
                else:
                    await asyncio.sleep(0.5)
            raise TimeoutError("O captcha demorou mais tempo que o esperado.")

    async def get_balance(self) -> float:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anti-captcha.com/getBalance",
                json={"clientKey": self.__api_key},
            )
            try:
                return float(response.json()["balance"])
            except KeyError:
                KeyError(
                    "O AntiCaptcha retornou um valor inválido ou a API KEY esta errada."
                )
