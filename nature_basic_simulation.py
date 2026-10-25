import random
from pathlib import Path
from typing import cast, Dict
import logging
logger = logging.getLogger(__name__)
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

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
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps

        self.boards = {}
        self.count_stats = {0: self.get_stats()}

        self.pretty_print(initial=True)
        logging.info(f"Initialized simulation")

    def step(self) -> None:
        """
        Performs one step of the simulation and prints the current board state to the console

        move order: PREDATOR -> HERBIVORE -> PLANT -> SPAWN NEW PLANTS
        """
        logging.info(f"Starting step: {self.curr_step}/{self.total_steps}...")
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR, self.curr_step)
        self.grid.step_per_type(EntityType.HERBIVORE, self.curr_step)
        self.grid.step_per_type(EntityType.PLANT, self.curr_step)
        self.grid.spawn_plants()
        self.pretty_print()
        logging.info(f"Finished step: {self.curr_step}/{self.total_steps}")

    def run_simulation(self) -> Dict:
        """
        Runs the simulation step by step
        """
        while self.curr_step < self.total_steps:
            self.step()
            self.count_stats[self.curr_step] = self.get_stats()
        return {"boards": self.boards, "live_stats": self.count_stats, "repro_stats": self.grid.repro_count,
                     "animal_consumption_stats": self.grid.animal_consumption_count}

    def pretty_print(self, initial: bool = False) -> None:
        """
        Print the current board state to the console
        Args:
            initial (bool, optional): Whether the function os printing the initial state. Defaults to False.
        """
        simple_grid = self.grid.simplify()
        self.boards[self.curr_step] = simple_grid
        header = (
            "\nboard at initial state" if initial else f"board at step {self.curr_step}"
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

def plot_live_organisms(df: pd.DataFrame, grid_name: str, total_steps: int, save_dir: str) -> None:
    df.plot(style=["-o", "-s", "-D"],figsize=(10,6))
    plt.legend(loc="upper right")
    plt.title(f"live organisms over time in {grid_name}")
    plt.xticks(range(0,total_steps+1))
    plt.xlabel("step")
    plt.ylabel("live organisms")
    plt.savefig(f"{save_dir}live_organisms_{grid_name}")
    plt.show()

def plot_herbivore_repro(stats: Dict[int, int], grid_name: str, save_dir: str) -> None:
    plt.figure(figsize=(10,6))
    plt.plot(stats.values())
    plt.title("Herbivore reproductions over time (until death of all Herbivores)")
    plt.xticks(range(0, len(stats)))
    plt.yticks(range(min(stats.values())-1, max(stats.values())+2))
    plt.xlabel("step")
    plt.ylabel("reproductions")
    plt.savefig(f"{save_dir}herbivore_repro_{grid_name}")
    plt.show()


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
    stats = sim.run_simulation()

    stats_dir = Path(cfg.paths.sim_stats_dir)
    file_name = f"{cfg.boards[initial_idx][0]}.json"
    stats_path = stats_dir / file_name
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w") as f:
        json.dump(stats, f)
    logging.info(f"Simulation stats saved to {stats_path}")

    print("********* END GAME *********")
    logging.info("Finished game")

    df = pd.DataFrame([{'step': k, **v} for k, v in stats["live_stats"].items()])
    plot_live_organisms(df[["Plant", "Herbivore", "Predator"]], cfg.boards[initial_idx][0], cfg.sim.total_steps, cfg.paths.sim_stats_dir)
    plot_herbivore_repro(stats["repro_stats"], cfg.boards[initial_idx][0], cfg.paths.sim_stats_dir)


if __name__ == "__main__":
    main()
