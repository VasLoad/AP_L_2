import re
from typing import Optional, Any
from urllib.parse import urljoin, urlparse, ParseResult
from functools import cached_property
import requests
from requests.exceptions import RequestException
from pathlib import Path

from errors import EmptyValueForMethodError

from config import HYPERLINK_PATTERN


class Link:
    """Класс ссылки.

    Attributes:
        _url: Ссылка.
        _base_url: Базовая ссылка (опционально).
    """

    def __init__(self, url: str, base_url: Optional[str] = None):
        self._url = url.strip()
        self._base_url = base_url.strip() if base_url else None

    @property
    def url(self) -> str:
        """Ссылка.

        Returns:
            Ссылка.
        """

        return self._url

    @property
    def base_url(self) -> Optional[str]:
        """Базовая ссылка или None.

        Returns:
            Базовая ссылка или None.
        """

        return self._base_url

    @property
    def is_absolute(self) -> bool:
        """Является ли URL абсолютным.

        Returns:
            Является ли URL абсолютным.
        """

        return bool(urlparse(self.url).scheme)

    @cached_property
    def absolute(self) -> Optional[str]:
        """Абсолютный URL или None.

        Returns:
            Абсолютный URL или None.
        """

        if self.is_absolute:
            return self.url

        if not self.base_url:
            return None

        return urljoin(self.base_url, self.url)

    @cached_property
    def scheme(self) -> Optional[str]:
        """Схема абсолютного URL или None.

        Returns:
            Схема абсолютного URL или None.
        """

        if self.absolute:
            return self._parsed.scheme

        return None

    @cached_property
    def domain(self) -> Optional[str]:
        """Домен в нижнем регистре или None.

        Returns:
            Домен в нижнем регистре или None.
        """

        if self.absolute:
            domain = self._parsed.netloc

            return domain.lower() if domain else None

        return None

    @cached_property
    def path(self) -> Optional[str]:
        """Путь абсолютной ссылки или None.

        Returns:
            Путь абсолютной ссылки или None.
        """

        if self.absolute:
            return urlparse(self.absolute).path or None

        return None

    @property
    def info(self) -> dict[str, Any]:
        """Информация о ссылке в виде словаря.

        Returns:
            Информация о ссылке в виде словаря.
        """

        return {
            "url": self.url,
            "base_url": self.base_url,
            "absolute_url": self.absolute,
            "is_absolute": self.is_absolute,
            "scheme": self.scheme,
            "domain": self.domain,
            "path": self.path,
        }

    @cached_property
    def _parsed(self) -> ParseResult:
        """Кэшированный результат urlparse.

        Returns:
            Кэшированный результат urlparse.
        """

        url_to_parse = self.absolute if self.absolute is not None else self.url

        return urlparse(url_to_parse)


class LinkExtractor:
    """Класс для извлечения и анализа ссылок из файлов .HTML/ссылок/HTML-кода с использованием регулярных выражений.

    Returns:
        Список экземпляров класса Link.
    """

    def __init__(self, base_url: Optional[str] = None):
        self._base_url = base_url.rstrip("/") if base_url else None

    def extract_from_file(self, html_file_path: str, unique: bool = False) -> list[Link]:
        """Извлекает ссылки и возвращает экземпляры класса Link из файла .HTML.

        Args:
            html_file_path: путь к файлу .HTML;
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Link (без дубликатов, если unique is True).

        Raises:
            FileNotFoundError: Файл .HTML не найден;
            ValueError: Указанный путь не является файлом .HTML;
            PermissionError: Отсутствуют права на чтение файла;
            OSError: Ошибка при чтении файла.
        """

        path = Path(html_file_path)

        if not path.exists():
            raise FileNotFoundError(f"Файл .HTML не найден: {path}.")

        if not path.is_file() or path.suffix not in (".html", ".htm"):
            raise ValueError(f"Указанный путь не является файлом .HTML: {path}.")

        try:
            with open(html_file_path, "r", encoding="utf-8") as html_file:
                html_content = html_file.read()
        except PermissionError:
            raise PermissionError(f"Отсутствуют права на чтение файла {path}.")
        except OSError as ex:
            raise OSError(f"Ошибка при чтении файла {path}.\nТекст ошибки: {ex}")

        return self.extract_from_html_code(html_content, unique)

    def extract_from_url(self, unique: bool = False) -> list[Link]:
        """Извлекает ссылки и возвращает экземпляры класса Link из url.

        Args:
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Link (без дубликатов, если unique is True).

        Raises:
            EmptyValueForMethodError: Поле "base_url" не может быть пустым для выполнения данного метода;
            RequestException: Ошибка при получении доступа к удалённому ресурсу.
        """

        if not self._base_url:
            raise EmptyValueForMethodError("base_url")

        try:
            response = requests.get(self._base_url, timeout=25)

            response.raise_for_status()

            return self.extract_from_html_code(response.text, unique)
        except RequestException as ex:
            raise RequestException(f"Ошибка при получении доступа к удалённому ресурсу {self._base_url}.\nТекст ошибки: {ex}")

    def extract_from_html_code(self, html_content: str, unique: bool = False) -> list[Link]:
        """Извлекает ссылки и возвращает экземпляры класса Link из HTML-кода.

        Args:
            html_content: HTML-код;
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Link (без дубликатов, если unique is True).
        """

        if not html_content:
            return []

        hyperlink_regex = re.compile(HYPERLINK_PATTERN, re.IGNORECASE | re.DOTALL)

        matches = hyperlink_regex.finditer(html_content)

        urls = [match.group("url").strip() for match in matches]

        if unique:
            urls = set(urls)

        return [Link(url=url, base_url=self._base_url) for url in urls]

    @staticmethod
    def validate_links(links: list[Link]) -> list[dict[str, Any]]:
        """Возвращает список с информацией о каждой ссылке.

        Args:
            links: Список экземпляров класса Link.

        Returns:
            Список словарей с анализом.
        """

        return [link.info for link in links]


if __name__ == "__main__":
    html = """
    <html>
        <body>
            <a href="https://example.ru/page1">Гиперссылка 1</a>
            <a href="/relative/path">Гиперссылка 2</a>
            <a href="contact.html">Гиперссылка 3</a>
            <a href="../about/team">Гиперссылка 4</a>
            <a href="//youtube.com/video">Гиперссылка 5</a>
            <a href="https://sub.example.ru/test">Гиперссылка 6</a>
            <a href="#section2">Гиперссылка 7</a>
            <a href="mailto:user@example.ru">Гиперссылка 8</a>
            <a href="   https://example.ru/with-spaces   ">Гиперссылка 9</a>
        </body>
    </html>
    """

    extractor = LinkExtractor(base_url="https://example.ru")

    links = extractor.extract_from_html_code(html)
    print(f"Найдено гиперссылок: {len(links)}")

    for link in links:
        info = link.info

        print(f"\nСсылка: {info["url"]}")
        print(f"\tБазовая: {info["base_url"]}")
        print(f"\tАбсолютная: {info["absolute_url"]}")
        print(f"\tАбсолютная (?): {info["is_absolute"]}")
        print(f"\tСхема: {info["scheme"]}")
        print(f"\tДомен: {info["domain"]}")
        print(f"\tПуть: {info["path"]}")

    print()
    print("Колчество гиперссылок по URL:", len(LinkExtractor("https://convertio.co/ru").extract_from_url()))
    print()

    print("Ссылки из файла:")
    for link in LinkExtractor("http://localhost:25990").extract_from_file("file.html"):
        print('\t' + link.absolute)
