from abc import ABC
from typing import Tuple
import random
from grid import EntityType

class Entity(ABC):
    """
    Abstract class for entities on the board
    """
    def __init__(self, t: EntityType, lifespan: int, loc: Tuple[int, int], cfg):
        self.cfg = cfg
        self._type = t
        self.lifespan = lifespan
        self.curr_step = 0
        self.loc = loc

    def get_type(self) -> EntityType:
        return self._type

    def is_still_alive(self):
        return self.curr_step < self.lifespan

class EmptySpace(Entity):
    def __init__(self, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.EMPTY, -1, loc, cfg)

class Tree(Entity):
    def __init__(self, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.TREE, -1, loc, cfg)

class Plant(Entity):
    def __init__(self, lifespan: int, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.PLANT, lifespan, loc, cfg)

    @staticmethod
    def spawn(spawn_threshold):
        return random.random() > spawn_threshold


