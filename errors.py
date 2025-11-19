class DataError(Exception):
    """Базовые исключения, связанные с данными."""

    pass


class EmptyValueForMethodError(DataError):
    """Ошибка пустого поля для метода."""

    def __init__(self, field_name: str):
        super().__init__(f"Поле \"{field_name}\" не может быть пустым для использования данного метода.")

class URLError(Exception):
    """Базовые исключения, связанные с удалёнными ресурсами."""

    pass

class URLException(URLError):
    def __init__(self, url: str):
        super().__init__(f"Не удалось получить доступ к удалённому ресурсу по адресу {url}.")
