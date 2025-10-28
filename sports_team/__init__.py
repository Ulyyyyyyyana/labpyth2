# sports_team/__init__.py

"""
Пакет sports_team — MVP-приложение для управления спортивной командой.
Содержит классы:
- Player — игрок
- Team — команда
- Match — матч
- db — работа с базой данных
- report — генерация отчётов (.docx)
"""

from sports_team.player import Player
from sports_team.team import Team
from sports_team.match import Match

__all__ = ["Player", "Team", "Match"]
