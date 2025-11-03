# sports_team/db.py
import sqlite3
import os
from datetime import datetime

DB_NAME = "sports.db"


def get_connection():
    """Возвращает подключение к базе данных."""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Создаёт все таблицы, если их нет."""
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

    # Таблица матчей
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


# === Сохранение данных ===
def save_team(team):
    """Сохраняет команду и её игроков."""
    conn = get_connection()
    cur = conn.cursor()

    # вставляем или обновляем команду
    cur.execute("""
        INSERT OR IGNORE INTO teams (name) VALUES (?);
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
    """Сохраняет результат матча в базу данных."""
    conn = get_connection()
    cur = conn.cursor()

    # Проверяем, что таблица существует
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT NOT NULL,
            team_b TEXT NOT NULL,
            score_a INTEGER DEFAULT 0,
            score_b INTEGER DEFAULT 0,
            date TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Считаем голы для обеих команд
    goals_a = sum(1 for e in match.events if e["team"] == "A")
    goals_b = sum(1 for e in match.events if e["team"] == "B")

    # Преобразуем дату в текст, чтобы SQLite точно сохранил
    date_str = match.date.strftime("%Y-%m-%d %H:%M:%S")

    # Записываем матч
    cur.execute("""
        INSERT INTO matches (team_a, team_b, score_a, score_b, date)
        VALUES (?, ?, ?, ?, ?);
    """, (match.team_a.name, match.team_b.name, goals_a, goals_b, date_str))

    conn.commit()
    conn.close()
    print(f"✅ Матч сохранён: {match.team_a.name} {goals_a}:{goals_b} {match.team_b.name}")



# === Загрузка данных ===
def load_team_matches(team_name):
    """Загружает все матчи команды из БД."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT team_a, team_b, score_a, score_b, date
        FROM matches
        WHERE team_a = ? OR team_b = ?
        ORDER BY date;
    """, (team_name, team_name))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_team_match_stats(team_name):
    """Возвращает статистику по матчам команды."""
    matches = load_team_matches(team_name)
    total = wins = losses = draws = 0

    for team_a, team_b, score_a, score_b, _ in matches:
        total += 1
        if team_name == team_a:
            if score_a > score_b:
                wins += 1
            elif score_a < score_b:
                losses += 1
            else:
                draws += 1
        elif team_name == team_b:
            if score_b > score_a:
                wins += 1
            elif score_b < score_a:
                losses += 1
            else:
                draws += 1

    return {
        "Матчи": total,
        "Победы": wins,
        "Поражения": losses,
        "Ничьи": draws
    }
