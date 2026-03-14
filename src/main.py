import logging
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger_config import setup_logging
from src.sources import FileTaskSource, GeneratorTaskSource, APITaskSource
from src.processor import TaskProcessor
from src.contracts import check_task_source
from models.task import Task
from models.exceptions import InvalidStatusError, InvalidIDError


def create_file():
    """Создает пример JSON файла с задачами"""
    import json

    sample_data = [
        {
            "id": "file_1",
            "payload": {
                "type": "calculation",
                "value": 42,
                "description": "Вычислить сумму"
            }
        },
        {
            "id": "file_2",
            "payload": {
                "type": "validation",
                "data": [1, 2, 3],
                "description": "Проверить данные"
            }
        },
        {
            "payload": {
                "type": "no_id",
                "description": "Задача без ID"
            }
        }
    ]

    with open("sample_tasks.json", "w", encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)

    print("Создан файл sample_tasks.json")


def demonstrate_lab1_sources():
    """Демонстрация работы источников задач (ЛР1)"""
    for _ in range(2): print()
    print("ЛАБОРАТОРНАЯ РАБОТА №1: ИСТОЧНИКИ ЗАДАЧ")

    processor = TaskProcessor()

    sources = [
        FileTaskSource("sample_tasks.json"),
        GeneratorTaskSource(count=3, pref="gen"),
        APITaskSource(end="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    ]

    for source in sources:
        if processor.add_source(source):
            print(f"Добавлен источник: {source}")
        else:
            print(f"Источник не прошел проверку: {source}")

    print(f"\nВсего источников: {processor.get_sorce_count()}")
    tasks = processor.process_all()

    print(f"\nПолучено задач: {len(tasks)}")
    for i, task in enumerate(tasks[:5], 1):
        print(f"  {i}. {task}")

    return tasks


def demonstrate_lab2_model():
    """Демонстрация работы модели задачи с дескрипторами (ЛР2)"""
    for _ in range(2): print()
    print("ЛАБОРАТОРНАЯ РАБОТА №2: МОДЕЛЬ ЗАДАЧИ С ДЕСКРИПТОРАМИ")

    # Создание задачи
    task = Task(
        id="TASK-001",
        description="Разработать модуль валидации",
        priority=3,
        status="pending",
        payload={"assignee": "ivanov", "deadline": "2024-02-01"}
    )

    print(f"\n1. СОЗДАНИЕ ЗАДАЧИ:")
    print(f"   {task}")
    print(f"   Приоритет: {task.priority} ({task.priority_name})")
    print(f"   Время создания: {time.ctime(task.created_at)}")

    # Демонстрация валидации
    print(f"\n2. ВАЛИДАЦИЯ АТРИБУТОВ:")
    try:
        Task(id="", description="test", priority=1)
    except InvalidIDError as e:
        print(f"   Перехвачена ошибка: {e}")

    # Изменение статуса
    print(f"\n3. УПРАВЛЕНИЕ СТАТУСОМ:")
    print(f"   Текущий статус: {task.status}")

    task.upd_status("running")
    print(f"   После upd_status('running'): {task.status}")

    task.upd_status("completed")
    print(f"   После upd_status('completed'): {task.status}")

    try:
        task.upd_status("pending")  # Нельзя вернуться
    except InvalidStatusError as e:
        print(f"   Некорректный переход перехвачен: {e}")

    # Вычисляемые свойства
    print(f"\n4. ВЫЧИСЛЯЕМЫЕ СВОЙСТВА:")
    print(f"   Готовность (is_ready): {task.is_ready}")
    print(f"   Завершена (is_completed): {task.is_completed}")
    print(f"   Возраст: {task.age_formatted}")

    # Data vs Non-data descriptors
    print(f"\n5. DATA VS NON-DATA DESCRIPTORS:")
    print(f"   Data descriptor (priority) - хранится в дескрипторе: {task.priority}")
    print(f"   Non-data descriptor (status) - в __dict__: {task.__dict__['status']}")

    return task


def demonstrate_integration():
    """Демонстрация интеграции ЛР1 и ЛР2"""
    for _ in range(2): print()
    print("ИНТЕГРАЦИЯ ЛР1 И ЛР2: ИСТОЧНИКИ + МОДЕЛЬ ЗАДАЧИ")

    class DomainTaskSource:
        def __init__(self, count=3):
            self.count = count

        def get_tasks(self):
            tasks = []
            for i in range(self.count):
                task = Task(
                    id=f"DOMAIN-{i + 1}",
                    description=f"Интегрированная задача {i + 1}",
                    priority=(i % 4) + 1,
                    status="pending",
                    payload={"source": "integration", "number": i + 1}
                )
                tasks.append(task)
            return tasks

        def __repr__(self):
            return f"DomainTaskSource(count={self.count})"

    source = DomainTaskSource()

    if check_task_source(source):
        print(f"Источник доменных задач прошел проверку контракта")

        processor = TaskProcessor()
        processor.add_source(source)

        tasks = processor.process_all()
        print(f"\nПолучено задач из процессора: {len(tasks)}")

        for i, task in enumerate(tasks, 1):
            print(f"\n  {i}. {task}")
            print(f"     Статус: {task.status}")
            print(f"     Приоритет: {task.priority_name}")
            print(f"     Готовность: {task.is_ready}")
    else:
        print("Источник не прошел проверку контракта")


def main():
    """Главная функция"""
    setup_logging(logging.INFO)

    create_file()
    lab1_tasks = demonstrate_lab1_sources()
    lab2_task = demonstrate_lab2_model()
    demonstrate_integration()


if __name__ == "__main__":
    main()