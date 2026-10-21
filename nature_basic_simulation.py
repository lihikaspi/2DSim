from grid import Grid
from omegaconf import OmegaConf
from entities.entity_type_enum import EntityType


class NatureGOLSimulation:
    def __init__(self, cfg, initial_grid) -> None:
        self.cfg = cfg
        self.initial_grid = initial_grid
        self.grid = Grid(initial_grid, cfg)
        self.states = []
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps
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
        simple_grid = self.grid.simplify()
        self.states.append(simple_grid)
        if initial:
            print(f"board at initial state")
        else:
            print(f"board at step {self.curr_step}")

def main():
    print("********* START GAME *********")
    cfg = OmegaConf.load("config.yaml")
    print(f"choose initial grid:")
    seed = int(input().strip())
    print(f"board chosen: {cfg.boards[seed][0]}")
    sim = NatureGOLSimulation(cfg, cfg.boards[seed][1])
    sim.run_simulation()
    print("********* START GAME *********")

if __name__ == "__main__":
    main()


