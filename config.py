from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class EntitiesConfig:
    t_plant: int
    t_herbivore: int
    r_herbivore_sight: int
    t_cooldown: int
    t_predator: int
    r_predator_sight: int
    plant_spawn_threshold: float
    moves: List[List[int]]
    never_dead: int
    plant_population_threshold: float


@dataclass
class SimConfig:
    board_size: Tuple[int, int]
    total_steps: int
    seed: int


@dataclass
class PrettyPrintConfig:
    empty: str
    tree: str
    plant: str
    herbivore: str
    predator: str


@dataclass
class PathsConfig:
    nature_boards_dir: str
    sim_stats_dir: str


@dataclass
class Config:
    entities: EntitiesConfig
    sim: SimConfig
    pretty_print: PrettyPrintConfig
    paths: PathsConfig
    boards: Dict[int, List[Any]] = field(default_factory=dict)
