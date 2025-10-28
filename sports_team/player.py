# sports_team/player.py
from abc import ABC
from typing import Dict


class Player(ABC):
    """Класс, описывающий игрока спортивной команды."""

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
        if value < 0:
            raise ValueError("Количество игр не может быть отрицательным")
        self._games = value

    @property
    def goals(self) -> int:
        return self._goals

    @goals.setter
    def goals(self, value: int):
        if value < 0:
            raise ValueError("Количество голов не может быть отрицательным")
        self._goals = value

    @property
    def assists(self) -> int:
        return self._assists

    @assists.setter
    def assists(self, value: int):
        if value < 0:
            raise ValueError("Количество передач не может быть отрицательным")
        self._assists = value

    # --- методы работы со статистикой ---
    def add_match_stats(self, goals: int = 0, assists: int = 0):
        """Добавить статистику за один матч."""
        if goals < 0 or assists < 0:
            raise ValueError("Значения голов и передач должны быть неотрицательными")
        self._games += 1
        self._goals += goals
        self._assists += assists

    def average_goals_per_game(self) -> float:
        """Среднее количество голов за игру."""
        if self._games == 0:
            return 0.0
        return round(self._goals / self._games, 2)

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
        return f"Player(name='{self.name}', number={self.number}, position='{self.position}')"

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return self.number == other.number

    def __lt__(self, other):
        """Сравнение по количеству голов."""
        if not isinstance(other, Player):
            return NotImplemented
        return self._goals < other._goals
