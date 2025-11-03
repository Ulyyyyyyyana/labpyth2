# sports_team/player.py
from abc import ABC, abstractmethod
from typing import Dict
from sports_team.utils import validate_non_negative


class Player(ABC):
    """Абстрактный базовый класс, описывающий игрока спортивной команды."""

    def __init__(self, name: str, number: int, position: str):
        self.name = name
        self.number = number
        self.position = position
        self._games = 0
        self._goals = 0
        self._assists = 0

    # --- managed-атрибуты ---
    @property
    def games(self) -> int:
        return self._games

    @games.setter
    def games(self, value: int):
        validate_non_negative(value, "Количество игр")
        self._games = value

    @property
    def goals(self) -> int:
        return self._goals

    @goals.setter
    def goals(self, value: int):
        validate_non_negative(value, "Количество голов")
        self._goals = value

    @property
    def assists(self) -> int:
        return self._assists

    @assists.setter
    def assists(self, value: int):
        validate_non_negative(value, "Количество передач")
        self._assists = value

    # --- абстрактный метод ---
    @abstractmethod
    def role(self) -> str:
        """Абстрактный метод, возвращающий роль игрока (наследники обязаны реализовать)."""
        pass

    # --- методы работы со статистикой ---
    def add_match_stats(self, goals: int = 0, assists: int = 0):
        """Добавить статистику за один матч."""
        if goals < 0 or assists < 0:
            raise ValueError("Значения голов и передач должны быть неотрицательными")
        self._games += 1
        self._goals += goals
        self._assists += assists
  

    def to_dict(self) -> Dict[str, str]:
        """Преобразовать объект игрока в словарь."""
        return {
            "Имя": self.name,
            "Номер": self.number,
            "Позиция": self.position,
            "Матчи": self._games,
            "Голы": self._goals,
            "Передачи": self._assists,
        }

    # --- dunder-методы ---
    def __str__(self) -> str:
        return f"{self.name} (№{self.number}, {self.position})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', number={self.number}, position='{self.position}')"

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return self.number == other.number

    def __lt__(self, other):
        """Сравнение по количеству голов."""
        if not isinstance(other, Player):
            return NotImplemented
        return self._goals < other._goals

    def __hash__(self):
        """Позволяет использовать объекты Player в множествах и как ключи словарей."""
        return hash((self.name, self.number))


# --- конкретные подклассы игроков ---
class Forward(Player):
    def __init__(self, name, number, position="Нападающий"):
        super().__init__(name, number, position)

    def role(self) -> str:
        return "Нападающий"


class Defender(Player):
    def __init__(self, name, number, position="Защитник"):
        super().__init__(name, number, position)

    def role(self) -> str:
        return "Защитник"


class Goalkeeper(Player):
    def __init__(self, name, number, position="Вратарь"):
        super().__init__(name, number, position)

    def role(self) -> str:
        return "Вратарь"
