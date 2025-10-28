import subprocess
import sys

if __name__ == "__main__":
    print("Запуск тестов проекта...\n")
    subprocess.run([sys.executable, "-m", "pytest", "-v"])