import sqlite3
import os

DB_NAME = "sports.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Создание всех таблиц, если их нет"""
    conn = get_connection()
    cur = conn.cursor()

    # Таблица команд
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    """)

    # Таблица игроков
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number INTEGER,
            position TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        );
    """)

    # ✅ Добавляем таблицу матчей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT NOT NULL,
            team_b TEXT NOT NULL,
            score_a INTEGER DEFAULT 0,
            score_b INTEGER DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def save_team(team):
    """Сохраняет команду и её игроков"""
    conn = get_connection()
    cur = conn.cursor()

    # вставляем или обновляем команду
    cur.execute("""
        INSERT OR IGNORE INTO teams (name)
        VALUES (?);
    """, (team.name,))
    conn.commit()

    # получаем id команды
    cur.execute("SELECT id FROM teams WHERE name = ?;", (team.name,))
    team_id = cur.fetchone()[0]

    # сохраняем игроков
    for p in team.players:
        cur.execute("""
            INSERT OR REPLACE INTO players (name, number, position, goals, assists, games, team_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (p.name, p.number, p.position, p.goals, p.assists, p.games, team_id))

    conn.commit()
    conn.close()


def save_match(match):
    """Сохраняет результат матча"""
    conn = get_connection()
    cur = conn.cursor()

    # убедимся, что таблица существует
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT NOT NULL,
            team_b TEXT NOT NULL,
            score_a INTEGER DEFAULT 0,
            score_b INTEGER DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # считаем голы через match.events
    goals_a = sum(1 for e in match.events if e["team"] == "A")
    goals_b = sum(1 for e in match.events if e["team"] == "B")

    cur.execute("""
        INSERT INTO matches (team_a, team_b, score_a, score_b, date)
        VALUES (?, ?, ?, ?, ?);
    """, (match.team_a.name, match.team_b.name, goals_a, goals_b, match.date))

    conn.commit()
    conn.close()