from src.sources import FileTaskSource, GeneratorTaskSource, APITaskSource
from src.processor import TaskProcessor
from src.logger_config import setup_logfing
import json, logging


def create_file():
    '''
    Создание файла file1.json с информацией для проверки FileTaskSource
    '''
    data = [
        {"id": "file_1", "payload": {"type": "calculation", "value": 42}},
        {"id": "file_2", "payload": {"type": "validation", "data": [1, 2, 3]}},
        {"payload": {"type": "no_id"}}
    ]

    with open("file1.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Создан файл file1.json")



def main() -> None:
    '''
    Основная функция. Вызывает настойку логов и создание файла для тестов,
    FileTaskSource, GeneratorTaskSource, APITaskSource и выводит результат
    '''
    setup_logfing(logging.INFO)
    create_file()
    processor = TaskProcessor()
    sources = [FileTaskSource('file1.json'),
               GeneratorTaskSource(count=3, pref='gen'),
               APITaskSource()]

    for source in sources:
        if processor.add_source(source):
            print(f'Источник {source} добавлен')
        else:
            print(f'Источник {source} не добавлен')

    print(f'Всего источников: {processor.get_sorce_count()}')

    print("НАЧАЛО ОБРАБОТКИ ЗАДАЧ")

    all_tasks = processor.process_all()

    print(f"ИТОГО ПОЛУЧЕНО ЗАДАЧ: {len(all_tasks)}")

    print("\nПервые 5 задач:")

    for i, task in enumerate(all_tasks[:5], 1):
        print(f"{i}. {task}")


if __name__ == "__main__":
    main()
