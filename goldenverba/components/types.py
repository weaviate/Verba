from pydantic import BaseModel
from typing import Literal, Union

class InputConfig(BaseModel):
    type: Literal["number", "text"]
    value: Union[int, str]
    description: str
