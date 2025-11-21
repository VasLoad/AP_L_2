from typing import Optional

from main import Link, LinkExtractor

# ФАЙЛ ПЕСОЧНИЦЫ ДЛЯ ПРИМЕРА РАБОТЫ С ОСНОВНЫМ ФУНКЦИОНАЛОМ
# ФАЙЛ НЕ ОТНОСИТСЯ К ОСНОВНОМУ ФУНКЦИОНАЛУ

TEXT_INPUT_FILE_PATH = "Путь к файлу"
TEXT_INPUT_URL = "URL удалённого ресурса"
TEXT_INPUT_HTML_CODE = "HTML-код"
TEXT_INPUT_BASE_URL = "Базовый URL"
TEXT_INPUT_UNIQUE = "Уникальные"

TEXT_PRINT_SEPARATOR = "#" * 50


class Sandbox:
    def extract_from_file(self):
        """Извлекает гиперссылки из файла .HTML."""

        file_path, base_url, unique = self.input_all_params(TEXT_INPUT_FILE_PATH)

        exctractor: LinkExtractor = LinkExtractor(base_url)

        try:
            hyperlinks = exctractor.extract_from_file(file_path, unique=unique)

            self.print_hyperlinks_info(hyperlinks)
        except Exception as ex:
            self.print_error(ex)

    def extract_from_url(self):
        """Извлекает гиперссылки с удалённого ресурса по URL."""

        url: str = self.input_str(TEXT_INPUT_URL)
        unique: Optional[bool] = self.input_bool(TEXT_INPUT_UNIQUE)

        exctractor: LinkExtractor = LinkExtractor(url)

        try:
            hyperlinks: list[Link] = exctractor.extract_from_url(unique=unique)

            self.print_hyperlinks_info(hyperlinks)
        except Exception as ex:
            self.print_error(ex)

    def extract_from_stream(self):
        """Извлекает гиперссылки из потока."""

        html_code: str = self.input_str_stream(TEXT_INPUT_HTML_CODE)
        base_url: Optional[str] = self.input_str(TEXT_INPUT_BASE_URL, can_be_empty=True)
        unique: Optional[bool] = self.input_bool(TEXT_INPUT_UNIQUE)

        exctractor: LinkExtractor = LinkExtractor(base_url)

        hyperlinks: list[Link] = exctractor.extract_from_html_code(html_code, unique=unique)

        self.print_hyperlinks_info(hyperlinks)

    @staticmethod
    def print_hyperlinks_info(hyperlinks: list[Link]):
        """Выводит информацию о каждой ссылке из списка.

        Args:
            hyperlinks: Список ссылок.
        """

        hyperlinks_len: int = len(hyperlinks)

        if hyperlinks_len == 0:
            print("Гиперссылки не найдены...")

            return

        print(TEXT_PRINT_SEPARATOR)
        print(f"Найдено гиперссылок: {hyperlinks_len}")
        print(TEXT_PRINT_SEPARATOR)

        for index, hyperlink in enumerate(hyperlinks):
            print(f"Ссылка {index + 1}:")
            print(hyperlink.info)

        print(TEXT_PRINT_SEPARATOR)

    @staticmethod
    def print_error(ex: Exception):
        """Выводит ошибку в случае возникновения проблемы при работе с парсером гиперссылок.

        Args:
            ex: Текст ошибки.
        """

        print("[= Ошибка! =]")
        print(ex)

    @staticmethod
    def print_help():
        """Выводит помощь по работе с программой."""

        print("\n" + "=" * 60)
        print("Источник:")
        print("1 - Файл")
        print("2 - URL")
        print("3 - Поток")
        print("0 / help - показать это меню")
        print("exit - выйти из программы")
        print("=" * 60)

    def input_all_params(
            self,
            prompt: str,
            base_url_prompt: str = TEXT_INPUT_BASE_URL,
            unique_prompt: str = TEXT_INPUT_UNIQUE
            ) -> tuple[str, Optional[str], Optional[bool]]:
        """Принимает введённые пользователем с клавиатуры параметры значения для prompt, base_url и unique.

        Args:
            prompt: Промпт для ввода значения запрашиваемого параметра;
            base_url_prompt: Промпт для ввода базового URL;
            unique_prompt: Промпт для ввода значения уникальности гиперссылок.

        Returns:
            Кортеж значений для запрашиваемого параметра, базового URL и уникальности гиперссылок.
        """

        param: str = self.input_str(prompt)
        base_url: Optional[str] = self.input_str(base_url_prompt, can_be_empty=True)
        unique: Optional[bool] = self.input_bool(unique_prompt)

        return param, base_url, unique

    def input_str_stream(self, prompt: str, stop_command: str = "stop") -> str:
        """Принимает введённые пользователем с клавиатуры значения в потоке.

        Args:
            prompt: Промпт для ввода значения запрашиваемого параметра;
            stop_command: Команда для прекращения ввода в потоке.

        Returns:
            Введённые пользователем с клавиатуры значения, склеенные в строку.
        """

        html_codes: list[str] = []

        print("Начинается ввод в цикле")

        while True:
            param: Optional[str] = self.input_str(f"{prompt} (stop - для выхода)", can_be_empty=True)

            if not param:
                continue

            if param == stop_command:
                break
            else:
                html_codes.append(param)

        return "".join(html_codes)

    def input_bool(self, prompt: str) -> bool:
        """Принимает введённое пользователем с клавиатуры булевое значение.
        
        Args:
            prompt: Промпт для ввода значения запрашиваемого параметра.
        """

        value: Optional[str] = self.input_str(f"{prompt}? [y/n]", can_be_empty=True)

        if value in ["y", "Да", "+"]:
            return True
        else:
            return False

    @staticmethod
    def input_str(prompt: str, can_be_empty: bool = False) -> Optional[str]:
        """Принимает введённое пользователем с клавиатуры значение.

        Args:
            prompt: Промпт для ввода значения запрашиваемого параметра;
            can_be_empty: Может ли введённое значение быть пустым.

        Returns:
            Значение для запрашиваемого параметра (None, если can_be_empty is True).
        """

        while True:
            value: str = input(f"{prompt}{(' (Опционально)' if can_be_empty else '')}: ").strip()

            if value:
                return value
            else:
                if can_be_empty:
                    return None
                else:
                    print("Поле не может быть пустым.")

    def run(self):
        """Запускает работу песочницы."""

        commands = {
            "1": self.extract_from_file,
            "2": self.extract_from_url,
            "3": self.extract_from_stream,
            "0": self.print_help,
            "help": self.print_help,
            "exit": self.exit
        }

        try:
            while True:
                cmd: str = input("\nВведите источник (0 / help - список источников): ").strip().lower()

                if cmd in commands:
                    commands[cmd]()
                else:
                    print("Неизвестная команда. Введите 'help'.")
        except (KeyboardInterrupt, EOFError):
            self.exit()

    @staticmethod
    def exit():
        """Завершает работу песочницы."""

        print("\nВыход из программы...")

        raise SystemExit

if __name__ == "__main__":
    sandbox = Sandbox()

    sandbox.run()
