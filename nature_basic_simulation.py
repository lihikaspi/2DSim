from omegaconf import OmegaConf

from entities.entity_type_enum import EntityType
from grid import Grid


class NatureGOLSimulation:
    """
    Nature Game Of Life Simulation Handler
    """

    def __init__(self, cfg, board_idx: int) -> None:
        """
        Initializes the simulation

        Args:
            cfg: OmegaConf config object
            board_idx (int):  board index in the config file
        """
        self.cfg = cfg
        self.initial_grid = cfg.boards[board_idx][1]
        self.grid = Grid(self.initial_grid, cfg)
        self.states = []
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps
        self.pretty_print(initial=True)

    def step(self) -> None:
        """
        Performs one step of the simulation and prints the current board state to the console

        move order: PREDATOR -> HERBIVORE -> PLANT -> SPAWN NEW PLANTS
        """
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR)
        self.grid.step_per_type(EntityType.HERBIVORE)
        self.grid.step_per_type(EntityType.PLANT)
        self.grid.spawn_plants()
        self.pretty_print()

    def run_simulation(self) -> None:
        """
        Runs the simulation step by step
        """
        while self.curr_step < self.total_steps:
            self.step()

    def pretty_print(self, initial: bool = False) -> None:
        """
        Print the current board state to the console
        Args:
            initial (bool, optional): Whether the function os printing the initial state. Defaults to False.
        """
        simple_grid = self.grid.simplify()
        self.states.append(simple_grid)
        header = (
            "board at initial state" if initial else f"board at step {self.curr_step}"
        )
        print(header)
        for row in simple_grid:
            print(" ".join(row))


def main():
    print("********* START GAME *********")
    cfg = OmegaConf.load("config.yaml")
    print("choose initial grid:")
    seed = int(input().strip())
    print(f"board chosen: {cfg.boards[seed][0]}")
    sim = NatureGOLSimulation(cfg, seed)
    sim.run_simulation()
    print("********* END GAME *********")


if __name__ == "__main__":
    main()
