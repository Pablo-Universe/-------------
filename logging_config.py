# [НОВИЙ ФАЙЛ] доданий під час рефакторингу
"""Налаштування стандартного модуля logging (консоль + файл)."""
import logging
from pathlib import Path

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(log_file: str = "app.log", level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if getattr(root, "_bank_configured", False):
        return
    root.setLevel(level)
    formatter = logging.Formatter(_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    try:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError as e:
        root.warning("Не вдалося відкрити лог-файл %s: %s", log_file, e)

    root._bank_configured = True  # type: ignore[attr-defined]