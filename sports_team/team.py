# sports_team/team.py
from typing import List, Optional
from sports_team.player import Player


class Team:
    """Класс, описывающий спортивную команду."""

    def __init__(self, name: str):
        self.name = name
        self.players: List[Player] = []

    # --- методы управления игроками ---
    def add_player(self, player: Player):
        """Добавить игрока в команду."""
        if any(p.number == player.number for p in self.players):
            raise ValueError(f"Игрок с номером {player.number} уже есть в команде.")
        self.players.append(player)

    def remove_player(self, number: int):
        """Удалить игрока по номеру."""
        for p in self.players:
            if p.number == number:
                self.players.remove(p)
                return
        raise ValueError(f"Игрок с номером {number} не найден в команде.")

    # --- статистика команды ---
    def total_goals(self) -> int:
        """Общее количество голов команды."""
        return sum(p.goals for p in self.players)

    def total_assists(self) -> int:
        """Общее количество передач команды."""
        return sum(p.assists for p in self.players)

    def total_games(self) -> int:
        """Среднее количество сыгранных матчей (по всем игрокам)."""
        if not self.players:
            return 0
        return round(sum(p.games for p in self.players) / len(self.players), 2)

    def top_scorer(self) -> Optional[Player]:
        """Возвращает лучшего бомбардира."""
        if not self.players:
            return None
        return max(self.players, key=lambda p: p.goals)

    # --- служебные методы ---
    def to_dict(self):
        """Представить команду в виде словаря (для отчётов)."""
        return {
            "Название команды": self.name,
            "Количество игроков": len(self.players),
            "Общие голы": self.total_goals(),
            "Общие передачи": self.total_assists(),
            "Средние матчи на игрока": self.total_games(),
        }

    # --- dunder-методы ---
    def __len__(self):
        """Позволяет использовать len(team)."""
        return len(self.players)

    def __iter__(self):
        """Позволяет итерироваться по игрокам: for p in team."""
        return iter(self.players)

    def __getitem__(self, index: int):
        """Позволяет обращаться к игроку как к элементу списка."""
        return self.players[index]

    def __str__(self):
        return f"Команда {self.name} ({len(self.players)} игроков)"

    def __repr__(self):
        return f"Team(name='{self.name}', players={len(self.players)})"
