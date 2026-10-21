import random
from enum import Enum
import numpy as np
from typing import Tuple, List
from entities import Entity, EmptySpace, Tree, Plant
from predator import Predator
from herbivore import Herbivore

class EntityType(Enum):
    """
    Entity type definitions to be used throughout the code
    """
    EMPTY = 0
    TREE = 1
    PLANT = 2
    HERBIVORE = 3
    PREDATOR = 4

class Grid:
    def __init__(self, cfg):
        self.cfg = cfg
        self.grid = self.set_initial_grid(cfg.sim.initial_grid)
        self.num_rows = len(self.grid)
        self.num_cols = len(self.grid[0])

    @staticmethod
    def _get_new_entity(val: int, loc: Tuple[int, int], cfg) -> Entity:
        if val == EntityType.EMPTY:
            return EmptySpace(loc, cfg)
        elif val == EntityType.TREE:
            return Tree(loc, cfg)
        elif val == EntityType.PLANT:
            return Plant(cfg.entities.t_plant, loc, cfg)
        elif val == EntityType.HERBIVORE:
            return Herbivore(cfg.entities.t_herbivore, loc, cfg.entities.r_herbivore_sight, cfg.entities.t_cooldown, cfg)
        elif val == EntityType.PREDATOR:
            return Predator(cfg.entities.t_predator, loc, cfg.entities.r_predator_sight, cfg)
        else:
            #TODO: print error message without traceback
            raise ValueError(f"Unknown entity type: {val}")

    def set_initial_grid(self, initial_grid: List[List[int]]):
        grid = np.ndarray(shape=(len(initial_grid[0]), len(initial_grid[1])))
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                grid[row, col] = self._get_new_entity(initial_grid[row][col], (row, col), self.cfg)
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
                self.update_grid(e.loc, EmptySpace(e.loc, self.cfg))
            elif t == EntityType.HERBIVORE or t == EntityType.PREDATOR:
                e.move(self)
            else:
                raise ValueError(f"Entity type {t} is not moveable")

    def spawn_plants(self):
        empty_cells = self.get_all_type_cells(EntityType.EMPTY)
        for _ in range(random.randint(0, len(empty_cells))):
            loc = random.choice(empty_cells)
            if Plant.spawn(self.cfg.entitie.plant_spawn_threshold):
                self.update_grid(loc, Plant(self.cfg.entities.t_plant, loc, self.cfg))

    def simplify(self):
        simple_grid = []
        for row in range(self.num_rows):
            simple_grid.append([])
            for col in range(self.num_cols):
                e_type = self.grid[row, col].get_type()
                #TODO: get simple board with numbers
        return simple_grid

