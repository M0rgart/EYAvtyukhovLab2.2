import pytest
import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, ANY
from src.main import main, create_file
from src.processor import TaskProcessor
from src.sources import FileTaskSource, GeneratorTaskSource, APITaskSource
from src.contracts import Task


class TestFileCreation:
    """Тесты для функции create_file"""

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_create_file_structure(self, mock_json_dump, mock_file):
        """Тест создания файла с правильной структурой"""
        create_file()

        mock_file.assert_called_once_with("file1.json", "w")

        args, kwargs = mock_json_dump.call_args
        data = args[0]

        assert len(data) == 3
        assert data[0]["id"] == "file_1"
        assert data[0]["payload"]["type"] == "calculation"
        assert data[1]["id"] == "file_2"
        assert data[2].get("id") is None
        assert data[2]["payload"]["type"] == "no_id"

        assert kwargs.get('indent') == 2

    @patch('builtins.print')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_create_file_print_message(self, mock_json_dump, mock_file, mock_print):
        """Тест вывода сообщения о создании файла"""
        create_file()

        mock_print.assert_called_once_with("Создан файл file1.json")


class TestMainFunction:
    """Интеграционные тесты для функции main"""

    @patch('src.main.create_file')
    @patch('src.main.TaskProcessor')
    @patch('src.main.FileTaskSource')
    @patch('src.main.GeneratorTaskSource')
    @patch('src.main.APITaskSource')
    @patch('src.main.setup_logfing')
    @patch('builtins.print')
    def test_main_successful_execution(
            self, mock_print, mock_setup, mock_api, mock_gen, mock_file,
            mock_processor_class, mock_create_file
    ):
        """Тест успешного выполнения main функции"""
        mock_file_instance = MagicMock()
        mock_file_instance.__str__.return_value = "FileTaskSource(path=file1.json)"
        mock_file.return_value = mock_file_instance

        mock_gen_instance = MagicMock()
        mock_gen_instance.__str__.return_value = "GeneratorTaskSource(count=3, pref=gen)"
        mock_gen.return_value = mock_gen_instance

        mock_api_instance = MagicMock()
        mock_api_instance.__str__.return_value = "APITaskSource(endpoint=https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        mock_api.return_value = mock_api_instance

        mock_processor = MagicMock()
        mock_processor.add_source.return_value = True
        mock_processor.get_sorce_count.return_value = 3
        mock_processor.process_all.return_value = [
            Task(id=1, payload="task1"),
            Task(id=2, payload="task2"),
            Task(id=3, payload="task3")
        ]
        mock_processor_class.return_value = mock_processor

        main()

        mock_setup.assert_called_once()
        mock_create_file.assert_called_once()
        mock_processor_class.assert_called_once()

        mock_file.assert_called_once_with('file1.json')
        mock_gen.assert_called_once_with(count=3, pref='gen')
        mock_api.assert_called_once()

        assert mock_processor.add_source.call_count == 3

        expected_calls = [
            unittest.mock.call('Источник FileTaskSource(path=file1.json) добавлен'),
            unittest.mock.call('Источник GeneratorTaskSource(count=3, pref=gen) добавлен'),
            unittest.mock.call('Источник APITaskSource(endpoint=https://www.youtube.com/watch?v=dQw4w9WgXcQ) добавлен'),
            unittest.mock.call('Всего источников: 3'),
            unittest.mock.call('НАЧАЛО ОБРАБОТКИ ЗАДАЧ'),
            unittest.mock.call('ИТОГО ПОЛУЧЕНО ЗАДАЧ: 3'),
            unittest.mock.call('\nПервые 5 задач:'),
            unittest.mock.call('1. Task(id=1, payload=task1)'),
            unittest.mock.call('2. Task(id=2, payload=task2)'),
            unittest.mock.call('3. Task(id=3, payload=task3)')
        ]

        actual_calls = mock_print.call_args_list[:len(expected_calls)]
        assert actual_calls == expected_calls

    @patch('src.main.create_file')
    @patch('src.main.TaskProcessor')
    @patch('src.main.FileTaskSource')
    @patch('src.main.GeneratorTaskSource')
    @patch('src.main.APITaskSource')
    @patch('src.main.setup_logfing')
    @patch('builtins.print')
    def test_main_with_failed_source_addition(
            self, mock_print, mock_setup, mock_api, mock_gen, mock_file,
            mock_processor_class, mock_create_file
    ):
        """Тест main когда некоторые источники не добавляются"""
        mock_file_instance = MagicMock()
        mock_file_instance.__str__.return_value = "FileTaskSource(path=file1.json)"
        mock_file.return_value = mock_file_instance

        mock_gen_instance = MagicMock()
        mock_gen_instance.__str__.return_value = "GeneratorTaskSource(count=3, pref=gen)"
        mock_gen.return_value = mock_gen_instance

        mock_api_instance = MagicMock()
        mock_api_instance.__str__.return_value = "APITaskSource(endpoint=https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
        mock_api.return_value = mock_api_instance

        mock_processor = MagicMock()
        mock_processor.add_source.side_effect = [True, False, True]
        mock_processor.get_sorce_count.return_value = 2
        mock_processor.process_all.return_value = [Task(id=1, payload="task1")]
        mock_processor_class.return_value = mock_processor

        main()

        actual_calls = mock_print.call_args_list[:4]
        expected_calls = [
            unittest.mock.call('Источник FileTaskSource(path=file1.json) добавлен'),
            unittest.mock.call('Источник GeneratorTaskSource(count=3, pref=gen) не добавлен'),
            unittest.mock.call('Источник APITaskSource(endpoint=https://www.youtube.com/watch?v=dQw4w9WgXcQ) добавлен'),
            unittest.mock.call('Всего источников: 2')
        ]
        assert actual_calls == expected_calls


class TestRealIntegration:
    """Реальные интеграционные тесты (работают с файловой системой)"""

    @pytest.fixture
    def temp_json_file(self):
        """Фикстура для создания временного JSON файла"""
        data = [
            {"id": "real1", "payload": {"value": 100}},
            {"id": "real2", "payload": {"text": "hello"}}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            temp_path = f.name

        yield temp_path

        os.unlink(temp_path)

    def test_file_task_source_real_file(self, temp_json_file):
        """Тест FileTaskSource с реальным файлом"""
        source = FileTaskSource(temp_json_file)
        tasks = source.get_tasks()

        assert len(tasks) == 2
        assert tasks[0].id == "real1"
        assert tasks[0].payload == {"value": 100}
        assert tasks[1].id == "real2"
        assert tasks[1].payload == {"text": "hello"}

    def test_processor_with_real_sources(self, temp_json_file):
        """Тест процессора с реальными источниками"""
        processor = TaskProcessor()

        file_source = FileTaskSource(temp_json_file)
        gen_source = GeneratorTaskSource(count=2, pref='test')

        processor.add_source(file_source)
        processor.add_source(gen_source)

        assert processor.get_sorce_count() == 2

        tasks = processor.process_all()

        assert len(tasks) == 4

        assert tasks[0].id == "real1"
        assert tasks[1].id == "real2"

        assert tasks[2].id == "test_1"
        assert tasks[3].id == "test_2"

    def test_generator_source_deterministic_with_patch(self):
        """Тест генератора с патчем random для детерминированного поведения"""
        with patch('random.randint', return_value=999):
            source = GeneratorTaskSource(count=2, pref='det')
            tasks = source.get_tasks()

        assert tasks[0].payload['data'] == 999
        assert tasks[1].payload['data'] == 999