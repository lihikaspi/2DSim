import json
import random
from pathlib import Path
from typing import Dict, cast
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
from omegaconf import OmegaConf

from config import Config
from entities.entity_type_enum import EntityType
from grid import Grid


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

def plot_live_organisms(df: pd.DataFrame, grid_name: str, save_dir: str) -> None:
    df.plot(style=["-o", "-s", "-D"], figsize=(10, 6))
    plt.legend(loc="upper right")
    plt.title(f"live organisms over time in {grid_name}")
    plt.xticks(range(0, df.shape[0]))
    plt.xlabel("step")
    plt.ylabel("live organisms")
    plt.tight_layout()
    plt.savefig(f"{save_dir}live_organisms_{grid_name}")
    plt.show()

def plot_herbivore_repro(df: pd.DataFrame, grid_name: str, save_dir: str) -> None:
    df.plot(style="-o", figsize=(10, 6))
    plt.title(f"Herbivore reproductions over time in {grid_name} (until death of all Herbivores)")
    plt.xticks(range(0, df.shape[0]))
    plt.yticks(range(0, int(df.max())+1))
    plt.xlabel("step")
    plt.ylabel("reproductions")
    plt.tight_layout()
    plt.savefig(f"{save_dir}herbivore_repro_{grid_name}")
    plt.show()

def plot_timeline(df: pd.DataFrame, grid_name: str, save_dir: str) -> None:
    cons_events = df.index[(df["animal_consumption_stats"] > 0) & (df["animal_consumption_stats"].notna())]
    repro_events = df.index[(df["repro_stats"] > 0) & (df["repro_stats"].notna())]

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.axhline(0, color="black", linewidth=1.5, zorder=1)
    ax.scatter(df.index, np.zeros(len(df)), color="gray", s=25, zorder=2)
    y_cons = 1.0
    ax.scatter(
        cons_events,
        [y_cons] * len(cons_events),
        marker="D",
        color="#e65100",
        s=90,
        label="Animal Consumption",
        zorder=3,
    )
    ax.vlines(
        cons_events,
        ymin=0,
        ymax=y_cons,
        colors="#e65100",
        linestyles="dashed",
        alpha=0.6,
    )
    y_repro = 2.0
    ax.scatter(
        repro_events,
        [y_repro] * len(repro_events),
        marker="^",
        color="#1565c0",
        s=110,
        label="Reproduction",
        zorder=3,
    )
    ax.vlines(
        repro_events,
        ymin=0,
        ymax=y_repro,
        colors="#1565c0",
        linestyles="dashed",
        alpha=0.6,
    )

    ax.set_xticks(df.index)
    ax.set_xlabel("Step Index", fontsize=11)
    ax.set_xlim(-0.8, len(df) - 0.2)
    ax.set_ylim(-0.4, 2.8)

    ax.set_yticks([])
    for spine in ["top", "left", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))

    ax.legend(loc="upper right", frameon=True)
    plt.title(f"Event Timeline in {grid_name}", pad=15, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{save_dir}events_timeline{grid_name}")
    plt.show()


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
