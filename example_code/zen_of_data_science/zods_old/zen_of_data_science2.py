from __future__ import annotations
import attrs
import attr
import typing

class PersonAgeOutOfRangeError(ValueError):
    pass

class PersonNameEror(ValueError):
    pass

class PersonNameWasEmptyError(PersonNameEror):
    pass

class PersonFirstLastNameError(PersonNameEror):
    pass

@attr.s
class Person:
    age: int = attrs.field(converter=float)
    full_name: int = attrs.field(converter=str)
    
    @age.validator
    def validate_age(self, attr, value):
        if value < 0 or value > 150:
            raise PersonAgeOutOfRangeError(f'{attr.name} must be between '
                f'0 and 150')
    
    @full_name.validator
    def validate_name(self, attr, full_name: str):
        if not len(full_name):
            raise PersonNameWasEmptyError(f'{attr.name} cannot '
                f'be empty string.')
        
        elif not len(full_name.split()) > 1:
            raise PersonFirstLastNameError(f'{attr.name} requires '
                f'first and last names.')

person_data = [
    {'age': 22, 'name': 'jose rodriguez'},
    {'age': 5, 'name': 'johnny'},
    {'age': 30, 'name': 'carol carn'},
    {'age': 55, 'name': 'david duke'},
]


if __name__ == '__main__':
    
    people = list()
    num_invalid = 0
    for d in person_data:
        try:
            people.append(Person(age=d['age'], full_name=d['name']))
        except PersonFirstLastNameError:
            num_invalid += 1
        
    try:
        Person(age=10, full_name='')
    except (PersonFirstLastNameError, PersonNameWasEmptyError):
        pass

    print(len(people))
    print(Person(age=10, full_name='yo holla'))

    #Person(age=None, full_name='Jose')
    #Person(age=10, full_name='Jose')
    #Person(age=-1, full_name='jose dillan')

    try:
        Person(age=-1, full_name='jose dillan')
    except PersonAgeOutOfRangeError as e:
        print(type(e))

    try:
        Person(age=10, full_name='')
    except PersonNameWasEmptyError as e:
        print(type(e))

    try:
        Person(age=10, full_name='Jose')
    except PersonFirstLastNameError as e:
        print(type(e))
    
    try:
        Person(age=10, full_name='Jose')
    except ValueError as e:
        print(type(e))

