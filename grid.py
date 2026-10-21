import random

import numpy as np
from typing import Tuple, List
from consts import EntityType, ENTITIES
from entities import Entity, EmptySpace, Tree, Plant
from predator import Predator
from herbivore import Herbivore
from mobile_entity import MobileEntity

class Grid:
    def __init__(self, initial_grid: List[List[int]]):
        self.grid = self.set_initial_grid(initial_grid)
        self.num_rows = len(initial_grid)
        self.num_cols = len(initial_grid[0])

    @staticmethod
    def _get_new_entity(val: int, loc) -> Entity:
        if val == EntityType.EMPTY:
            return EmptySpace(loc)
        elif val == EntityType.TREE:
            return Tree(loc)
        elif val == EntityType.PLANT:
            return Plant(ENTITIES.T_PLANT, loc)
        elif val == EntityType.HERBIVORE:
            return Herbivore(ENTITIES.T_HERBIVORE, loc, ENTITIES.R_HERBIVORE_SIGHT, ENTITIES.T_COOLDOWN)
        elif val == EntityType.PREDATOR:
            return Predator(ENTITIES.T_PREDATOR, loc, ENTITIES.R_PREDATOR_SIGHT)
        else:
            #TODO: print error message without traceback
            raise ValueError(f"Unknown entity type: {val}")

    def set_initial_grid(self, initial_grid: List[List[int]]):
        grid = np.ndarray(shape=(len(initial_grid[0]), len(initial_grid[1])))
        for row in initial_grid:
            for col in row:
                grid[row, col] = self._get_new_entity(int(row[col]), (row, col))
        return grid

    def is_in_grid(self, x: int, y: int):
        return not (x >= self.num_rows or x < 0 or y >= self.num_cols or y < 0)

    def update_grid(self, loc: Tuple[int, int], new_ent: Entity):
        if self.grid[loc] is not None and self.grid[loc].get_type() == EntityType.HERBIVORE:
            self.grid[loc] = [self.grid[loc], new_ent]
        self.grid[loc] = new_ent

    def get_radius_coords(self, loc: Tuple[int, int], radius: int) -> Tuple[int, int, int, int]:
        r_start = max(0, loc[0] - radius)
        r_end = min(self.num_rows, loc[0] + radius + 1)
        c_start = max(0, loc[1] - radius)
        c_end = min(self.num_cols, loc[1] + radius + 1)
        return r_start, r_end, c_start, c_end

    def get_truncated_grid(self, loc: Tuple[int, int], radius:int) -> np.ndarray:
        r_start, r_end, c_start, c_end = self.get_radius_coords(loc, radius)
        return self.grid[r_start:r_end, c_start:c_end]

    def is_valid_move(self, row: int, col: int, visited=None) -> bool:
        return (self.is_in_grid(row, col)
                and (not visited[row,col] if visited is not None else True)
                and self.grid[row,col] not in [EntityType.TREE, EntityType.PREDATOR])

    def is_in_radius(self, loc: Tuple[int, int], row: int, col: int, radius: int) -> bool:
        r_start, r_end, c_start, c_end = self.get_radius_coords(loc, radius)
        return r_start <= row < r_end and c_start <= col < c_end

    def get_valid_moves(self, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        moves = [n.loc for n in neighbors if self.is_valid_move(n.loc[0], n.loc[1])]
        return moves

    def get_empty_neighbors(self, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        empty_neighbors = [n.loc for n in neighbors if n.get_type() == EntityType.EMPTY]
        return empty_neighbors

    def get_all_type_cells(self, t: EntityType, only_loc: bool = True):
        all_cells = self.grid.flatten()
        type_cells = [c.loc if only_loc else c for c in all_cells if c.get_type() == t]
        return type_cells

    def step_per_type(self, t: EntityType) -> None:
        ents = self.get_all_type_cells(t, only_loc=False)
        for e in ents:
            if t == EntityType.PLANT and not e.is_still_alive():
                self.update_grid(e.loc, EmptySpace(e.loc))
            elif t == EntityType.HERBIVORE or t == EntityType.PREDATOR:
                e.move(self)
            else:
                raise ValueError(f"Entity type {t} is not moveable")

    def spawn_plants(self):
        empty_cells = self.get_all_type_cells(EntityType.EMPTY)
        for _ in range(random.randint(0, len(empty_cells))):
            loc = random.choice(empty_cells)
            if Plant.spawn():
                self.update_grid(loc, Plant(ENTITIES.T_PLANT, loc))

    def simplify(self):
        simple_grid = []
        for row in range(self.num_rows):
            simple_grid.append([])
            for col in range(self.num_cols):
                e_type = self.grid[row, col].get_type()
                #TODO: get simple board with numbers
        return simple_grid

