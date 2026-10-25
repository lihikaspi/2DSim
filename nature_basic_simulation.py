import random
from pathlib import Path
from typing import cast, Dict
import logging
logger = logging.getLogger(__name__)

from omegaconf import OmegaConf

from entities.entity_type_enum import EntityType
from grid import Grid
from config import Config


class NatureGOLSimulation:
    """
    Nature Game Of Life Simulation Handler
    """

    def __init__(self, cfg: Config, board_idx: int) -> None:
        """
        Initializes the simulation

        Args:
            cfg (Config): OmegaConf config object
            board_idx (int):  board index in the config file
        """
        self.cfg = cfg
        self.initial_grid = cfg.boards[board_idx][1]
        self.grid = Grid(self.initial_grid, cfg)
        self.states = []
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps
        self.pretty_print(initial=True)
        logging.info(f"Initialized simulation")

    def step(self) -> None:
        """
        Performs one step of the simulation and prints the current board state to the console

        move order: PREDATOR -> HERBIVORE -> PLANT -> SPAWN NEW PLANTS
        """
        logging.info(f"Starting step: {self.curr_step}/{self.total_steps}...")
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR)
        self.grid.step_per_type(EntityType.HERBIVORE)
        self.grid.step_per_type(EntityType.PLANT)
        self.grid.spawn_plants()
        self.pretty_print()
        logging.info(f"Finished step: {self.curr_step}/{self.total_steps}")

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

    def get_stats(self) -> Dict[str, int]:
        return self.grid.get_entity_stats()


def load_config(yaml_path: str = "config.yaml") -> Config:
    schema = OmegaConf.structured(Config)
    yaml_conf = OmegaConf.load(yaml_path)
    merged_conf = OmegaConf.merge(schema, yaml_conf)
    return cast(Config, OmegaConf.to_object(merged_conf))


def main():
    logging.basicConfig(filename='NatureGOL.log', level=logging.INFO)

    cfg = load_config("./config.yaml")
    logging.info("Config file loaded")
    random.seed(cfg.sim.seed)

    print("********* START GAME *********")
    logging.info("Starting game...")
    print("choose initial grid:")
    initial_idx = int(input().strip())
    print(f"board chosen: {cfg.boards[initial_idx][0]}")
    logging.info(f"Initial grid: {cfg.boards[initial_idx][0]}")
    sim = NatureGOLSimulation(cfg, initial_idx)
    logging.info(f"Initial grid entity stats: {sim.get_stats()}")
    sim.run_simulation()
    print("********* END GAME *********")
    logging.info("Finished game")


if __name__ == "__main__":
    main()
