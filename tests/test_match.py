import os
import sys
import pytest
from datetime import datetime

# 👇 Импортируем всё нужное
from sports_team.player import Forward, Defender, Goalkeeper, Player
from sports_team.team import Team
from sports_team.match import Match
from sports_team.report import save_team_report_docx
from sports_team.db import init_db, save_team, save_match, get_connection


# === Автоматическая фикстура для безопасной среды ===
@pytest.fixture(autouse=True)
def no_external_side_effects(monkeypatch, tmp_path):
    """Изолирует тесты: отключает os.startfile и меняет рабочую директорию."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "startfile", lambda *_, **__: None)
    # также глушим print, если нужно, чтобы тесты были “тихие”
    monkeypatch.setattr("builtins.print", lambda *_, **__: None)
    yield


# === Player subclasses ===
def test_create_forward_player():
    p = Forward("Иван Иванов", 10)
    assert p.name == "Иван Иванов"
    assert p.number == 10
    assert p.position == "Нападающий"
    assert p.games == 0
    assert p.goals == 0
    assert p.assists == 0
    assert p.role() == "Нападающий"
    assert isinstance(p, Player)


def test_defender_and_goalkeeper_roles():
    d = Defender("Петров", 5)
    g = Goalkeeper("Сидоров", 1)
    assert d.role() == "Защитник"
    assert g.role() == "Вратарь"
    assert isinstance(d, Player)
    assert isinstance(g, Player)


def test_add_match_stats_and_average():
    p = Forward("Олег", 7)
    p.add_match_stats(goals=2, assists=1)
    p.add_match_stats(goals=1, assists=2)
    assert p.games == 2
    assert p.goals == 3
    assert p.assists == 3
    assert round(p.average_goals_per_game(), 2) == 1.5


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
    assert data["Имя"] == "Илья"


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
    assert isinstance(t.players[0], Forward)
    assert isinstance(t.players[1], Defender)


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
    assert list(iter(t))[0].name == "Иван"


def test_team_str_and_iter_getitem_repr():
    t = Team("Зенит")
    p = Forward("Малком", 10)
    t.add_player(p)
    assert "Зенит" in str(t)
    assert repr(t).startswith("Team(")
    assert isinstance(t[0], Forward)


def test_to_dict_structure():
    t = Team("Локомотив")
    d = t.to_dict()
    expected_keys = {"Название команды", "Количество игроков", "Общее количество голов"}
    assert set(d.keys()) == expected_keys
    assert d["Название команды"] == "Локомотив"


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
    assert "Барселона" in m.summary()
    assert "Match" in repr(m)


def test_match_str_and_summary_without_goals():
    a = Team("Ростов")
    b = Team("Урал")
    m = Match(a, b)
    s = str(m)
    r = repr(m)
    summ = m.summary()
    assert "Ростов" in s
    assert ":" in summ
    assert "Match" in r


def test_invalid_minute_and_same_team():
    a = Team("Ливерпуль")
    b = Team("МЮ")
    p = Forward("Салах", 11)
    a.add_player(p)
    m = Match(a, b)
    with pytest.raises(ValueError):
        m.record_goal(p, -10)
    with pytest.raises(ValueError):
        m.record_goal(p, 130)
    with pytest.raises(ValueError):
        Match(a, a)


# === Report and Database tests ===
def test_report_docx_creates_file(tmp_path):
    from sports_team.db import init_db  # локальный импорт, чтобы не мешать другим тестам

    # ✅ создаём временную БД в tmp_path
    os.chdir(tmp_path)
    init_db()

    t = Team("Тест")
    t.add_player(Forward("Игрок", 9))
    filename = tmp_path / "report.docx"
    save_team_report_docx(t, filename)
    assert os.path.exists(filename)
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
def test_team_stats_and_remove_player():
    t = Team("Зенит")
    p1 = Forward("Иван", 9)
    p2 = Defender("Павел", 4)
    p1.add_match_stats(goals=3, assists=1)
    p2.add_match_stats(goals=1, assists=2)
    t.add_player(p1)
    t.add_player(p2)

    assert t.total_assists() == 3
    assert t.total_games() == 2
    assert t.top_scorer() == p1

    t.remove_player(9)
    assert len(t) == 1
    assert str(t).startswith("Команда")
    assert isinstance(t[0], Defender)
def test_player_dunder_methods_and_properties():
    p = Forward("Илья", 7)
    p.games = 5
    p.goals = 4
    p.assists = 2
    assert "Илья" in str(p)
    assert "Forward" not in repr(p)  # просто проверка на строку
    assert p.games == 5 and p.goals == 4 and p.assists == 2
def test_match_finalize_and_errors():
    a = Team("Барса")
    b = Team("Реал")
    p = Forward("Иван", 9)
    a.add_player(p)
    m = Match(a, b)
    with pytest.raises(ValueError):
        m.record_goal(p, 130)
    with pytest.raises(ValueError):
        Match(a, a)
def test_get_team_match_stats_empty(tmp_path):
    os.chdir(tmp_path)
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO teams (name) VALUES ('Test')")
    conn.commit()
    conn.close()
    from sports_team.db import get_team_match_stats
    stats = get_team_match_stats("Test")
    assert isinstance(stats, dict)

