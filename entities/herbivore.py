import random
from entities.entity import EmptySpace
from entities.entity_type_enum import EntityType
from entities.mobile_entity import MobileEntity
from typing import Tuple


class Herbivore(MobileEntity):
    def __init__(self, lifespan: int, loc: Tuple[int, int], r: int, t_cooldown: int, cfg):
        super().__init__(EntityType.HERBIVORE, lifespan, loc, r, cfg)
        self._t_cooldown = t_cooldown
        self._steps_since_repro = None

    def get_steps_since_repro(self) -> int:
        return self._steps_since_repro

    def get_cooldown(self) -> int:
        return self._t_cooldown

    def move(self, grid):
        if not self.is_still_alive():
            grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
            print(f"INFO:{self.loc}: herbivore reached lifespan")
            return

        if self._steps_since_repro is not None:
            self._steps_since_repro += 1

        next_move = self.get_next_move(grid, predator=False)
        next_move_entity = grid.grid[next_move]

        if next_move_entity.get_type() == EntityType.HERBIVORE and next_move != self.loc:
            if (Herbivore.can_reproduce(self._steps_since_repro, self._t_cooldown)
                    and Herbivore.can_reproduce(next_move_entity.get_steps_since_repro(), next_move_entity.get_cooldown())):
                self.reproduction(grid, next_move)
                self._steps_since_repro = 0
            self.curr_step += 1
            return

        if next_move_entity.get_type() == EntityType.PLANT:
            self.curr_step = 0
        else:
            self.curr_step += 1

        print(f"INFO:{self.loc} -> {next_move}: herbivore moved")
        grid.update_grid(self.loc, EmptySpace(self.loc, self.cfg))
        self.loc = next_move
        grid.update_grid(next_move, self)

    @staticmethod
    def can_reproduce(steps_since: int, cooldown: int) -> bool:
        return steps_since is None or steps_since >= cooldown

    def reproduction(self, grid, partner_loc: Tuple[int, int]):
        neighbors = grid.get_empty_neighbors(partner_loc)
        if not neighbors:
            print(f"INFO:{self.loc}: no empty neighboring cell, can't reproduce")
            return
        repro_loc = random.choice(neighbors)
        grid.update_grid(repro_loc, Herbivore(self.lifespan, repro_loc, self._radius, self._t_cooldown, self.cfg))
        print(f"INFO:{self.loc}: herbivore reproduced")
        print(f"INFO:{repro_loc}: new herbivore spawned after reproduction")