"""
Лабораторная работа №2. Вариант 20.
Задание №1 = 4: Повышение резкости (Unsharp Masking)
Задание №2 = 2: Робастная (устойчивая) коррекция яркости
"""

import os
import sys
import datetime

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()
os.chdir(SCRIPT_DIR)

try:
    import cv2
    import numpy as np
except ImportError as e:
    print("=" * 60)
    print("ОШИБКА: не установлена библиотека:", e.name)
    print("Открой PowerShell и выполни:")
    print("    python -m pip install opencv-python numpy")
    print("=" * 60)
    input("Нажми Enter для выхода...")
    sys.exit(1)

BASE = "Lab2_Media"
INPUT_DIR = os.path.join(BASE, "data", "input")
OUTPUT_DIR = os.path.join(BASE, "data", "output")
LOG_FILE = os.path.join(BASE, "logs", "history.txt")
RESULT_PATH = os.path.join(OUTPUT_DIR, "result.jpg")


def unsharp_masking(img, sigma=1.0, strength=1.5):
    """Повышение резкости: I_sharp = I + k*(I - Blur(I))."""
    blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma)
    return cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)


def robust_correction(img):
    """Робастная коррекция яркости по медиане и MAD."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    median = float(np.median(gray))
    mad = float(np.median(np.abs(gray.astype(np.float32) - median))) or 1.0
    shift = 128.0 - median
    scale = 1.0 + 0.5 * (shift / 128.0)
    out = img.astype(np.float32) * scale + shift * 0.5
    return np.clip(out, 0, 255).astype(np.uint8)


def log_entry(filename, filter_name, status):
    """Дозапись строки в журнал (режим 'a', UTF-8)."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[{}] Файл: {} | Фильтр: {} | Статус: {}\n".format(
        ts, filename, filter_name, status
    )
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="UTF-8") as f:
        f.write(line)


def main():
    print("Рабочая папка:", os.getcwd())
    if not os.path.isdir(BASE):
        print("ОШИБКА: папка '{}' не найдена рядом со скриптом!".format(BASE))
        return

    filename = input("Имя файла (например, image1.jpg): ").strip()
    if not filename:
        print("Имя файла не введено")
        return

    path = os.path.join(INPUT_DIR, filename)

    if not os.path.exists(path):
        print("Ошибка: Файл не найден")
        log_entry(filename, "-", "Ошибка: файл не найден")
        return

    try:
        with open(path, "rb") as f:
            raw = f.read()
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise IOError("decode failed")
    except (PermissionError, IOError, OSError):
        print("Ошибка: Нет прав на чтение файла {}. Обратитесь к администратору".format(filename))
        log_entry(filename, "-", "Ошибка доступа")
        return

    try:
        result = robust_correction(unsharp_masking(img))
    except Exception as e:
        print("Ошибка обработки:", e)
        log_entry(filename, "-", "Ошибка обработки")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not cv2.imwrite(RESULT_PATH, result):
        print("Ошибка сохранения")
        log_entry(filename, "-", "Ошибка сохранения")
        return

    print("Готово! Результат сохранён:", RESULT_PATH)
    log_entry(filename, "Unsharp Masking + Робастная коррекция", "Успешно")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Неожиданная ошибка:", e)
    finally:
        try:
            input("\nEnter для выхода...")
        except EOFError:
            pass
