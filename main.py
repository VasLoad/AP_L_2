import re
from typing import Optional, Any
from urllib.parse import urljoin, urlparse, ParseResult
from functools import cached_property
import requests
from requests.exceptions import RequestException
from pathlib import Path

from errors import EmptyValueForMethodError

from config import HYPERLINK_PATTERN


class Hyperlink:
    """Класс гиперссылки.

    Attributes:
        _url: Ссылка.
        _base_url: Базовая ссылка (опционально).
    """

    def __init__(self, url: str, base_url: Optional[str] = None):
        self._url = url.strip()
        self._base_url = base_url.strip() if base_url else None

    @property
    def url(self) -> str:
        """Ссылка."""

        return self._url

    @property
    def base_url(self) -> str:
        """Базовая ссылка."""

        return self._base_url

    @cached_property
    def _parsed(self) -> ParseResult:
        """Кэшированный результат urlparse для повторного использования."""

        url_to_parse = self.absolute if self.absolute is not None else self.url

        return urlparse(url_to_parse)

    @property
    def is_absolute(self) -> bool:
        """Является ли URL абсолютным."""

        return bool(urlparse(self.url).scheme)

    @cached_property
    def absolute(self) -> Optional[str]:
        """Получение абсолютного URL (при наличии).

        Returns:
            Абсолютный URL при наличии.
        """

        if self.is_absolute:
            return self.url

        if not self.base_url:
            return None

        return urljoin(self.base_url, self.url)

    @cached_property
    def scheme(self) -> Optional[str]:
        """Схема абсолютного URL или None."""

        if self.absolute:
            return self._parsed.scheme

        return None

    @cached_property
    def domain(self) -> Optional[str]:
        """Домен в нижнем регистре или None."""

        if self.absolute:
            domain = self._parsed.netloc

            return domain.lower() if domain else None

        return None

    @cached_property
    def path(self) -> Optional[str]:
        """Путь абсолютной ссылки или None."""

        if self.absolute:
            return urlparse(self.absolute).path or None

        return None

    @property
    def info(self) -> dict[str, Any]:
        """Информация о ссылке в виде словаря."""

        return {
            "url": self.url,
            "base_url": self.base_url,
            "absolute_url": self.absolute,
            "is_absolute": self.is_absolute,
            "scheme": self.scheme,
            "domain": self.domain,
            "path": self.path,
        }


class HyperlinkExtractor:
    """Класс для извлечения и анализа ссылок из файлов .HTML/ссылок/HTML-кода с использованием регулярных выражений.
    Возвращает список экземпляров класса Hyperlink.
    """

    def __init__(self, base_url: Optional[str] = None):
        self._base_url = base_url.rstrip("/") if base_url else None

    def extract_from_file(self, html_file_path: str, unique: bool = False) -> list[Hyperlink]:
        """Извлекает ссылки и возвращает экземпляры класса Hyperlink из файла .HTML.

        Args:
            html_file_path: путь к файлу .HTML.
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Hyperlink.
            Без дубликатов, если unique=True.

        Raises:
            FileNotFoundError: Файл .HTML не найден.
            ValueError: Указанный путь не является файлом .HTML.
            PermissionError: Отсутствуют права на чтение файла.
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

        return self.extract_from_html(html_content, unique)

    def extract_from_url(self, unique: bool = False) -> list[Hyperlink]:
        """Извлекает ссылки и возвращает экземпляры класса Hyperlink из url.

        Args:
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Hyperlink.
            Без дубликатов, если unique=True.

        Raises:
            EmptyValueForMethodError: Поле "base_url" не может быть пустым для выполнения данного метода.
            RequestException: Ошибка при получении доступа к удалённому ресурсу.
        """

        if not self._base_url:
            raise EmptyValueForMethodError("base_url")

        try:
            response = requests.get(self._base_url, timeout=25)

            response.raise_for_status()

            return self.extract_from_html(response.text, unique)
        except RequestException as ex:
            raise RequestException(f"Ошибка при получении доступа к удалённому ресурсу {self._base_url}.\nТекст ошибки: {ex}")

    def extract_from_html(self, html_content: str, unique: bool = False) -> list[Hyperlink]:
        """Извлекает ссылки и возвращает экземпляры класса Hyperlink из HTML-кода.

        Args:
            html_content: HTML-код.
            unique: Если True - дубликаты ссылок удаляются. По умолчанию False.

        Returns:
            Список объектов Hyperlink.
            Без дубликатов, если unique=True.
        """

        if not html_content:
            return []

        matches = re.compile(HYPERLINK_PATTERN, re.IGNORECASE).finditer(html_content)

        urls = [match.group("url").strip() for match in matches]

        if unique:
            urls = set(urls)

        return [Hyperlink(url=url, base_url=self._base_url) for url in urls]

    @staticmethod
    def validate_hyperlinks(links: list[Hyperlink]) -> list[dict[str, Any]]:
        """Возвращает список с информацией о каждой ссылке.

        Args:
            links: Список объектов Hyperlink.

        Returns:
            Список словарей с анализом.
        """

        return [link.info for link in links]


if __name__ == "__main__":
    html = """
    <html>
        <body>
            <a href="https://example.com/page1">Абсолютная внутренняя</a>
            <a href="/relative/path">Относительная от корня</a>
            <a href="contact.html">Относительная от текущей папки</a>
            <a href="../about/team">Относительная вверх</a>
            <a href="//evil.com/hack">Протокол-относительная (опасная!)</a>
            <a href="https://sub.example.com/test">Внешний поддомен</a>
            <a href="#section2">Только якорь</a>
            <a href="mailto:user@example.com">Email</a>
            <a href="   https://example.com/with-spaces   ">С пробелами</a>
        </body>
    </html>
    """

    extractor = HyperlinkExtractor(base_url="https://example.com")

    links = extractor.extract_from_html(html)
    print(f"Найдено ссылок: {len(links)}")

    for link in links:
        info = link.info

        print(f"\nСсылка: {info["url"]}")
        print(f"\tБазовая: {info["base_url"]}")
        print(f"\tАбсолютная: {info["absolute_url"]}")
        print(f"\tАбсолютная (?): {info["is_absolute"]}")
        print(f"\tСхема: {info["scheme"]}")
        print(f"\tДомен: {info["domain"]}")
        print(f"\tПуть: {info["path"]}")

    print(len(HyperlinkExtractor("https://convertio.co/ru/mp3-ogg/").extract_from_url(unique=True)))

    for link in HyperlinkExtractor().extract_from_file("file.html"):
        print(link.info, end="\n")
