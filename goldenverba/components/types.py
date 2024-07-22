from pydantic import BaseModel
from typing import Literal, Union

class InputConfig(BaseModel):
    type: Literal["number", "text", "dropdown", "password", "bool"]
    value: Union[int, str, bool]
    description: str
    values: list[str]
