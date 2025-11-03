import sys
import os
import pickle
import subprocess
import platform

from sports_team.player import Forward, Defender, Goalkeeper
from sports_team.team import Team
from sports_team.match import Match
from sports_team.report import save_team_report_docx
from sports_team.db import init_db, save_team, save_match

SAVE_FILE = "teams.pkl"
teams = {}

# === Инициализация базы ===
init_db()


# === Сохранение и загрузка состояния ===
def save_state():
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(teams, f)
    except Exception as e:
        print("Ошибка при сохранении состояния:", e)


def load_state():
    global teams
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                loaded = pickle.load(f)
                if isinstance(loaded, dict):
                    teams.update(loaded)
        except Exception:
            teams = {}
    else:
        teams = {}


# === Работа с командами ===
def create_team():
    """Создание новой команды."""
    name = input("Введите название команды: ").strip()
    if not name:
        print("Название команды не может быть пустым.")
        return

    key = name.lower()
    if key in teams:
        print(f"Команда '{name}' уже существует.")
        return

    teams[key] = Team(name)
    save_state()
    print(f"Команда '{name}' успешно создана.")


def add_player_to_team():
    """Добавление игрока в команду."""
    if not teams:
        print("Нет созданных команд. Сначала создайте хотя бы одну команду.")
        return

    team_name = input("Введите название команды: ").strip()
    if not team_name:
        print("Название команды не может быть пустым.")
        return

    team = teams.get(team_name.lower())
    if team is None:
        print(f"Команда '{team_name}' не найдена.")
        return

    player_name = input("Имя игрока: ").strip()
    if not player_name:
        print("Имя игрока не может быть пустым.")
        return

    try:
        number = int(input("Номер игрока: ").strip())
        if number <= 0:
            print("Номер должен быть положительным числом.")
            return
    except ValueError:
        print("Введите корректный номер.")
        return

    position = input("Позиция (Нападающий / Защитник / Вратарь): ").strip().lower()
    if not position:
        print("Позиция не может быть пустой.")
        return

    # Проверяем дублирование
    for existing_player in team.players:
        if existing_player.number == number:
            print(f"Игрок с номером {number} уже существует в команде.")
            return

    # === Создаём игрока нужного подкласса ===
    if "напад" in position:
        player = Forward(player_name, number)
    elif "защит" in position:
        player = Defender(player_name, number)
    elif "врат" in position:
        player = Goalkeeper(player_name, number)
    else:
        print("Неизвестная позиция. Используйте: Нападающий, Защитник или Вратарь.")
        return

    team.add_player(player)
    save_state()
    print(f"✅ Игрок {player_name} ({player.role()}) добавлен в команду {team.name}.")


