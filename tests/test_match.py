import pytest
from datetime import datetime
from sports_team.player import Player
from sports_team.team import Team
from sports_team.match import Match


def test_create_match_and_summary():
    team_a = Team("Барселона")
    team_b = Team("Реал")

    match = Match(team_a, team_b, datetime(2025, 5, 20))
    assert "Барселона" in str(match)
    assert "Реал" in str(match)
    assert isinstance(match.date, datetime)
    assert len(match.events) == 0


def test_record_goals_and_score():
    a = Team("Динамо")
    b = Team("ЦСКА")
    p1 = Player("Иван", 9, "Форвард")
    p2 = Player("Петр", 11, "Нападающий")
    a.add_player(p1)
    b.add_player(p2)

    match = Match(a, b)

    match.record_goal(p1, 10)
    match.record_goal(p1, 55)
    match.record_goal(p2, 70)

    assert match.score() == (2, 1)
    assert match.winner() == a
    assert "Динамо 2:1 ЦСКА" == match.summary()


def test_invalid_minute_raises_error():
    a = Team("Локо")
    b = Team("Спартак")
    p = Player("Олег", 8, "Полузащитник")
    a.add_player(p)
    match = Match(a, b)

    with pytest.raises(ValueError):
        match.record_goal(p, -5)

    with pytest.raises(ValueError):
        match.record_goal(p, 200)


def test_same_team_error():
    a = Team("Торпедо")
    with pytest.raises(ValueError):
        Match(a, a)
