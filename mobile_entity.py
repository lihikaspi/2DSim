from grid import EntityType
from entities import Entity
from grid import Grid
from typing import Tuple, List
from collections import deque
from abc import abstractmethod
from predator import Predator
import random
import numpy as np

class MobileEntity(Entity):
    def __init__(self, t: EntityType, lifespan: int, loc: Tuple[int, int], radius: int, cfg):
        super().__init__(t, lifespan, loc, cfg)
        self._radius = radius

    def bfs(self, grid: Grid, target: EntityType, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Breadth-first search on the game grid looking for a cell with the wanted entity type
        Args:
            grid (Grid): truncated grid containing only valid cells inside the entity's radius
            target (EntityType): the goal entity type to find
            loc (Tuple[int, int]): current entity's location

        Returns:
            List[Tuple[int, int]]: path from the current entity to the desired entity type's location
        """
        rows, cols = grid.grid.shape
        queue = deque([loc])
        visited = [[False] * cols for _ in range(rows)]
        final_traversal_summary = []

        while queue:
            row, col = queue.popleft()
            visited[row][col] = True
            curr_cell = grid.grid[row,col]
            final_traversal_summary.append(curr_cell.loc)

            if curr_cell.get_type() == target:
                return final_traversal_summary

            moves = np.mgrid[-1:2, -1:2].transpose(1, 2, 0)

            for new_row, new_col in moves:
                if grid.is_valid_move(new_row, new_col, visited=visited) and grid.is_in_radius(loc, new_row, new_col, self._radius):
                    queue.append((new_row, new_col))
                    visited[new_row][new_col] = True
        print(f"INFO:{self.loc}: found path to {EntityType(target).name} -> {final_traversal_summary}")
        return final_traversal_summary

    def get_random_valid_move(self, grid: Grid) -> Tuple[int, int]:
        valid_moves = grid.get_valid_moves(self.loc)
        if len(valid_moves) == 0:
            print(f"INFO:{self.loc}: no valid moves, entity not moving!")
            return self.loc
        else:
            return random.choice(valid_moves)

    def get_next_move(self, grid: Grid) -> Tuple[int, int]:
        if self._radius <= 0:
            return self.get_random_valid_move(grid)
        target = EntityType.HERBIVORE if isinstance(self, Predator) else EntityType.PLANT
        path = self.bfs(grid, target, self.loc)
        if len(path) == 0:
            return self.get_random_valid_move(grid)
        return path.pop()

    @abstractmethod
    def move(self, grid: Grid):
        pass
