from abc import ABC, abstractmethod
from config import ScriptConfig


class IConfigurable(ABC):
    @abstractmethod
    def configure(self, config: ScriptConfig) -> None:
        ...
