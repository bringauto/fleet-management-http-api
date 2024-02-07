

# Car

## Post

Requirements:
- [PlatformHWId](#platformhwid) must exist and must not be used by some other Car.

Result:
- Car is created.

## Delete

Requirements:
- There must not be any order referencing the car.

Result:
- Car is deleted.
- All [Car States](#car-state) referencing the Car are deleted.

# Car State

There is a maximum number $N_{states}$ of Car States to be stored in the API.

## Post

Requirements:
- [Car](#car) must exist.
- Unique ID.

Result:
- Car State ID is automatically generated/overwritten before being stored by the API.
- Car State is created.
- Oldest Car States might be deleted, so the number of states stored by the API is not greater than $N_{states}$.

# PlatformHWId

Requirements:
- Unique ID.