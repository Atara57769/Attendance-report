from abc import ABC, abstractmethod
from typing import Any

class Subject:
    pass # forward declaration

class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """
    @abstractmethod
    def update(self, subject: "Subject", event_name: str, **kwargs: Any) -> None:
        pass

class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, event_name: str, **kwargs: Any) -> None:
        for observer in self._observers:
            observer.update(self, event_name, **kwargs)
