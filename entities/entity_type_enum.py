from enum import Enum


class EntityType(Enum):
    """
    Entity type definitions to be used throughout the code
    """
    EMPTY = 0
    TREE = 1
    PLANT = 2
    HERBIVORE = 3
    PREDATOR = 4
