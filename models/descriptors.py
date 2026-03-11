import time, logging
from datetime import datetime
from typing import Optional, Any, Callable
import exceptions
from src.contracts import TaskSource

logger = logging.getLogger(__name__)


class ValidatedString:
    """
    Data descriptor для валидации строковых атрибутов
    """

    def __init__(self, min_len: int = 1, max_len: int = 255, nullable: bool = False,
                 error_class: Exception = exceptions.InvalidDescriptionError):
        self.min_len = min_len
        self.max_len = max_len
        self.nullable = nullable
        self.error_class = error_class
        self.data = {}

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.data.get(id(obj), "" if not self.nullable else None)

    def __set__(self, obj, value):
        if value is None:
            if self.nullable:
                self.data[id(obj)] = None
                logger.debug(f"Установленно значение None для {self}")
                return
            else:
                raise self.error_class(f"Значение не может быть None", str(self))

        if not isinstance(value, str):
            raise self.error_class(f"Значение должно быть строкой,"
                                   f"получен {type(value).__name__}", str(self))

        if len(value) < self.min_len:
            raise self.error_class(f"Строка слишком короткая (мин. {self.max_len})", str(self))

        if len(value) > self.max_len:
            raise self.error_class(f"Строка слишком длинная (макс. {self.max_len})", str(self))

        self.data[id(obj)] = value.strip()
        logger.debug(f"Установлено значение '{value}' для {self}")

    def __delete__(self, obj):
        """Запрет на удаление атрибута"""
        raise AttributeError(f"Нельзя удалить атрибут {self}")

    def __repr__(self):
        return f"ValidatedString(min={self.min_len}, max={self.max_len})"