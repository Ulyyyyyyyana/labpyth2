import pytest
from sports_team.player import Player
from sports_team.team import Team


def test_create_team():
    team = Team("Динамо")
    assert team.name == "Динамо"
    assert len(team) == 0


def test_add_and_remove_player():
    team = Team("Зенит")
    p = Player("Артем", 10, "Форвард")
    team.add_player(p)

    assert len(team) == 1
    assert team.players[0].name == "Артем"

    # проверяем удаление
    team.remove_player(10)
    assert len(team) == 0


def test_add_duplicate_number_raises_error():
    team = Team("ЦСКА")
    p1 = Player("Игорь", 1, "Вратарь")
    p2 = Player("Вася", 1, "Защитник")
    team.add_player(p1)

    with pytest.raises(ValueError):
        team.add_player(p2)


def test_total_statistics_and_top_scorer():
    team = Team("Спартак")
    p1 = Player("Иван", 9, "Форвард")
    p2 = Player("Павел", 10, "Полузащитник")

    p1.add_match_stats(goals=3, assists=1)
    p2.add_match_stats(goals=1, assists=2)

    team.add_player(p1)
    team.add_player(p2)

    assert team.total_goals() == 4
    assert team.total_assists() == 3
    assert team.top_scorer().name == "Иван"


def test_to_dict_structure():
    team = Team("Локомотив")
    d = team.to_dict()

    expected_keys = {
        "Название команды",
        "Количество игроков",
        "Общие голы",
        "Общие передачи",
        "Средние матчи на игрока",
    }

    assert set(d.keys()) == expected_keys
    assert d["Название команды"] == "Локомотив"
