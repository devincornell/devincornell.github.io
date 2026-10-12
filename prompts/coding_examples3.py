from __future__ import annotations

from typing import Annotated
from dataclasses import dataclass, asdict
import dataclasses
from pydantic import BaseModel, Field
import uuid

@dataclass(slots=True, frozen=True)
class UserInfo:
    name: Annotated[str, Field(description="Public name of the user.", default='<NAME_EMPTY>')]
    age: Annotated[int, Field(description="Age of the user (does not appear publicly).", gt=0, lt=150)]

class User(BaseModel):
    uuid: Annotated[str, Field(description="Unique identifier of the instance.")]
    info: UserInfo

@dataclass(slots=True, frozen=True)
class UserDataclass:
    info: UserInfo


d = asdict(UserDataclass(info=UserInfo(name="Alice", age=30)))
print(d)
exit()

# schema generation:
# model_json_schema uses the dataclass Field metadata to generate the schema
User.model_json_schema()
import json
print(json.dumps(User.model_json_schema(), indent=2))

user = User.model_validate({
    'info': {
        'age': -4
    }
})
print(user)


UserInfo(age=10)
