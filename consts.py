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

class ENTITIES:
    T_PLANT = 10
    T_HERBIVORE = 15
    R_HERBIVORE_SIGHT = 3
    T_COOLDOWN = 20
    T_PREDATOR = 20
    R_PREDATOR_SIGHT = 5
    PLANT_SPAWN_THRESHOLD = 0.5

class GRID:
    SIZE = (30,30)

class PRETTY_PRINT:
    EMPTY = '.'
    TREE = '^'
    PLANT = '*'
    HERBIVORE = 'H'
    PREDATOR = 'P'
