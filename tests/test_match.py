import os
import sys
import pytest
import time
from datetime import datetime

from sports_team.utils import timed, validate_non_negative
from sports_team.player import Forward, Defender, Goalkeeper, Player
from sports_team.team import Team
from sports_team.match import Match
from sports_team.report import save_team_report_docx
from sports_team.db import init_db, save_team, save_match, get_connection


# === Безопасная среда для всех тестов ===
@pytest.fixture(autouse=True)
def no_external_side_effects(monkeypatch, tmp_path):
    """Изолирует тесты: не даёт им портить реальные файлы и выводить лишнее."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "startfile", lambda *_, **__: None)
    monkeypatch.setattr("builtins.print", lambda *_, **__: None)
    yield


# === Тесты для utils ===
def test_validate_non_negative_ok_and_fail():
    # Корректное значение
    validate_non_negative(5, "Очки")
    # Ошибка при отрицательном
    with pytest.raises(ValueError):
        validate_non_negative(-3, "Очки")


def test_timed_decorator_measures_time(monkeypatch):
    called = {}

    @timed
    def slow_function(x):
        time.sleep(0.05)
        called["ok"] = True
        return x * 2

    start = time.time()
    result = slow_function(3)
    end = time.time()

    assert result == 6
    assert "ok" in called
    assert end - start >= 0.04  # чуть больше 0.05
    # Декоратор должен вернуть ту же функцию, не ломая поведение
    assert callable(slow_function)


# === Player subclasses ===
def test_create_forward_player():
    p = Forward("Иван Иванов", 10)
    assert p.name == "Иван Иванов"
    assert p.number == 10
    assert p.position == "Нападающий"
    assert p.role() == "Нападающий"
    assert isinstance(p, Player)


def test_defender_and_goalkeeper_roles():
    d = Defender("Петров", 5)
    g = Goalkeeper("Сидоров", 1)
    assert d.role() == "Защитник"
    assert g.role() == "Вратарь"



def test_negative_values_raise_error():
    p = Defender("Павел", 3)
    with pytest.raises(ValueError):
        p.goals = -1
    with pytest.raises(ValueError):
        p.add_match_stats(goals=-1)


def test_dunder_eq_lt_hash():
    a = Forward("Игрок A", 10)
    b = Defender("Игрок B", 10)
    c = Forward("Игрок C", 11)
    a.goals = 5
    c.goals = 2
    assert a == b
    assert c != a
    assert c < a
    assert isinstance(hash(a), int)


def test_to_dict_contains_expected_keys():
    p = Goalkeeper("Илья", 1)
    p.add_match_stats(goals=0, assists=1)
    data = p.to_dict()
    expected = {"Имя", "Номер", "Позиция", "Матчи", "Голы", "Передачи"}
    assert set(data.keys()) == expected


def test_cannot_instantiate_abstract_player():
    with pytest.raises(TypeError):
        Player("Test", 99, "Никто")


# === Team tests ===
def test_create_team_and_add_players():
    t = Team("Спартак")
    f = Forward("Иван", 9)
    d = Defender("Павел", 5)
    t.add_player(f)
    t.add_player(d)
    assert len(t) == 2


def test_add_duplicate_number_raises_error():
    t = Team("ЦСКА")
    f1 = Forward("Артём", 10)
    f2 = Defender("Сергей", 10)
    t.add_player(f1)
    with pytest.raises(ValueError):
        t.add_player(f2)


def test_total_goals_assists_and_len_iter():
    t = Team("Динамо")
    f = Forward("Иван", 9)
    g = Goalkeeper("Пётр", 1)
    f.add_match_stats(goals=3, assists=2)
    g.add_match_stats(goals=0, assists=1)
    t.add_player(f)
    t.add_player(g)
    assert t.total_goals() == 3
    assert t.total_assists() == 3
    assert len(t) == 2


def test_team_str_and_iter_getitem_repr():
    t = Team("Зенит")
    p = Forward("Малком", 10)
    t.add_player(p)
    assert "Зенит" in str(t)
    assert isinstance(t[0], Forward)


def test_to_dict_structure():
    t = Team("Локомотив")
    d = t.to_dict()
    expected_keys = {"Название команды", "Количество игроков", "Общее количество голов"}
    assert set(d.keys()) == expected_keys





# === Match tests ===
def test_match_record_and_winner():
    a = Team("Барселона")
    b = Team("Реал")
    p1 = Forward("Левандовский", 9)
    p2 = Forward("Бензема", 11)
    a.add_player(p1)
    b.add_player(p2)
    m = Match(a, b)
    m.record_goal(p1, 10)
    m.record_goal(p2, 20)
    m.record_goal(p1, 60)
    assert m.score() == (2, 1)
    assert m.winner() == a


def test_invalid_minute_and_same_team():
    a = Team("Ливерпуль")
    b = Team("МЮ")
    p = Forward("Салах", 11)
    a.add_player(p)
    with pytest.raises(ValueError):
        Match(a, a)
    m = Match(a, b)
    with pytest.raises(ValueError):
        m.record_goal(p, -10)
    with pytest.raises(ValueError):
        m.record_goal(p, 130)


def test_match_str_and_summary_without_goals():
    a = Team("Ростов")
    b = Team("Урал")
    m = Match(a, b)
    assert "Ростов" in str(m)
    assert ":" in m.summary()


# === Report & Database tests ===
def test_report_docx_creates_file(tmp_path):
    os.chdir(tmp_path)
    init_db()
    t = Team("Тест")
    t.add_player(Forward("Игрок", 9))
    filename = tmp_path / "report.docx"
    save_team_report_docx(t, filename)
    assert filename.exists()
    assert filename.stat().st_size > 0


def test_database_functions(tmp_path):
    os.chdir(tmp_path)
    init_db()
    t = Team("TestDB")
    t.add_player(Forward("DB Player", 7))
    save_team(t)
    m = Match(t, Team("Test2"))
    save_match(m)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM teams;")
    data = cur.fetchall()
    conn.close()
    assert data and "TestDB" in data[0][0]
def test_create_player_creates_correct_subclass():
    t = Team("Тестовая")
    f = t.create_player("Иван", 10, "нападающий")
    d = t.create_player("Павел", 5, "защитник")
    g = t.create_player("Олег", 1, "вратарь")

    assert isinstance(f, Forward)
    assert isinstance(d, Defender)
    assert isinstance(g, Goalkeeper)
    assert len(t) == 3

def test_create_player_invalid_position_raises():
    t = Team("Ошибочная")
    with pytest.raises(ValueError):
        t.create_player("Никита", 12, "тренер")

def test_team_iter_and_getitem():
    t = Team("Итерация")
    p1 = Forward("Игрок1", 7)
    p2 = Defender("Игрок2", 3)
    t.add_player(p1)
    t.add_player(p2)

    # __getitem__ и __iter__
    assert t[0] == p1
    assert [p.name for p in t] == ["Игрок1", "Игрок2"]

def test_team_repr_and_str_contain_name():
    t = Team("Краснодар")
    s = str(t)
    r = repr(t)
    assert "Краснодар" in s
    assert "Team" in r
    assert "игроков" in s.lower()

def test_match_stats_counts_correctly():
    """Проверяет расчёт побед, поражений и ничьих."""
    team1 = Team("Барса")
    team2 = Team("Реал")
    m1 = Match(team1, team2)
    m1.events = [
        {"player": Forward("Левандовский", 9), "minute": 10, "team": "A"},
        {"player": Forward("Бензема", 11), "minute": 20, "team": "B"},
        {"player": Forward("Левандовский", 9), "minute": 70, "team": "A"},
    ]

    team1.matches = [m1]
    team2.matches = [m1]

    stats = team1.match_stats()
    assert stats["Матчи"] == 1
    assert stats["Победы"] == 1
    assert stats["Поражения"] == 0
    assert stats["Ничьи"] == 0


def test_match_stats_draw_result():
    t1 = Team("Ювентус")
    t2 = Team("Милан")
    m = Match(t1, t2)
    m.events = [
        {"player": Forward("Игрок1", 7), "minute": 30, "team": t1},
        {"player": Forward("Игрок2", 9), "minute": 45, "team": t2},
    ]
    t1.matches = [m]
    stats = t1.match_stats()
    assert stats["Матчи"] == 1
    assert stats["Ничьи"] == 1