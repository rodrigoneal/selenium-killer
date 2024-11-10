from typing import Optional, Sequence
from selenium_form_killer.util.util import join_url_action

from selenium_form_killer.types.selenium_types import (
    FormInputABC,
    SeleniumKillerABC,
    FormABC,
)


class Form(FormABC):
    def __init__(
        self,
        killer: "SeleniumKillerABC",
        inputs: Sequence["FormInput"],
        action: str | None,
        method: str | None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        captcha: Optional[str] = None,
        button: Optional[dict[str, str]] = None,
        url_base: Optional[str] = None,
    ) -> None:
        self.inputs = inputs
        self.action = action
        self.method = method
        self.id = id
        self.name = name
        self.button = button
        self.captcha = captcha
        self.url_base = url_base
        self.__killer = killer

    def pretty_print(self) -> None:
        from pprint import pprint

        for index, input in enumerate(self.inputs):
            pprint(f"{index}: {input}")

    def __repr__(self) -> str:
        if self.inputs:
            if len(self.inputs) > 9:
                str_inputs = ", ".join(
                    [
                        str(index) + ": " + str(input)
                        for index, input in enumerate(self.inputs[:9])
                    ]
                )
                str_inputs += ", ..."
                return str(f"<Form: {self.id=}, {str_inputs=} {self.captcha=}>")
            else:
                str_inputs = ", ".join(
                    [
                        str(index) + ": " + str(input)
                        for index, input in enumerate(self.inputs)
                    ]
                )
                return str(f"<Form: {self.id=}, {str_inputs=}>")
        return str(f"<Form: {self.id=}>")

    def add_input(self, name: str, value: str, type: str = "text") -> None:
        self.inputs.append(FormInput(name=name, value=value, type=type))

    def delete_input(self, name: str) -> None:
        self.inputs = [input for input in self.inputs if input.name != name]

    def total_inputs(self) -> int:
        return len(self.inputs)

    def get_input(self, name: str) -> "FormInput":
        for input in self.inputs:
            if input.name == name:
                return input

    def get_inputs_by_index(self, index: list[int]) -> list["FormInput"]:
        return [self.inputs[indice] for indice in index]

    async def submit(
        self,
        url: Optional[str] = None,
        token: Optional[dict[str, str]] = {},
        method: str = None,
        input_data: str | list["FormInput"] | list[int] | None = "all",
        input_query_params: str | list["FormInput"] | list[int] | None = None,
        **kwargs,
    ) -> "SeleniumKillerABC":
        self.__killer.logger.info(f"Submitting form: {self}")
        if not self.method and not method:
            raise ValueError(
                "method is required" + "Form: " + str(self) + "Not have method"
            )
        elif method:
            self.method = method
        if input_query_params == "all":
            params = {}
            params.update({input.to_dict() for input in self.inputs})
            kwargs["params"] = params
        elif isinstance(input_query_params, list):
            if isinstance(input_query_params[0], int):
                inputs = self.get_inputs_by_index(input_query_params)
                params = {input.name: input.value for input in inputs}
                kwargs["params"] = params
            elif isinstance(input_data[0], FormInput):
                kwargs["params"] = {input.name: input.value for input in self.inputs}

        if input_data == "all":
            pass
        elif isinstance(input_data, list):
            if isinstance(input_data[0], int):
                self.inputs = [self.inputs[indice] for indice in input_data]
            elif isinstance(input_data[0], FormInput):
                self.inputs = input_data
        elif isinstance(input_data, dict):
            self.inputs = [FormInput(name=k, value=v) for k, v in input_data.items()]
        elif not input_data:
            self.inputs = []
        kwargs["data"] = {input.name: input.value for input in self.inputs}

        if token:
            kwargs["data"].update(token)

        if not url:
            url = join_url_action(self.url_base, self.action)
        await self.__killer.send_request(method=self.method, url=url, **kwargs)
        return self.__killer


class FormInput(FormInputABC):
    def __init__(self, name: str, value: str, type: str = "text") -> None:
        self.type = type
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return str(f"<FormInput: name:{self.name} type:{self.type} value:{self.value}>")

    def to_dict(self) -> dict:
        return {self.name: self.value}
