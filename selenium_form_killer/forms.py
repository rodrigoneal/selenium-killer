class Forms:
    def __init__(self, forms: list):
        self.forms = forms


class Form:
    def __init__(self, input: list["Input"]):
        self.inputs: list["Input"] = input


class Input:
    def __init__(self, name: str, value: str, type: str):
        self.name = name
        self.value = value
        self.type = type
