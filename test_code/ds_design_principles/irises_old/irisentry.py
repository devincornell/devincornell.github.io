
import attrs
import attr
import pandas as pd
import typing

from .ids import IrisEntryID

@attr.s(frozen=True, slots=True)
class IrisEntry:
    '''Represents a single piece of data in your dataset.'''
    __slots__ = []
    
    # good idea to make custom times for IDs to make things clearer to the reader 
    # (esp when you have many types of ids that are all strings)
    idx: IrisEntryID = attrs.field()
    
    # these are all measurements in the attrs dataframe
    sepal_length: int = attrs.field(converter=float)
    sepal_width: int = attrs.field(converter=float)
    petal_length: int = attrs.field(converter=float)
    petal_width: int = attrs.field(converter=float)

    
    # adding converter=str makes sure that the property is a string (and string convertable)
    # these will both be validated later using the species_validator method.
    species: str = attrs.field(converter=str) 
    
    ################### Class Construction and Validators ###################
    
    # class constructors are great btw
    @classmethod
    def from_dataframe_row(cls, idx: IrisEntryID, row: pd.Series):
        '''Class constructor from dataframe row.'''
        
        # create intermediate variable with type hint to indicate
        # this function will return whatever type it is
        new_obj: cls = cls(
            idx=idx,
            sepal_length = row['sepal_length'],
            sepal_width = row['sepal_width'],
            petal_length = row['petal_length'],
            petal_width = row['petal_width'],
            species = row['species'],
        )
        return new_obj
    
    # validates the length of names
    @species.validator
    def species_validator(self, attr, value) -> None:
        if not len(value) > 0:
            raise ValueError(f'Attribute {attr} must be a '
                'string larger than 0 characters.')
        
    # this can act as a validator for all of these attributes by adding the decorators
    @sepal_length.validator
    @sepal_width.validator
    @petal_length.validator
    @petal_width.validator
    def meas_validator(self, attr, value) -> None:
        if not value > 0:
            raise ValueError(f'Attribute {attr.name} was {value}, but it must be larger than zero.')
        
        
    ################### Methods ###################
    
    def sepal_area(self) -> float:
        return self.sepal_length * self.sepal_width

