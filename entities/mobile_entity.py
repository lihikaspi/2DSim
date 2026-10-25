import random
from abc import ABC, abstractmethod
from collections import deque
from typing import List
import logging
logger = logging.getLogger(__name__)

from config import Config
from entities.entity import Entity
from entities.entity_type_enum import EntityType
from entities.location import Location


class MobileEntity(ABC, Entity):
    """
    Abstract mobile Entity class. Inherits from Entity
    """

    def __init__(self, t: EntityType, lifespan: int, loc: Location, radius: int, cfg: Config) -> None:
        """
        Initializes a mobile entity

        Args:
            t (EntityType): entity type
            lifespan (int): lifespan of the entity
            loc (Location): location of the entity
            radius (int): sight radius for hunting
            cfg (Config): OmegaConf object
        """
        super().__init__(t, lifespan, loc, cfg)
        self._radius = radius

    def bfs(self, grid, target: EntityType, loc: Location) -> List[Location]:
        """
        Breadth-first search (BFS) finding the shortest path to target within the sight radius

        Args:
            grid: Grid object
            target (EntityType): target entity type
            loc (Location): starting location of the entity

        Returns:
            List[Location]: path from the starting entity to the closest target within sight radius
        """
        rows, cols = grid.grid.shape
        queue = deque([loc.coords])
        visited = [[False] * cols for _ in range(rows)]
        visited[loc.row][loc.col] = True
        parent = {loc.coords: None}

        target_cell = None

        while queue:
            curr_row, curr_col = queue.popleft()

            if (
                grid.grid[curr_row, curr_col].type == target
                and (curr_row, curr_col) != loc.coords
            ):
                target_cell = (curr_row, curr_col)
                break

            for dr, dc in self.cfg.entities.moves:
                nr, nc = curr_row + dr, curr_col + dc
                if (
                    grid.is_valid_move(Location(nr, nc), visited=visited)
                    and grid.check_herbivores_repro(self, grid.grid[nr, nc])
                    and grid.is_in_radius(loc, Location(nr, nc), self._radius)
                ):
                    visited[nr][nc] = True
                    parent[(nr, nc)] = (curr_row, curr_col)
                    queue.append((nr, nc))

        if target_cell is None:
            return []

        path = []
        curr = target_cell
        while curr is not None:
            path.append(Location(curr[0], curr[1]))
            curr = parent[curr]
        path.reverse()
        return path

    def get_random_valid_move(self, grid) -> Location:
        """
        Calculates a random valid move

        Args:
            grid: Grid object

        Returns:
            a valid move, if no valid moves available returns the entity's current location
        """
        valid_moves = grid.get_valid_moves(self.loc)
        if not valid_moves:
            return self.loc
        logging.info(f"Random valid move {[m.coords for m in valid_moves]} for entity at location {self.loc.coords}")
        return random.choice(valid_moves)

    def get_next_move(self, grid, predator: bool = False) -> Location:
        """
        Calculates the next move for the entity

        Args:
            grid: Grid object
            predator (bool, optional): whether searching a move to a predator or not. Affects the searched target. Defaults to False.

        Returns:
            the next move
        """
        if self._radius <= 0:
            return self.get_random_valid_move(grid)
        target = EntityType.HERBIVORE if predator else EntityType.PLANT
        path = self.bfs(grid, target, self.loc)
        if len(path) <= 1:
            logging.info(f"No {EntityType.HERBIVORE if predator else EntityType.PLANT} in sight radius {self._radius} for entity at location: {self.loc.coords}")
            return self.get_random_valid_move(grid)
        return path[1]

    @abstractmethod
    def move(self, grid) -> None:
        """
        Abstract method to move the entity
        Args:
            grid: Grid object
        """
        pass
