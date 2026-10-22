import random
from typing import List, Tuple

import numpy as np

from entities.entity import EmptySpace, Entity, Plant, Tree
from entities.entity_type_enum import EntityType
from entities.herbivore import Herbivore
from entities.predator import Predator


class Grid:
    """
    Grid object class. Handles all grid updates and checks
    """

    def __init__(self, initial_grid: List[List[int]], cfg) -> None:
        """
        Initializes the grid using the given initial grid

        Args:
            initial_grid (List[List[int]]): Initial grid state
            cfg: OmegaConf object
        """
        self.cfg = cfg
        self.num_rows = len(initial_grid)
        self.num_cols = len(initial_grid[0])
        self.grid = self.set_initial_grid(initial_grid)

    @staticmethod
    def _get_new_entity(val: int, loc: Tuple[int, int], cfg) -> Entity:
        """
        create a new entity of the given type in the given location. raises error if given type is not a valid.

        Args:
            val (int): new entity type
            loc (Tuple[int, int]): location
            cfg: OmegaConf config object

        Returns:
            new entity
        """
        ent = EntityType(val)
        if ent == EntityType.EMPTY:
            return EmptySpace(loc, cfg)
        elif ent == EntityType.TREE:
            return Tree(loc, cfg)
        elif ent == EntityType.PLANT:
            return Plant(cfg.entities.t_plant, loc, cfg)
        elif ent == EntityType.HERBIVORE:
            return Herbivore(
                cfg.entities.t_herbivore,
                loc,
                cfg.entities.r_herbivore_sight,
                cfg.entities.t_cooldown,
                cfg,
            )
        elif ent == EntityType.PREDATOR:
            return Predator(
                cfg.entities.t_predator, loc, cfg.entities.r_predator_sight, cfg
            )
        else:
            # TODO: print error message without traceback
            raise ValueError(f"Unknown entity type: {val}")

    def set_initial_grid(self, initial_grid: List[List[int]]) -> np.ndarray:
        """
        Initializes the starting grid with Entity type objects

        Args:
            initial_grid ([List[int]]): Initial grid state

        Returns:
            new grid with Entity objects as values

        """
        grid = np.ndarray(shape=(self.num_rows, self.num_cols), dtype=Entity)
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                grid[row, col] = self._get_new_entity(
                    initial_grid[row][col], (row, col), self.cfg
                )
        return grid

    def is_in_grid(self, x: int, y: int) -> bool:
        """
        Checks if the given position is within the grid

        Args:
            x (int): row position
            y (int): column position

        Returns:
            true if position is within the grid, false otherwise

        """
        return not (x >= self.num_rows or x < 0 or y >= self.num_cols or y < 0)

    def update_grid(self, loc: Tuple[int, int], new_ent: Entity) -> None:
        """
        Updates the given position in the grid

        Args:
            loc (Tuple[int, int]): new position
            new_ent (Entity): new entity
        """
        self.grid[loc] = new_ent

    def get_radius_coords(
        self, loc: Tuple[int, int], radius: int
    ) -> Tuple[int, int, int, int]:
        """
        Calculates the starting and ending indexes of the rows and columns from the main grid to include only cells
        within a given radius of the given location

        Args:
            loc (Tuple[int, int]): new position
            radius (int): radius around the location

        Returns:
            starting and ending indexes of the rows and columns: r_start, r_end, c_start, c_end
        """
        r_start = max(0, loc[0] - radius)
        r_end = min(self.num_rows, loc[0] + radius + 1)
        c_start = max(0, loc[1] - radius)
        c_end = min(self.num_cols, loc[1] + radius + 1)
        return r_start, r_end, c_start, c_end

    def get_truncated_grid(self, loc: Tuple[int, int], radius: int) -> np.ndarray:
        """
        Truncates the main grid in a given radius around the given position

        Args:
            loc (Tuple[int, int]): position to truncate around
            radius (int): radius around the location

        Returns:
            new truncated grid
        """
        r_start, r_end, c_start, c_end = self.get_radius_coords(loc, radius)
        return self.grid[r_start:r_end, c_start:c_end]

    def is_valid_move(
        self, row: int, col: int, visited: List[List[bool]] = None
    ) -> bool:
        """
        Checks if the given location is free to move to.

        Checks the basic requirements (inside the grid, not stepping on Trees or Predators, and not a visited
        cell if inside the BFS search) and can be used for all types of entities

        Args:
            row (int): row position
            col (int): column position  :
            visited (List[List[bool]], optional): visited cells in BFS search. Defaults to None.

        Returns:
            true if location is free to move to, false otherwise
        """
        return (
            self.is_in_grid(row, col)
            and (not visited[row][col] if visited is not None else True)
            and self.grid[row, col].get_type() is not EntityType.TREE
            and self.grid[row, col].get_type() is not EntityType.PREDATOR
        )

    def is_in_radius(
        self, loc: Tuple[int, int], row: int, col: int, radius: int
    ) -> bool:
        """
        Checks if the given position is within the radius of the given location

        Args:
            loc (Tuple[int, int]): main position for the radius
            row (int): row position to check
            col (int): column position to check
            radius (int): radius around the location

        Returns:
            true if location is within the radius of the given location, false otherwise
        """
        r_start, r_end, c_start, c_end = self.get_radius_coords(loc, radius)
        return r_start <= row < r_end and c_start <= col < c_end

    def check_herbivores_repro(self, ent1: Entity, ent2: Entity) -> bool:
        """
        checks if two given Herbivores can reproduce. If either given entity is not a Herbivore returns true always

        Args:
            ent1 (Entity): first entity
            ent2 (Entity): second entity

        Returns:
            returns true if both given Herbivores can reproduce, false otherwise
        """
        if (
            ent1.get_type() == EntityType.HERBIVORE
            and ent2.get_type() == EntityType.HERBIVORE
        ):
            return Herbivore.check_reproduction_possibility(ent1, ent2)
        return True

    def get_valid_moves(self, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Calculates all valid moves for a given location

        Args:
            loc (Tuple[int, int]): location to calculate valid moves for

        Returns:
            List[Tuple[int, int]]: list of locations of all valid moves

        """
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        moves = [
            n.loc
            for n in neighbors
            if n.loc != loc
            and self.is_valid_move(n.loc[0], n.loc[1])
            and self.check_herbivores_repro(self.grid[loc], n)
        ]
        return moves

    def get_empty_neighbors(self, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Calculates all empty neighbors for a given location

        Args:
            loc (Tuple[int, int]): location to calculate empty neighbors for

        Returns:
            List[Tuple[int, int]]: list of locations of all empty neighbors
        """
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        empty_neighbors = [n.loc for n in neighbors if n.get_type() == EntityType.EMPTY]
        return empty_neighbors

    def get_all_type_cells(self, t: EntityType, only_loc: bool = True):
        """
        Calculates all type cells in the board for a given type

        Args:
            t (EntityType): type to calculate type cells for
            only_loc (bool, optional): return only locations of the entities. Defaults to True.

        Returns:
            list of all type cells, containing either locations or entities
        """
        all_cells = self.grid.flatten()
        type_cells = [c.loc if only_loc else c for c in all_cells if c.get_type() == t]
        return type_cells

    def step_per_type(self, t: EntityType) -> None:
        """
        performs a step for all entities of a given type sequentially

        Args:
            t (EntityType): type to perform step for
        """
        ents = self.get_all_type_cells(t, only_loc=False)
        moved = set()
        for e in ents:
            if id(e) in moved or self.grid[e.loc] is not e:
                continue
            if t == EntityType.PLANT:
                e.increase_step()
                if not e.is_still_alive():
                    self.update_grid(e.loc, EmptySpace(e.loc, self.cfg))
            elif t == EntityType.HERBIVORE or t == EntityType.PREDATOR:
                moved.add(id(e))
                e.move(self)
            elif t == EntityType.EMPTY or t == EntityType.TREE:
                raise ValueError(f"Entity type {t} is not moveable")

    def spawn_plants(self):
        """
        Spawns plants at random empty locations. If no plants are still alive, not spawning
        """
        if len(self.get_all_type_cells(EntityType.PLANT)) == 0:
            return
        empty_cells = self.get_all_type_cells(EntityType.EMPTY)
        for _ in range(random.randint(0, len(empty_cells))):
            loc = random.choice(empty_cells)
            if self.grid[loc].get_type() == EntityType.EMPTY and Plant.spawn(
                self.cfg.entities.plant_spawn_threshold
            ):
                self.update_grid(loc, Plant(self.cfg.entities.t_plant, loc, self.cfg))

    def simplify(self) -> List[List[int]]:
        """
        Simplifies the grid to be print ready. Uses the entity type to char mapping found in the config object

        Returns:
            List[List[int]]: simplified grid
        """
        mapping = self.cfg.pretty_print
        return [
            [
                mapping[self.grid[r, c].get_type().name.lower()]
                for c in range(self.num_cols)
            ]
            for r in range(self.num_rows)
        ]
