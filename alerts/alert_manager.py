from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
import logging

from alerts.alert_type_enum import AlertType
from entities.entity_type_enum import EntityType

logger = logging.getLogger("SimulationAlerts")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class SimulationEvent:
    event_type: AlertType
    data: Dict[str, Any]


class AlertObserver(ABC):
    @abstractmethod
    def update(self, event: SimulationEvent) -> None:
        pass


class AlertManager:
    def __init__(self) -> None:
        self._observers: List[AlertObserver] = []

    def attach(self, observer: AlertObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: AlertObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: SimulationEvent) -> None:
        for observer in self._observers:
            observer.update(event)


class PredatorAteHerbivoreAlert(AlertObserver):
    def update(self, event: SimulationEvent) -> None:
        if event.event_type == AlertType.PREDATOR_ATE_HERBIVORE:
            predator = event.data.get("predator")
            location = event.data.get("location")
            logger.info(f"ALERT: Predator at {location} ate an Herbivore!")


class ExtinctionAlert(AlertObserver):
    def __init__(self) -> None:
        self._tracked_types = set()

    def update(self, event: SimulationEvent) -> None:
        if event.event_type != AlertType.STEP_END:
            return

        counts: Dict[str, int] = event.data.get("counts", {})
        step: int = event.data.get("step", 0)

        for entity_type, count in counts.items():
            if count > 0:
                self._tracked_types.add(entity_type)

        for entity_type in list(self._tracked_types):
            if counts.get(entity_type, 0) == 0:
                logger.warning(
                    f"ALERT: Extinction! No more entities of type '{entity_type}' are alive at step {step}."
                )
                self._tracked_types.remove(entity_type)


class PlantOverpopulationAlert(AlertObserver):
    def __init__(self, threshold: float = 0.90) -> None:
        self.threshold = threshold
        self._alert_active = False

    def update(self, event: SimulationEvent) -> None:
        if event.event_type != AlertType.STEP_END:
            return

        counts: Dict[str, int] = event.data.get("counts", {})
        total_cells: int = event.data.get("total_cells", 1)
        step: int = event.data.get("step", 0)

        plant_count = counts.get(str(EntityType.PLANT), 0)
        ratio = plant_count / total_cells

        if ratio > self.threshold:
            if not self._alert_active:
                logger.warning(
                    f"ALERT: Overpopulation! Plant count ({plant_count}/{total_cells}, {ratio * 100:.1f}%) "
                    f"exceeded {self.threshold * 100:.0f}% of the grid at step {step}."
                )
                self._alert_active = True
        else:
            self._alert_active = False