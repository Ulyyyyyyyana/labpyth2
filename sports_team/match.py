# sports_team/match.py
from datetime import datetime
from sports_team.team import Team
from sports_team.player import Player


class Match:
    """Класс, описывающий футбольный матч между двумя командами."""

    def __init__(self, team_a: Team, team_b: Team, date: datetime = None):
        if team_a == team_b:
            raise ValueError("Команды не могут быть одинаковыми.")
        self.team_a = team_a
        self.team_b = team_b
        self.date = date or datetime.now()
        self.events = []  # список словарей вида {'minute': 34, 'player': obj, 'team': 'A'}

    # --- методы событий ---
    def record_goal(self, player: Player, minute: int):
        """Регистрирует гол игрока и добавляет событие."""
        if minute < 0 or minute > 120:
            raise ValueError("Минута должна быть в диапазоне 0–120.")
        # добавляем гол игроку
        player.add_match_stats(goals=1)
        # определяем, к какой команде принадлежит
        team_name = "A" if player in self.team_a.players else "B"
        self.events.append({
            "minute": minute,
            "player": player,
            "team": team_name
        })

    def score(self):
        """Возвращает счёт в виде кортежа (голы команды A, голы команды B)."""
        goals_a = sum(1 for e in self.events if e["team"] == "A")
        goals_b = sum(1 for e in self.events if e["team"] == "B")
        return goals_a, goals_b

    def winner(self):
        """Определяет победителя матча."""
        goals_a, goals_b = self.score()
        if goals_a > goals_b:
            return self.team_a
        elif goals_b > goals_a:
            return self.team_b
        else:
            return None  # ничья

    def summary(self):
        """Краткая текстовая сводка."""
        goals_a, goals_b = self.score()
        return f"{self.team_a.name} {goals_a}:{goals_b} {self.team_b.name}"

    # --- dunder-методы ---
    def __str__(self):
        return f"Матч {self.team_a.name} vs {self.team_b.name} ({self.date.strftime('%d.%m.%Y')})"

    def __repr__(self):
        return f"Match({self.team_a.name!r}, {self.team_b.name!r}, {len(self.events)} событий)"
