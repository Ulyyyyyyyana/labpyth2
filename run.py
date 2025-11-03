import sys
import os
import pickle
from sports_team.player import Forward, Defender, Goalkeeper
from sports_team.team import Team
from sports_team.match import Match
from sports_team.report import save_team_report_docx
from sports_team.db import init_db, save_team, save_match

SAVE_FILE = "teams.pkl"

teams = {}

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
                else:
                    teams = {}
        except Exception:
            teams = {}
    else:
        teams = {}


# === Работа с командами ===
def create_team():
    name = input("Введите название команды: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return

    key = name.lower()
    if key in teams:
        print(f"Команда '{name}' уже существует.")
        return

    teams[key] = Team(name)
    save_state()
    print(f"Команда '{name}' успешно создана.")


def add_player_to_team():
    if not teams:
        print("Нет созданных команд. Сначала создайте команду.")
        return

    name = input("Введите название команды: ").strip()
    if not name:
        print("Название команды не может быть пустым.")
        return

    team = teams.get(name.lower())
    if team is None:
        print(f"Команда '{name}' не найдена.")
        return

    player_name = input("Имя игрока: ").strip()
    if not player_name:
        print("Имя не может быть пустым.")
        return

    try:
        number = int(input("Номер игрока: ").strip())
        if number <= 0:
            print("Номер должен быть положительным числом.")
            return
    except ValueError:
        print("Неверный номер. Введите целое число.")
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
        player = Forward(player_name, number, "Нападающий")
    elif "защит" in position:
        player = Defender(player_name, number, "Защитник")
    elif "врат" in position:
        player = Goalkeeper(player_name, number, "Вратарь")
    else:
        print("Неизвестная позиция. Используйте: Нападающий, Защитник или Вратарь.")
        return

    team.add_player(player)
    save_state()
    print(f"Игрок {player_name} ({player.role()}) добавлен в команду {team.name}.")


def show_team_info():
    if not teams:
        print("Нет созданных команд.")
        return

    name = input("Введите название команды: ").strip()
    if not name:
        print("Название команды не может быть пустым.")
        return

    team = teams.get(name.lower())
    if team is None:
        print(f"Команда '{name}' не найдена.")
        return

    print(f"\n=== {team.name} ===")
    print(f"Количество игроков: {len(team)}")
    print(f"Общие голы: {team.total_goals()}")
    print(f"Общие передачи: {team.total_assists()}")
    avg_games = team.total_games() / len(team) if len(team) > 0 else 0
    print(f"Средние матчи на игрока: {avg_games:.2f}\n")

    if team.players:
        print("Состав команды:")
        for p in team.players:
            print(f" - {p.name} (№{p.number}, {p.role()}) — "
                  f"Голы: {p.goals}, Передачи: {p.assists}, Матчи: {p.games}")
    else:
        print("В команде нет игроков.")
    print()


def list_all_teams():
    if not teams:
        print("Нет команд.")
        return

    print("\n=== Список всех команд ===")
    for team in teams.values():
        print(f" - {team.name} (игроков: {len(team)})")
    print()


# === Матчи ===
def record_match():
    if len(teams) < 2:
        print("Для проведения матча нужно как минимум две команды.")
        return

    team_a_name = input("Введите первую команду: ").strip()
    team_b_name = input("Введите вторую команду: ").strip()

    team_a = teams.get(team_a_name.lower())
    team_b = teams.get(team_b_name.lower())

    if team_a is None or team_b is None:
        print("Одна из команд не найдена.")
        return

    if team_a == team_b:
        print("Нельзя провести матч между одной и той же командой.")
        return

    match = Match(team_a, team_b)
    print(f"\nМатч {match.team_a.name} vs {match.team_b.name} начался!")

    while True:
        goal = input("\nВведите имя игрока, забившего гол (или 'stop' для завершения): ").strip()
        if goal.lower() == "stop":
            break

        try:
            minute = int(input("Минута гола: ").strip())
            if not 1 <= minute <= 120:
                print("Минута должна быть от 1 до 120.")
                continue
        except ValueError:
            print("Введите число для минуты.")
            continue

        found_player = None
        for team in [match.team_a, match.team_b]:
            for p in team.players:
                if p.name.lower() == goal.lower():
                    found_player = p
                    break
            if found_player:
                break

        if not found_player:
            print("Игрок не найден в обеих командах.")
            continue

        try:
            match.record_goal(found_player, minute)
            print(f"Гол! {found_player.name} на {minute}-й минуте.")
        except Exception as e:
            print("Ошибка записи гола:", e)

    print("\n" + match.summary())
    winner = match.winner()
    if winner:
        print(f"Победитель: {winner.name}")
    else:
        print("Ничья")
    match.finalize_match()
    if not hasattr(match.team_a, "matches"):
        match.team_a.matches = []
    if not hasattr(match.team_b, "matches"):
        match.team_b.matches = []
    match.team_a.matches.append(match)
    match.team_b.matches.append(match)
    
    save_match(match)
    
    save_team(match.team_a)
    save_team(match.team_b)
    save_state()

# === Отчёты и база данных ===
def save_report():
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
        print(f"Отчёт сохранён: {filename}")
    except Exception as e:
        print("Ошибка при сохранении отчёта:", e)


def save_all_to_db():
    if not teams:
        print("Нет данных для сохранения.")
        return

    try:
        init_db()
        for team in teams.values():
            save_team(team)
        print("Все данные успешно сохранены в базу данных.")
    except Exception as e:
        print("Ошибка при сохранении в базу данных:", e)


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
