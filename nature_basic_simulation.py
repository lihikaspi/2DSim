import json
import random
from pathlib import Path
from typing import Dict, cast

import pandas as pd
from omegaconf import OmegaConf

from alerts.alert_type_enum import AlertType
from config import Config
from entities.entity_type_enum import EntityType
from grid import Grid

from alerts.alert_manager import (
    AlertManager,
    ExtinctionAlert,
    PlantOverpopulationAlert,
    PredatorAteHerbivoreAlert,
    SimulationEvent
)
from plots import plot_live_organisms, plot_herbivore_repro, plot_timeline


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
        self.alert_manager = AlertManager()
        self.alert_manager.attach(PredatorAteHerbivoreAlert())
        self.alert_manager.attach(ExtinctionAlert())
        self.alert_manager.attach(PlantOverpopulationAlert(threshold=cfg.entities.plant_population_threshold))

        self.initial_grid = cfg.boards[board_idx][1]
        self.grid = Grid(self.initial_grid, cfg, self.alert_manager)
        self.curr_step = 0
        self.total_steps = cfg.sim.total_steps

        self.boards = {}
        self.count_stats = {0: self.get_stats()}

        self.pretty_print(initial=True)

        self.alert_manager.notify(
            SimulationEvent(
                event_type=AlertType.STEP_END,
                data={
                    "step": self.curr_step,
                    "counts": self.get_stats(),
                    "total_cells": self.grid.num_cells,
                },
            )
        )

    def step(self) -> None:
        """
        Performs one step of the simulation and prints the current board state to the console

        move order: PREDATOR -> HERBIVORE -> PLANT -> SPAWN NEW PLANTS
        """
        self.curr_step += 1
        self.grid.step_per_type(EntityType.PREDATOR, self.curr_step)
        self.grid.step_per_type(EntityType.HERBIVORE, self.curr_step)
        self.grid.step_per_type(EntityType.PLANT, self.curr_step)
        self.grid.spawn_plants()
        self.pretty_print()

        self.alert_manager.notify(
            SimulationEvent(
                event_type=AlertType.STEP_END,
                data={
                    "step": self.curr_step,
                    "counts": self.get_stats(),
                    "total_cells": self.grid.num_cells,
                },
            )
        )

    def run_simulation(self) -> Dict:
        """
        Runs the simulation step by step
        """
        while self.curr_step < self.total_steps:
            self.step()
            self.count_stats[self.curr_step] = self.get_stats()
        return {
            "boards": self.boards,
            "live_stats": self.count_stats,
            "repro_stats": self.grid.repro_count,
            "animal_consumption_stats": self.grid.animal_consumption_count,
        }

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


def main():
    cfg = load_config("./config.yaml")
    random.seed(cfg.sim.seed)

    print("********* START GAME *********")
    print("choose initial grid:")
    initial_idx = int(input().strip())
    print(f"board chosen: {cfg.boards[initial_idx][0]}")
    sim = NatureGOLSimulation(cfg, initial_idx)
    stats = sim.run_simulation()

    stats_dir = Path(cfg.paths.sim_stats_dir)
    file_name = f"{cfg.boards[initial_idx][0]}.json"
    stats_path = stats_dir / file_name
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w") as f:
        json.dump(stats, f)
    print("********* END GAME *********")

    # TODO change df load logic - load only desired columns
    states_df = pd.DataFrame({col: pd.Series(steps) for col, steps in stats.items()})
    states_df.index = states_df.index.astype(int)
    states_df = states_df.sort_index()
    live_stats_df = pd.DataFrame(states_df["live_stats"].tolist(), index=states_df.index)

    print("simulation data df info:")
    states_df.info()
    print("simulation data stats:")
    print(states_df.describe())

    plot_live_organisms(live_stats_df[["Plant", "Herbivore", "Predator"]], cfg.boards[initial_idx][0], cfg.paths.sim_stats_dir)
    plot_herbivore_repro(states_df["repro_stats"].dropna(), cfg.boards[initial_idx][0], cfg.paths.sim_stats_dir)
    plot_timeline(states_df, cfg.boards[initial_idx][0], cfg.paths.sim_stats_dir)

if __name__ == "__main__":
    main()
