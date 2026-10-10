from __future__ import annotations

from typing import Annotated, NewType
from pydantic import BaseModel, Field, RootModel, model_validator

class Point(BaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

class PointList(RootModel[list[Point]]):
    '''List of points.'''
    def mean(self) -> float:
        pass

PointName = NewType('PointName', str)

class PointMap(RootModel[dict[PointName, Point]]):
    '''Dictionary mapping point names to points.'''
    def names(self) -> list[PointName]:
        return list(self.root.keys())

    def point_list(self) -> PointList:
        return PointList(root=list(self.root.values()))

class UniqueNamesList(RootModel[list[PointName]]):
    @model_validator(mode='after')
    def check_uniqueness(self) -> None:
        if len(self.root) != len(set(self.root)):
            raise ValueError("All names in the list must be unique")


class RadialPoint(BaseModel):
    r: Annotated[float, Field(description='Radius of the point in polar coords.')]
    theta: Annotated[float, Field(description='Angle of the point in polar coords.')]

    @classmethod
    def from_cartesian(cls, point: 'Point') -> typing.Self:
        """Transforms the upstream Point type into this downstream type."""
        return cls(
            r=math.sqrt(point.x**2 + point.y**2),
            theta=math.atan2(point.y, point.x),
        )
