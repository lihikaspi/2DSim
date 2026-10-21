from entities.entity_type_enum import EntityType
from entities.entity import EmptySpace
from entities.mobile_entity import MobileEntity
from typing import Tuple

class Predator(MobileEntity):
    def __init__(self, lifespan: int, loc: Tuple[int, int], r: int, cfg):
        super().__init__(EntityType.PREDATOR, lifespan, loc, r, cfg)

    def move(self, grid) -> None:
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            print(f"INFO:{self.loc}: predator reached lifespan")
            return

        next_move = self.get_next_move(grid)
        self.curr_step = 0 if grid.grid[next_move].get_type() == EntityType.HERBIVORE else self.curr_step + 1

        print(f"INFO:{self.loc} -> {next_move}: herbivore moved")
        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)