import random
from typing import Tuple

from entities.entity_type_enum import EntityType


class Entity:
    """
    Entity class
    """

    def __init__(self, t: EntityType, lifespan: int, loc: Tuple[int, int], cfg) -> None:
        """
        Initializes the new entity

        Args:
            t (EntityType): Entity type
            lifespan (int): Lifespan of the entity
            loc (Tuple[int, int]): Location of the entity
            cfg: OmegaConf object
        """
        self.cfg = cfg
        self._type = t
        self.lifespan = lifespan
        self.curr_step = 0
        self.loc = loc

    def get_type(self) -> EntityType:
        """
        Returns the entity type
        """
        return self._type

    def is_still_alive(self) -> bool:
        """
        Checks if the entity is still alive (hasn't reached the lifespan)
        Returns:
            true if still alive, false otherwise
        """
        return self.curr_step < self.lifespan


class EmptySpace(Entity):
    """
    Empty space class
    """

    def __init__(self, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.EMPTY, -1, loc, cfg)


class Tree(Entity):
    """
    Tree class. Trees are treated as walls on the board and are impassable to all entities
    """

    def __init__(self, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.TREE, -1, loc, cfg)


class Plant(Entity):
    """
    Plant class
    """

    def __init__(self, lifespan: int, loc: Tuple[int, int], cfg):
        super().__init__(EntityType.PLANT, lifespan, loc, cfg)

    @staticmethod
    def spawn(spawn_threshold: float) -> bool:
        """
        Decides whether to spawn a new plant at random

        Args:
            spawn_threshold (float): Threshold for spawning a new plant (between 0 and 1)

        Returns:
            true if the random number is over the threshold, false otherwise

        """
        return random.random() > spawn_threshold

    def increase_step(self):
        """
        Increases the step counter
        """
        self.curr_step += 1
