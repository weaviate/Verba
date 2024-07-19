from pydantic import BaseModel
from typing import Literal, Union

class InputConfig(BaseModel):
    type: Literal["number", "text", "dropdown", "password"]
    value: Union[int, str]
    description: str
    values: list[str]