def show_team_info():
    """Вывод информации о команде."""
    if not teams:
        print("Нет созданных команд. Сначала создайте хотя бы одну команду.")
        return

    name = input("Введите название команды: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return

    team = teams.get(name.lower())
    if team is None:
        print(f"Команда '{name}' не найдена.")
        return

    print(f"\n=== {team.name} ===")
    print(f"Игроков: {len(team)}")
    print(f"Голы: {team.total_goals()} | Передачи: {team.total_assists()} | Матчей: {team.total_games()}")
    print(f"Лучший бомбардир: {team.top_scorer().name if team.top_scorer() else '—'}")

    if not team.players:
        print("В команде нет игроков.")
        return

    print("\nСостав:")
    for p in team.players:
        print(f" - {p.name} (№{p.number}, {p.role()}) — "
              f"Голы: {p.goals}, Передачи: {p.assists}, Матчи: {p.games}")
    print()


def list_all_teams():
    """Список всех команд."""
    if not teams:
        print("Нет команд.")
        return

    print("\n=== Список всех команд ===")
    for team in teams.values():
        print(f" - {team.name} (игроков: {len(team)})")
    print()


# === Матчи ===
def record_match():
    """Проведение матча между двумя командами."""
    if len(teams) < 2:
        print("Для проведения матча нужно как минимум две команды.")
        return

    team_a_name = input("Введите первую команду: ").strip()
    team_b_name = input("Введите вторую команду: ").strip()

    team_a = teams.get(team_a_name.lower())
    team_b = teams.get(team_b_name.lower())

    if not team_a or not team_b:
        print("Одна из команд не найдена.")
        return
    if team_a == team_b:
        print("Нельзя провести матч между одной и той же командой.")
        return

    match = Match(team_a, team_b)
    print(f"\nМатч {team_a.name} vs {team_b.name} начался!")

    while True:
        goal = input("\nВведите имя игрока, забившего гол (или 'стоп' для завершения): ").strip()
        if goal.lower() == "стоп":
            break

        try:
            minute = int(input("Минута гола: ").strip())
            if not 1 <= minute <= 120:
                print("Минута должна быть от 1 до 120.")
                continue
        except ValueError:
            print("Введите число для минуты.")
            continue

        # --- Поиск игрока ---
        found_player = None
        for team in [team_a, team_b]:
            for p in team.players:
                if p.name.lower() == goal.lower():
                    found_player = p
                    break
            if found_player:
                break

        if not found_player:
            print("Игрок не найден в обеих командах.")
            continue

        match.record_goal(found_player, minute)
        print(f"⚽ Гол! {found_player.name} ({found_player.role()}) на {minute}-й минуте!")

    print("\n" + match.summary())
    winner = match.winner()
    print(f"🏆 Победитель: {winner.name if winner else 'Ничья'}")

    match.finalize_match()
    match.team_a.matches = getattr(match.team_a, "matches", []) + [match]
    match.team_b.matches = getattr(match.team_b, "matches", []) + [match]

    save_match(match)
    save_team(match.team_a)
    save_team(match.team_b)
    save_state()


def save_report():
    """Создание .docx отчёта о команде."""
    if not teams:
        print("Нет созданных команд.")
        return

    name = input("Введите название команды для отчёта: ").strip()
    if not name:
        print("Название команды не может быть пустым.")
        return

    team = teams.get(name.lower())
    if team is None:
        print(f"Команда '{name}' не найдена.")
        return

    filename = f"report_{team.name.replace(' ', '_')}.docx"
    try:
        save_team_report_docx(team, filename)
        print(f"📄 Отчёт сохранён: {filename}")
    except Exception as e:
        print("Ошибка при сохранении отчёта:", e)


def save_all_to_db():
    """Сохранение всех данных в базу."""
    if not teams:
        print("Нет созданных команд.")
        return

    try:
        init_db()
        for team in teams.values():
            save_team(team)
        print("Все данные сохранены в базу данных.")
    except Exception as e:
        print("Ошибка при сохранении:", e)
 
def clear_state():
    """Полностью очищает сохранённые данные (файл teams.pkl и базу данных)."""
    global teams
    teams = {}
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        print("Файл состояния teams.pkl удалён.")
    if os.path.exists("sports.db"):
        os.remove("sports.db")
        print("База данных sports.db удалена.")
    init_db()
    print("Всё очищено, можно начать заново!")
 
def open_database():
    """Открывает базу данных sports.db в системном приложении."""
    db_path = os.path.abspath("sports.db")
    if not os.path.exists(db_path):
        print("База данных не найдена. Сначала сохраните данные (пункт 6).")
        return

    try:
        system = platform.system()
        os.startfile(db_path)
        print(f"Открыта база данных: {db_path}")

    except Exception as e:
        print(f"Ошибка при открытии базы данных: {e}")



# === Главное меню ===
def menu():
    while True:
        print("\n===== МЕНЮ =====")
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Показать информацию о команде")
        print("4. Провести матч")
        print("5. Сохранить отчёт (.docx)")
        print("6. Сохранить всё в базу данных")
        print("7. Показать все команды")
        print("8. Очистить все данные о командах")
        print("9. Открыть базу данных")
        print("0. Выход")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            create_team()
        elif choice == "2":
            add_player_to_team()
        elif choice == "3":
            show_team_info()
        elif choice == "4":
            record_match()
        elif choice == "5":
            save_report()
        elif choice == "6":
            save_all_to_db()
        elif choice == "7":
            list_all_teams()
        elif choice == "8":
            clear_state()
        elif choice == "9":
            open_database()
        elif choice == "0":
            save_state()
            print("Выход из программы.")
            sys.exit(0)
        else:
            print("Неверный выбор. Попробуйте снова.")


# === Точка входа ===
if __name__ == "__main__":
    print("Добро пожаловать в систему управления спортивной командой!")
    load_state()
    menu()
