import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def plot_live_organisms(df: pd.DataFrame, grid_name: str, save_dir: str) -> None:
    """
    plots live organisms over time

    Args:
        df (pd.DataFrame): consists of entity-type columns and step idx as rows
        grid_name (str): grid template name
        save_dir (str): save directory
    """
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
    """
    plots herbivore reproduction over time

    Args:
        df (pd.DataFrame): consists of reproduction counters in each step (row)
        grid_name (str): grid template name
        save_dir (str): save directory
    """
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
    """
    plots events timeline over time

    Args:
        df (pd.DataFrame): consists of events counters in each step (row)
        grid_name (str): grid template name
        save_dir (str): save directory
    """
    cons_events = df.index[df["animal_consumption_stats"] > 0]
    repro_events = df.index[df["repro_stats"] > 0]

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
