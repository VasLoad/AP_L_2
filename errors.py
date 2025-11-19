class DataError(Exception):
    """Базовые исключения, связанные с данными."""

    pass


class EmptyValueForMethodError(DataError):
    """Ошибка пустого поля для метода."""

    def __init__(self, field_name: str):
        super().__init__(f"Поле \"{field_name}\" не может быть пустым для использования данного метода.")
