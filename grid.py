import random
from typing import List, Tuple, Dict
import logging
logger = logging.getLogger(__name__)

import numpy as np

from config import Config
from entities.entity import EmptySpace, Entity, Plant, Tree
from entities.entity_type_enum import EntityType
from entities.herbivore import Herbivore
from entities.predator import Predator
from entities.location import Location


class Grid:
    """
    Grid object class. Handles all grid updates and checks
    """

    def __init__(
        self, initial_grid: List[List[int]], cfg: Config) -> None:
        """
        Initializes the grid using the given initial grid

        Args:
            initial_grid (List[List[int]]): Initial grid state
            cfg (Config): OmegaConf object
        """
        self.cfg = cfg
        self.num_rows = len(initial_grid)
        self.num_cols = len(initial_grid[0])
        self.num_cells = self.num_rows * self.num_cols
        self.grid = self.set_initial_grid(initial_grid)

        self.extinction = self.initialize_extinction_dict()
        logging.info(f"Initialized grid")

    @staticmethod
    def get_new_entity(val: int, loc: Location, cfg) -> Entity:
        """
        create a new entity of the given type in the given location. raises error if given type is not a valid.

        Args:
            val (int): new entity type
            loc (Location): location
            cfg: OmegaConf config object

        Returns:
            new entity
        """
        try:
            ent = EntityType(val)
        except ValueError:
            logging.error(f"Unknown entity type: {val}")
            raise ValueError(f"Unknown entity type value: {val}")

        e_cfg = cfg.entities
        builders = {
            EntityType.EMPTY: lambda: EmptySpace(loc, cfg),
            EntityType.TREE: lambda: Tree(loc, cfg),
            EntityType.PLANT: lambda: Plant(e_cfg.t_plant, loc, cfg),
            EntityType.HERBIVORE: lambda: Herbivore(
                e_cfg.t_herbivore, loc, e_cfg.r_herbivore_sight, e_cfg.t_cooldown, cfg),
            EntityType.PREDATOR: lambda: Predator(
                e_cfg.t_predator, loc, e_cfg.r_predator_sight, cfg),
        }

        builder = builders.get(ent)
        if not builder:
            logging.error(f"No constructor registered for: {ent}")
            raise ValueError(f"No constructor registered for: {ent}")
        return builder()

    def set_initial_grid(self, initial_grid: List[List[int]]) -> np.ndarray:
        """
        Initializes the starting grid with Entity type objects

        Args:
            initial_grid ([List[int]]): Initial grid state

        Returns:
            new grid with Entity objects as values

        """
        logging.info(f"Converting initial grid into a Grid object...")
        grid = np.ndarray(shape=(self.num_rows, self.num_cols), dtype=Entity)
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                grid[row, col] = self.get_new_entity(
                    initial_grid[row][col], Location(row, col), self.cfg
                )
        logging.info(f"Initial grid created in size: {grid.shape}")
        return grid

    def is_in_grid(self, loc: Location) -> bool:
        """
        Checks if the given position is within the grid

        Args:
            loc (Location): position to check

        Returns:
            true if position is within the grid, false otherwise

        """
        return not (loc.row >= self.num_rows or loc.row < 0 or loc.col >= self.num_cols or loc.col < 0)

    def update_grid(self, loc: Location, new_ent: Entity) -> None:
        """
        Updates the given position in the grid

        Args:
            loc (Location): new position
            new_ent (Entity): new entity
        """
        self.grid[loc.coords] = new_ent
        logging.info(f"grid at location {loc.coords} updated with entity {new_ent.type}")

    def get_radius_coords(self, loc: Location, radius: int) -> Tuple[int, int, int, int]:
        """
        Calculates the starting and ending indexes of the rows and columns from the main grid to include only cells
        within a given radius of the given location

        Args:
            loc (Location): new position
            radius (int): radius around the location

        Returns:
            starting and ending indexes of the rows and columns: r_start, r_end, c_start, c_end
        """
        r_start = max(0, loc.row - radius)
        r_end = min(self.num_rows, loc.row + radius + 1)
        c_start = max(0, loc.col - radius)
        c_end = min(self.num_cols, loc.col + radius + 1)
        return r_start, r_end, c_start, c_end

    def get_truncated_grid(self, loc: Location, radius: int) -> np.ndarray:
        """
        Truncates the main grid in a given radius around the given position

        Args:
            loc (Location): position to truncate around
            radius (int): radius around the location

        Returns:
            new truncated grid
        """
        r_start, r_end, c_start, c_end = self.get_radius_coords(loc, radius)
        return self.grid[r_start:r_end, c_start:c_end]

    def is_valid_move(self, loc: Location, visited: List[List[bool]] | None = None) -> bool:
        """
        Checks if the given location is free to move to.

        Checks the basic requirements (inside the grid, not stepping on Trees or Predators, and not a visited
        cell if inside the BFS search) and can be used for all types of entities

        Args:
            loc (Location): position to check
            visited (List[List[bool]], optional): visited cells in BFS search. Defaults to None.

        Returns:
            true if location is free to move to, false otherwise
        """
        return (
            self.is_in_grid(loc)
            and (not visited[loc.row][loc.col] if visited is not None else True)
            and self.grid[loc.coords].type not in [EntityType.TREE, EntityType.PREDATOR]
        )

    def is_in_radius(self, r_loc: Location, t_loc: Location, radius: int) -> bool:
        """
        Checks if the given position is within the radius of the given location

        Args:
            r_loc (Location): center position for the radius
            t_loc (Location): position to check
            radius (int): radius around the location

        Returns:
            true if location is within the radius of the given location, false otherwise
        """
        r_start, r_end, c_start, c_end = self.get_radius_coords(r_loc, radius)
        return r_start <= t_loc.row < r_end and c_start <= t_loc.col < c_end

    def check_herbivores_repro(self, ent1: Entity, ent2: Entity) -> bool:
        """
        checks if two given Herbivores can reproduce. If either given entity is not a Herbivore returns true always

        Args:
            ent1 (Entity): first entity
            ent2 (Entity): second entity

        Returns:
            returns true if both given Herbivores can reproduce, false otherwise
        """
        if ent1.type == EntityType.HERBIVORE and ent2.type == EntityType.HERBIVORE:
            return Herbivore.check_reproduction_possibility(ent1, ent2)
        return True

    def get_valid_moves(self, loc: Location) -> List[Location]:
        """
        Calculates all valid moves for a given location

        Args:
            loc (Location): location to calculate valid moves for

        Returns:
            List[Location]: list of locations of all valid moves

        """
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        moves = [
            n.loc
            for n in neighbors
            if n.loc.coords != loc.coords
            and self.is_valid_move(n.loc)
            and self.check_herbivores_repro(self.grid[loc.coords], n)
        ]
        logging.info(f"Found {len(moves)} valid moves for entity at location {loc.coords}: {moves}")
        return moves

    def get_empty_neighbors(self, loc: Location) -> List[Location]:
        """
        Calculates all empty neighbors for a given location

        Args:
            loc (Location): location to calculate empty neighbors for

        Returns:
            List[Location]: list of locations of all empty neighbors
        """
        neighbors = self.get_truncated_grid(loc, 1).flatten()
        empty_neighbors = [n.loc for n in neighbors if n.type == EntityType.EMPTY]
        logging.info(f"Found {len(empty_neighbors)} empty cells for entity at location {loc.coords}: {empty_neighbors}")
        return empty_neighbors

    def get_all_type_cells(self, t: EntityType, only_loc: bool = True) -> List[Location] | List[Entity]:
        """
        Calculates all type cells in the board for a given type

        Args:
            t (EntityType): type to calculate type cells for
            only_loc (bool, optional): return only locations of the entities. Defaults to True.

        Returns:
            list of all type cells, containing either locations or entities
        """
        all_cells = self.grid.flatten()
        type_cells = [c.loc if only_loc else c for c in all_cells if c.type == t and c.is_still_alive()]
        logging.info(f"Found {len(type_cells)} {t} cells")
        return type_cells

    def step_per_type(self, t: EntityType) -> None:
        """
        performs a step for all entities of a given type sequentially

        Args:
            t (EntityType): type to perform step for
        """
        if self.extinction[t]:
            return
        ents = self.get_all_type_cells(t, only_loc=False)

        moved = set()
        for e in ents:
            if id(e) in moved or self.grid[e.loc.coords] is not e:
                continue
            if t == EntityType.PLANT:
                e.increase_age()
                if not e.is_still_alive():
                    logging.warning(f"Plant at location {e.loc.coords} is already dead")
                    self.update_grid(e.loc, EmptySpace(e.loc, self.cfg))
            elif t == EntityType.HERBIVORE or t == EntityType.PREDATOR:
                moved.add(id(e))
                e.move(self)
            elif t == EntityType.EMPTY or t == EntityType.TREE:
                logging.error(f"Entity {t} is not moveable")
                raise ValueError(f"Entity type {t} is not moveable")

        for entity_type in (EntityType.PREDATOR, EntityType.HERBIVORE, EntityType.PLANT):
            self.check_extinction(entity_type)

    def spawn_plants(self):
        """
        Spawns plants at random empty locations. If no plants are still alive, not spawning
        """
        if self.extinction[EntityType.PLANT]:
            return
        all_plants = self.get_all_type_cells(EntityType.PLANT)
        new_count = 0
        empty_cells = self.get_all_type_cells(EntityType.EMPTY)
        new_locs = random.sample(empty_cells, random.randint(0, len(empty_cells)))
        for loc in new_locs:
            if Plant.spawn(self.cfg.entities.plant_spawn_threshold):
                new_count += 1
                self.update_grid(loc, Plant(self.cfg.entities.t_plant, loc, self.cfg))
        logging.info(f"Spawned {new_count} plants")
        if len(all_plants)+new_count > self.num_cells*0.9:
            logging.info(f"Plants have exceeded over 90% of the board")

    def simplify(self) -> List[List[str]]:
        """
        Simplifies the grid to be print ready. Uses the entity type to char mapping found in the config object

        Returns:
            List[List[int]]: simplified grid
        """
        mapping = self.cfg.pretty_print
        return [
            [
                getattr(mapping, self.grid[r, c].type.name.lower())
                for c in range(self.num_cols)
            ]
            for r in range(self.num_rows)
        ]

    def get_entity_stats(self) -> Dict[EntityType, int]:
        """
        returns counts of all entities of each type
        """
        plants = len(self.get_all_type_cells(EntityType.PLANT))
        herbivores = len(self.get_all_type_cells(EntityType.HERBIVORE))
        predators = len(self.get_all_type_cells(EntityType.PREDATOR))
        trees = len(self.get_all_type_cells(EntityType.TREE))
        emptys = len(self.get_all_type_cells(EntityType.EMPTY))
        return {EntityType.PLANT: plants, EntityType.HERBIVORE: herbivores,
                EntityType.PREDATOR: predators, EntityType.TREE: trees, EntityType.EMPTY: emptys}

    def initialize_extinction_dict(self) -> Dict[EntityType, bool]:
        """
        initializes extinction dict for all entities
        """
        stats = self.get_entity_stats()
        return {k: (v==0) for k, v in stats.items()}

    def check_extinction(self, t: EntityType) -> bool:
        """
        checks if an entity type has gone extinct and updates the extinction dict
        Args:
            t: entity type
        """
        if not self.extinction[t] and len(self.get_all_type_cells(t)) == 0:
            self.extinction[t] = True
            logging.info(f'No more {t} entities are alive on the board')
            return True
        return False