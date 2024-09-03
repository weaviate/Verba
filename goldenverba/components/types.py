from pydantic import BaseModel
from typing import Literal, Union

class InputConfig(BaseModel):
    type: Literal["number", "text", "dropdown", "password", "bool", "multi"]
    value: Union[int, str, bool]
    description: str
    values: list[str]
