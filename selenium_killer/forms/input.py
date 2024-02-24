from typing import Optional


class Form:
    def __init__(
        self,
        inputs: list["FormInput"],
        action: str,
        method: str,
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

    def __repr__(self) -> str:
        return str(f"<Form: {self.id=}>")


class FormInput:
    def __init__(self, name: str, value: str, type: str = "text") -> None:
        self.type = type
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return str(f"<FormInput: name:{self.name} type:{self.type} value:{self.value}>")

    def to_dict(self) -> dict:
        return {self.name: self.value}
