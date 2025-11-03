# sports_team/utils.py
import time
import functools


def timed(func):
    """Декоратор — измеряет время выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f" {func.__name__} выполнена за {elapsed:.4f} сек")
        return result
    return wrapper

def validate_non_negative(value: int, name: str):
    """Утилита для проверки неотрицательных значений."""
    if value < 0:
        raise ValueError(f"{name} не может быть отрицательным.")

