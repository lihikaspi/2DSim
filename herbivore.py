from entities import EmptySpace
from mobile_entity import MobileEntity
from grid import Grid, EntityType
from typing import Tuple
import random

class Herbivore(MobileEntity):
    def __init__(self, lifespan: int, loc: Tuple[int, int], r: int, t_cooldown: int, cfg):
        super().__init__(EntityType.HERBIVORE, lifespan, loc, r, cfg)
        self._t_cooldown = t_cooldown
        self._steps_since_repro = None

    def move(self, grid: Grid):
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            print(f"INFO:{self.loc}: herbivore reached lifespan")
            return
        if self._steps_since_repro is not None:
            self._steps_since_repro += 1

        next_move = self.get_next_move(grid)
        self.curr_step = 0 if grid.grid[next_move].get_type() == EntityType.PLANT else self.curr_step + 1
        if grid.grid[next_move].get_type() == EntityType.HERBIVORE and self.can_reproduce():
            self.reproduction(grid, next_move)
            self._steps_since_repro = 1

        print(f"INFO:{self.loc} -> {next_move}: herbivore moved")
        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)

    def can_reproduce(self):
        return self._steps_since_repro is None or self._steps_since_repro > self._t_cooldown

    def reproduction(self, grid: Grid, next_move: Tuple[int, int]):
        repro_loc = random.choice(grid.get_empty_neighbors(next_move))
        grid.update_grid(repro_loc, Herbivore(self.lifespan, repro_loc, self._radius, self._t_cooldown, self.cfg))
        print(f"INFO:{self.loc}: herbivore reproduced")
        print(f"INFO:{repro_loc}: new herbivore spawned after reproduction")