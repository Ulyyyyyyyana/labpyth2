# sports_team/team.py
from typing import List, Dict
from sports_team.player import Player, Forward, Defender, Goalkeeper


class Team:
    """Класс, описывающий спортивную команду."""

    def __init__(self, name: str):
        self.name = name
        self.players: List[Player] = []

    def add_player(self, player: Player):
        """Добавить игрока в команду."""
        if not isinstance(player, Player):
            raise TypeError("Можно добавить только объект класса Player или его подкласса")
        # Проверяем, нет ли игрока с таким же номером
        if any(p.number == player.number for p in self.players):
            raise ValueError(f"Игрок с номером {player.number} уже есть в команде")
        self.players.append(player)

    def create_player(self, name: str, number: int, position: str):
        """Создать игрока нужного типа по его позиции."""
        position_lower = position.lower()
        if "напад" in position_lower:
            player = Forward(name, number, position)
        elif "защит" in position_lower:
            player = Defender(name, number, position)
        elif "врат" in position_lower:
            player = Goalkeeper(name, number, position)
        else:
            raise ValueError("Неизвестная позиция игрока")
        self.add_player(player)
        return player

    def total_goals(self) -> int:
        return sum(p.goals for p in self.players)

    def to_dict(self) -> Dict[str, str]:
        """Преобразовать команду в словарь для отчёта."""
        return {
            "Название команды": self.name,
            "Количество игроков": len(self.players),
            "Общее количество голов": self.total_goals(),
        }
    def total_assists(self) -> int:
        """Общее количество передач у всех игроков."""
        return sum(p.assists for p in self.players)
    def top_scorer(self):
        """Возвращает игрока с наибольшим количеством голов."""
        if not self.players:
            return None
        return max(self.players, key=lambda p: p.goals)
    def total_games(self) -> int:
        """Общее количество матчей у всех игроков."""
        return sum(p.games for p in self.players)

    def __len__(self):
        return len(self.players)

    def __iter__(self):
        return iter(self.players)

    def __getitem__(self, index: int):
        return self.players[index]

    def __str__(self):
        return f"Команда {self.name} ({len(self.players)} игроков)"

    def __repr__(self):
        return f"Team(name='{self.name}', players={len(self.players)})"
    
    def match_stats(self):
        """Возвращает статистику по матчам: всего, побед, поражений, ничьих."""
        stats = {"Матчи": 0, "Победы": 0, "Поражения": 0, "Ничьи": 0}

        matches = getattr(self, "matches", [])
        for match in matches:
            stats["Матчи"] += 1
            goals_a, goals_b = match.score()

            # Определяем, сколько забила текущая команда и соперник
            if match.team_a == self:
                team_goals, opponent_goals = goals_a, goals_b
            elif match.team_b == self:
                team_goals, opponent_goals = goals_b, goals_a
            else:
                continue  # на случай, если матч не связан с этой командой

            # Обновляем статистику в одну строку
            if team_goals > opponent_goals:
                stats["Победы"] += 1
            elif team_goals < opponent_goals:
                stats["Поражения"] += 1
            else:
                stats["Ничьи"] += 1

        return stats
