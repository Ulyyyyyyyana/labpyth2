import pytest

from sports_team.player import Player
def test_create_player():
    """Проверяем корректное создание игрока."""
    p = Player("Иван Иванов", 10, "Нападающий")

    assert p.name == "Иван Иванов"
    assert p.number == 10
    assert p.position == "Нападающий"
    assert p.games == 0
    assert p.goals == 0
    assert p.assists == 0


def test_add_match_stats():
    """Добавление статистики за матч должно работать правильно."""
    p = Player("Иван", 9, "Форвард")
    p.add_match_stats(goals=2, assists=1)

    assert p.games == 1
    assert p.goals == 2
    assert p.assists == 1
    assert p.average_goals_per_game() == 2.0


def test_multiple_matches():
    """Средний показатель должен считаться корректно при нескольких матчах."""
    p = Player("Олег", 7, "Полузащитник")
    p.add_match_stats(goals=1, assists=0)
    p.add_match_stats(goals=3, assists=1)

    assert p.games == 2
    assert p.goals == 4
    assert p.average_goals_per_game() == 2.0


def test_negative_values_raise_error():
    """Отрицательные значения должны вызывать исключения."""
    p = Player("Петр", 5, "Защитник")

    with pytest.raises(ValueError):
        p.goals = -1
    with pytest.raises(ValueError):
        p.add_match_stats(goals=-2, assists=0)


def test_eq_and_lt_methods():
    """Проверка работы dunder-методов __eq__ и __lt__."""
    a = Player("Игрок A", 10, "Форвард")
    b = Player("Игрок B", 10, "Полузащитник")
    c = Player("Игрок C", 11, "Форвард")

    a.goals = 5
    c.goals = 3

    assert a == b           # одинаковые номера — равны
    assert c != a           # разные номера — не равны
    assert c < a            # меньше по количеству голов


def test_to_dict_returns_expected_structure():
    """Метод to_dict должен возвращать корректные ключи и значения."""
    p = Player("Дмитрий", 8, "Вратарь")
    p.add_match_stats(goals=0, assists=1)
    data = p.to_dict()

    expected_keys = {"Имя", "Номер", "Позиция", "Матчи", "Голы", "Передачи"}
    assert set(data.keys()) == expected_keys
    assert data["Имя"] == "Дмитрий"
    assert isinstance(data["Номер"], int)
