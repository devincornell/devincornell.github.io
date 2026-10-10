from __future__ import annotations

import math
from typing import Annotated, Self
from pydantic import BaseModel, Field

class CartesianPoint(BaseModel):
    '''A single point in Cartesian space'''
    x: Annotated[float, Field(description="The x-coordinate")]
    y: Annotated[float, Field(description="The y-coordinate")]

    @classmethod
    def from_polar(cls, point: PolarPoint) -> Self:
        """Transforms the upstream PolarPoint type into this downstream CartesianPoint type."""
        return cls(
            x=point.r * math.cos(point.theta),
            y=point.r * math.sin(point.theta),
        )

    def to_polar(self) -> PolarPoint:
        """Transforms this Cartesian point into a polar point."""
        return PolarPoint.from_cartesian(self)

class PolarPoint(BaseModel):
    '''A single point in polar coordinates'''
    r: Annotated[float, Field(description='Radius of the point in polar coords.')]
    theta: Annotated[float, Field(description='Angle of the point in polar coords.')]

    @classmethod
    def from_cartesian(cls, point: CartesianPoint) -> Self:
        """Transforms the upstream Point type into this downstream type."""
        return cls(
            r=math.sqrt(point.x**2 + point.y**2),
            theta=math.atan2(point.y, point.x),
        )

    def to_cartesian(self) -> CartesianPoint:
        """Transforms this polar point into a Cartesian point."""
        return CartesianPoint.from_polar(self)
