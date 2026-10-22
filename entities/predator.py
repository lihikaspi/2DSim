from typing import Tuple

from entities.entity import EmptySpace
from entities.entity_type_enum import EntityType
from entities.mobile_entity import MobileEntity


class Predator(MobileEntity):
    """
    Predator class. Inherits from MobileEntity
    """
    def __init__(self, lifespan: int, loc: Tuple[int, int], r: int, cfg) -> None:
        """
        Initializes the predator

        Args:
            lifespan (int): Lifespan of the predator
            loc (Tuple[int, int]): Location of the predator
            r (int): Sight radius for hunting
            cfg: OmegaConf object
        """
        super().__init__(EntityType.PREDATOR, lifespan, loc, r, cfg)

    def move(self, grid) -> None:
        """
        Move the predator. Implements the abstract method from MobileEntity

        Args:
            grid: Grid object
        """
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            # print(f"INFO:{self.loc}: predator reached lifespan")
            return

        next_move = self.get_next_move(grid, predator=True)
        target_entity = grid.grid[next_move]

        if target_entity.get_type() == EntityType.HERBIVORE:
            self.curr_step = 0
        else:
            self.curr_step += 1

        # print(f"INFO:{self.loc} -> {next_move}: predator moved")
        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)
