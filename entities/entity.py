import random

from config import Config
from entities.entity_type_enum import EntityType
from entities.location import Location


class Entity:
    """
    Entity class
    """

    def __init__(
        self, t: EntityType, lifespan: int, loc: Location, cfg: Config
    ) -> None:
        """
        Initializes the new entity

        Args:
            t (EntityType): Entity type
            lifespan (int): Lifespan of the entity
            loc (Location): Location of the entity
            cfg (Config): OmegaConf object
        """
        self.cfg = cfg
        self.type = t
        self.lifespan = lifespan
        self.curr_step = 0
        self.loc = loc

    def is_still_alive(self) -> bool:
        """
        Checks if the entity is still alive (hasn't reached the lifespan)
        Returns:
            true if still alive, false otherwise
        """
        if self.lifespan == self.cfg.entities.never_dead:
            return True
        return self.curr_step < self.lifespan

    def kill(self) -> None:
        """
        kills the entity
        """
        if self.lifespan == self.cfg.entities.never_dead:
            raise ValueError(f"Entity {self.type} does not have an age")
        self.curr_step = self.lifespan

    def increase_age(self) -> None:
        """
        Increases the age of the entity
        """
        if self.lifespan == self.cfg.entities.never_dead:
            raise ValueError(f"Entity {self.type} does not have an age")
        self.curr_step += 1

    def refuel_age(self) -> None:
        """
        resets the age of the entity
        """
        if self.lifespan == self.cfg.entities.never_dead:
            raise ValueError(f"Entity {self.type} does not have an age")
        self.curr_step = 0


class EmptySpace(Entity):
    """
    Empty space class
    """

    def __init__(self, loc: Location, cfg: Config) -> None:
        super().__init__(EntityType.EMPTY, cfg.entities.never_dead, loc, cfg)


class Tree(Entity):
    """
    Tree class. Trees are treated as walls on the board and are impassable to all entities
    """

    def __init__(self, loc: Location, cfg: Config) -> None:
        super().__init__(EntityType.TREE, cfg.entities.never_dead, loc, cfg)


class Plant(Entity):
    """
    Plant class
    """

    def __init__(self, lifespan: int, loc: Location, cfg: Config) -> None:
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
