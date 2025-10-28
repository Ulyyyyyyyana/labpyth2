# run.py
import sys
import os
import pickle
from sports_team.player import Player
from sports_team.team import Team
from sports_team.match import Match
from sports_team.report import save_team_report_docx
from sports_team.db import init_db, save_team, save_match

SAVE_FILE = "teams.pkl"

# Хранилище команд в памяти (ключ — имя команды в нижнем регистре)
teams = {}


# --- Сохранение / загрузка состояния ---
def save_state():
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(teams, f)
        print("✅ Состояние сохранено")
    except Exception as e:
        print("Ошибка при сохранении состояния:", e)


def load_state():
    global teams
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                loaded = pickle.load(f)
                print(f"DEBUG: Загружены данные: {type(loaded)}")
                print(f"DEBUG: Ключи в загруженных данных: {list(loaded.keys()) if isinstance(loaded, dict) else 'N/A'}")
                
                # Защита на случай несовместимости структуры
                if isinstance(loaded, dict):
                    teams.update(loaded)
                    print("✅ Состояние загружено")
                else:
                    print("⚠️ Некорректный формат файла сохранения")
                    teams = {}
        except Exception as e:
            print("Ошибка при загрузке состояния:", e)
            teams = {}
    else:
        print("⚠️ Файл сохранения не найден, начинаем с чистого листа")
        teams = {}


# === Функции работы программы ===
def debug_print_keys():
    # Показывает текущие ключи в словаре teams — полезно для отладки
    print("DEBUG: текущие команды в памяти:", list(teams.keys()))
    if teams:
        print("DEBUG: детальная структура команд:")
        for key, team in teams.items():
            print(f"  Ключ: '{key}' -> Команда: '{team.name}' (id: {id(team)}, игроков: {len(team)})")
            for player in team.players:
                print(f"    Игрок: {player.name} (№{player.number})")
    else:
        print("DEBUG: словарь teams пуст")


def create_team():
    name = input("Введите название команды: ").strip()
    if not name:
        print("❌ Название не может быть пустым.")
        return
    
    key = name.lower().strip()
    print(f"DEBUG: Создание команды. Введено: '{name}', ключ: '{key}'")
    print(f"DEBUG: Текущие ключи перед созданием: {list(teams.keys())}")
    
    if key in teams:
        print(f"❌ Команда '{name}' уже существует.")
        debug_print_keys()
        return
    
    # Создаем команду и сразу проверяем
    new_team = Team(name)
    teams[key] = new_team
    print(f"DEBUG: Команда создана. Проверяем наличие ключа '{key}': {key in teams}")
    
    save_state()
    print(f"✅ Команда '{name}' создана.")
    debug_print_keys()


def add_player_to_team():
    if not teams:
        print("❌ Нет созданных команд. Сначала создайте команду.")
        debug_print_keys()
        return
        
    name = input("Введите название команды: ").strip()
    if not name:
        print("❌ Название команды не может быть пустым.")
        return
        
    key = name.lower()
    print(f"DEBUG: Поиск команды. Введено: '{name}', ключ для поиска: '{key}'")
    print(f"DEBUG: Доступные ключи: {list(teams.keys())}")
    
    team = teams.get(key)
    
    # ИСПРАВЛЕНИЕ: проверяем именно на None, а не на "falsy"
    if team is None:
        print(f"❌ Команда '{name}' не найдена.")
        print(f"DEBUG: teams.get('{key}') вернул: {team}")
        debug_print_keys()
        return

    print(f"DEBUG: Команда найдена: {team.name}")
    
    player_name = input("Имя игрока: ").strip()
    if not player_name:
        print("❌ Имя не может быть пустым.")
        return
        
    try:
        number = int(input("Номер игрока: ").strip())
        if number <= 0:
            print("❌ Номер должен быть положительным числом.")
            return
    except ValueError:
        print("❌ Неверный номер — нужно целое число.")
        return
        
    position = input("Позиция игрока: ").strip()
    if not position:
        print("❌ Позиция не может быть пустой.")
        return

    try:
        # Проверяем, нет ли уже игрока с таким номером в команде
        for existing_player in team.players:
            if existing_player.number == number:
                print(f"❌ Игрок с номером {number} уже существует в команде.")
                return
                
        player = Player(player_name, number, position)
        team.add_player(player)
        save_state()
        print(f"✅ Игрок {player_name} добавлен в команду {team.name}.")
        print(f"DEBUG: Теперь в команде {len(team.players)} игроков")
    except Exception as e:
        print("❌ Ошибка при добавлении игрока:", e)


def show_team_info():
    if not teams:
        print("❌ Нет созданных команд.")
        return
        
    name = input("Введите название команды: ").strip()
    if not name:
        print("❌ Название команды не может быть пустым.")
        return
        
    key = name.lower()
    print(f"DEBUG: Поиск команды для информации. Ключ: '{key}'")
    
    team = teams.get(key)
    
    # ИСПРАВЛЕНИЕ: проверяем именно на None
    if team is None:
        print(f"❌ Команда '{name}' не найдена.")
        debug_print_keys()
        return

    print(f"\n=== {team.name} ===")
    print(f"Количество игроков: {len(team)}")
    print(f"Общие голы: {team.total_goals()}")
    print(f"Общие передачи: {team.total_assists()}")
    if len(team) > 0:
        print(f"Средние матчи на игрока: {team.total_games() / len(team):.2f}")
    else:
        print("Средние матчи на игрока: 0.00")
    
    if team.players:
        print("Состав:")
        for p in team.players:
            print(f"  - {p.name} (№{p.number}, {p.position}) — Голы: {p.goals}, Передачи: {p.assists}, Матчи: {p.games}")
    else:
        print("Состав: нет игроков")
    print()


