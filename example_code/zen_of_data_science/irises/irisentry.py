
import attrs
import attr
import pandas as pd
import typing

@attr.s(frozen=True, slots=True)
class IrisEntry:
    '''Represents a single iris.'''
    sepal_length: int = attrs.field(converter=float)
    sepal_width: int = attrs.field(converter=float)
    species: str = attrs.field(converter=str) 
    
    @classmethod
    def from_dataframe_row(cls, row: pd.Series):
        '''Class method constructor from dataframe row.'''
        new_obj: cls = cls(
            sepal_length = row['sepal_length'],
            sepal_width = row['sepal_width'],
            species = row['species'],
        )
        return new_obj
    
    @species.validator
    def species_validator(self, attr, value) -> None:
        if not len(value) > 0:
            raise ValueError(f'Attribute {attr.name} must be a '
                'string larger than 0 characters.')
    
    @sepal_length.validator
    @sepal_width.validator
    def meas_validator(self, attr, value) -> None:
        if not value > 0:
            raise ValueError(f'Attribute {attr.name} was '
                f'{value}, but it must be larger than zero.')
    
    def sepal_area(self) -> float:
        return self.sepal_length * self.sepal_width

