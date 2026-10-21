from grid import Grid, EntityType
from omegaconf import OmegaConf


class NatureGOLSimulation:
    def __init__(self, cfg, initial_grid) -> None:
        self.cfg = cfg
        self.initial_grid = initial_grid
        self.grid = Grid(cfg)
        self.states = []
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps
        # self.pretty_prinrint(initial=True)

    def step(self) -> None:
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR)
        self.grid.step_per_type(EntityType.HERBIVORE)
        self.grid.step_per_type(EntityType.PLANT)
        self.grid.spawn_plants()
        # self.pretty_print()

    def run_simulation(self) -> None:
        while self.curr_step < self.total_steps:
            self.step()

    def pretty_print(self, initial: bool = False):
        # TODO
        simple_grid = self.grid.simplify()
        self.states.append(simple_grid)
        pass

def main():
    cfg = OmegaConf.load("config.yaml")
    print(f"choose initial grid:")
    seed = int(input().strip())
    print(f"board chosen: {cfg.boards[seed][0]}")
    sim = NatureGOLSimulation(cfg, cfg.boards[seed][1])
    sim.run_simulation()

if __name__ == "__main__":
    main()


