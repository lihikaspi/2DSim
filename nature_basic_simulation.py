from typing import List

from consts import EntityType
from grid import Grid
import yaml

class NatureGOLSimulation:
    def __init__(self, initial_grid: List[List[int]], total_steps: int) -> None:
        self.initial_grid = initial_grid
        self.grid = Grid(initial_grid)
        self.states = []
        self.curr_step = 0
        self.total_steps = total_steps
        self.pretty_print(initial=True)

    def step(self) -> None:
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR)
        self.grid.step_per_type(EntityType.HERBIVORE)
        self.grid.step_per_type(EntityType.PLANT)
        self.grid.spawn_plants()
        self.pretty_print()

    def run_simulation(self) -> None:
        while self.curr_step < self.total_steps:
            self.step()

    def pretty_print(self, initial: bool = False):
        # TODO
        simple_grid = self.grid.simplify()
        self.states.append(simple_grid)
        pass



