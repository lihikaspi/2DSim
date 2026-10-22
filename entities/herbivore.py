import random
from typing import Tuple

from omegaconf import DictConfig, ListConfig

from config import Config
from entities.entity import EmptySpace
from entities.entity_type_enum import EntityType
from entities.mobile_entity import MobileEntity
from entities.location import Location


class Herbivore(MobileEntity):
    """
    Herbivore class. Inherits from MobileEntity
    """

    def __init__(self, lifespan: int, loc: Location, r: int, t_cooldown: int, cfg: Config) -> None:
        """
        Initializes a Herbivore object

        Args:
            lifespan (int): Lifespan of the entity
            loc (Location): Location of the entity
            r (int): sight radius for hunting
            t_cooldown (int): Cooldown time after reproduction
            cfg (Config): OmegaConf object
        """
        super().__init__(EntityType.HERBIVORE, lifespan, loc, r, cfg)
        self.t_cooldown = t_cooldown
        self.steps_since_repro = None

    def reset_steps_since_repro(self) -> None:
        """
        Resets the number of steps since reproduction
        """
        self.steps_since_repro = 0

    def move(self, grid) -> None:
        """
        moves the entity. Implements the abstract method from MobileEntity.

        Args:
            grid: Grid object
        """
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            return

        if self.steps_since_repro is not None:
            self.steps_since_repro += 1

        next_move = self.get_next_move(grid, predator=False)
        next_move_entity = grid.grid[next_move.coords]

        if next_move_entity.type == EntityType.HERBIVORE and next_move.coords != self.loc.coords:
            if Herbivore.check_reproduction_possibility(self, next_move_entity):
                if self.reproduction(grid, next_move):
                    self.reset_steps_since_repro()
                    next_move_entity.reset_steps_since_repro()
            self.curr_step += 1
            return

        if next_move_entity.type == EntityType.PLANT:
            self.refuel_age()
        else:
            self.increase_age()

        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)

    @staticmethod
    def can_reproduce(steps_since: int, cooldown: int) -> bool:
        """
        check if a herbivore can reproduce given the steps since the reproduction and cooldown period
        Args:
            steps_since (int): Number of steps since reproduction
            cooldown (int): Cooldown time after reproduction

        Returns:
            true if herbivore can reproduce, false otherwise
        """
        return steps_since is None or steps_since >= cooldown

    @staticmethod
    def check_reproduction_possibility(herb1: Herbivore, herb2: Herbivore) -> bool:
        """
        checks if two herbivores can reproduce with each other
        Args:
            herb1 (Herbivore): first Herbivore
            herb2 (Herbivore): second Herbivore

        Returns:
            true if herbivore can reproduce, false otherwise
        """
        return Herbivore.can_reproduce(
            herb1.steps_since_repro, herb1.t_cooldown
        ) and Herbivore.can_reproduce(herb2.steps_since_repro, herb2.t_cooldown)

    def reproduction(self, grid, partner_loc: Location) -> bool:
        """
        performs the reproduction of a new Herbivore. If there are no empty neighboring cells reproduction is canceled

        Args:
            grid: Grid object
            partner_loc (Tuple[int, int]): Location of the partner

        Returns:
            true if reproduction happened, false otherwise
        """
        neighbors = grid.get_empty_neighbors(partner_loc)
        if not neighbors:
            return False
        repro_loc = random.choice(neighbors)
        grid.update_grid(
            repro_loc,
            Herbivore(
                self.lifespan, repro_loc, self._radius, self.t_cooldown, self.cfg
            ),
        )
        return True