def list_all_teams():
    if not teams:
        print("❌ Команды отсутствуют.")
        return
        
    print("\n=== Список всех команд ===")
    for key, team in teams.items():
        print(f" - {team.name} (игроков: {len(team)})")
    debug_print_keys()


def record_match():
    if len(teams) < 2:
        print("❌ Для проведения матча нужно как минимум 2 команды.")
        debug_print_keys()
        return
        
    team_a_name = input("Введите первую команду: ").strip()
    team_b_name = input("Введите вторую команду: ").strip()

    team_a = teams.get(team_a_name.lower())
    team_b = teams.get(team_b_name.lower())

    # ИСПРАВЛЕНИЕ: проверяем именно на None
    if team_a is None or team_b is None:
        print("❌ Одна из команд не найдена.")
        print(f"DEBUG: Команда A '{team_a_name}' -> '{team_a_name.lower()}' {'найдена' if team_a else 'не найдена'}")
        print(f"DEBUG: Команда B '{team_b_name}' -> '{team_b_name.lower()}' {'найдена' if team_b else 'не найдена'}")
        debug_print_keys()
        return

    if team_a == team_b:
        print("❌ Нельзя провести матч между одной и той же командой.")
        return

    match = Match(team_a, team_b)
    print(f"\n🏟️ Матч {match.team_a.name} vs {match.team_b.name} начался!")

    while True:
        goal = input("\nВведите имя игрока, забившего гол (или 'stop' для завершения): ").strip()
        if goal.lower() == "stop":
            break
            
        try:
            minute = int(input("Минута гола: ").strip())
            if minute < 1 or minute > 120:
                print("⚠️ Минута должна быть от 1 до 120.")
                continue
        except ValueError:
            print("⚠️ Введите число для минуты.")
            continue

        # ищем игрока по имени
        found_player = None
        for team in [match.team_a, match.team_b]:
            for p in team.players:
                if p.name.lower() == goal.lower():
                    found_player = p
                    break
            if found_player:
                break

        if not found_player:
            print("❌ Игрок не найден в обеих командах.")
            print(f"Доступные игроки:")
            print(f"  {match.team_a.name}: {[p.name for p in match.team_a.players]}")
            print(f"  {match.team_b.name}: {[p.name for p in match.team_b.players]}")
            continue

        try:
            match.record_goal(found_player, minute)
            print(f"⚽ {found_player.name} забил на {minute}-й минуте!")
        except Exception as e:
            print("❌ Ошибка записи гола:", e)

    print("\n📊 " + match.summary())
    winner = match.winner()
    if winner:
        print(f"🏆 Победитель: {winner.name}")
        save_match(match)
        save_state()
        return
    else:
        print("🤝 Ничья")
        save_match(match)
        save_state()
        return

    # сохраняем матч и обновлённые игроки
    


def save_report():
    if not teams:
        print("❌ Нет созданных команд.")
        return
        
    name = input("Введите название команды для отчёта: ").strip()
    if not name:
        print("❌ Название команды не может быть пустым.")
        return
        
    key = name.lower()
    team = teams.get(key)
    
    # ИСПРАВЛЕНИЕ: проверяем именно на None
    if team is None:
        print(f"❌ Команда '{name}' не найдена.")
        debug_print_keys()
        return
        
    filename = f"report_{team.name.replace(' ', '_')}.docx"
    try:
        save_team_report_docx(team, filename)
        print(f"✅ Отчёт сохранён в файл: {filename}")
    except Exception as e:
        print("❌ Ошибка при сохранении отчёта:", e)


def save_all_to_db():
    if not teams:
        print("❌ Нет данных для сохранения.")
        return
        
    try:
        init_db()
        for team in teams.values():
            save_team(team)
        print("✅ Все данные сохранены в базу данных (sports.db).")
    except Exception as e:
        print("❌ Ошибка при сохранении в базу данных:", e)


# === Главное меню ===
def menu():
    while True:
        print("\n" + "="*5 + " МЕНЮ " + "="*5)
        print("1. Создать команду")
        print("2. Добавить игрока в команду")
        print("3. Показать информацию о команде")
        print("4. Провести матч")
        print("5. Сохранить отчёт (.docx)")
        print("6. Сохранить всё в базу данных")
        print("7. Показать все команды (debug)")
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
            print("👋 Выход из программы. До встречи!")
            save_state()
            sys.exit(0)
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


# === Точка входа ===
if __name__ == "__main__":
    print("⚽ Добро пожаловать в систему управления спортивной командой ⚽")
    print("DEBUG: Загрузка состояния...")
    load_state()
    debug_print_keys()
    menu()