import unittest

from main import LinkExtractor

class TestHyperlinkRegex(unittest.TestCase):
    """Класс тестов регулярного выражения для поиска гиперссылок."""

    def setUp(self):
        """Создаёт новый экземпляр класса LinkExtractor при каждом новом тесте."""

        self.extractor = LinkExtractor()

    def test_with_enters(self):
        """Проверяет гиперссылки с пробельными символами."""

        html_code = """
            <a href="https://convertio.co/ru/" aria-label="Go to index page">
                <svg xmlns="http://www.w3.org/2000/svg" width="147" height="30" viewBox="0 0 147 30">
                <path fill="#ff3333"
                      d="M15.047 30C6.737 30 0 23.284 0 15 0 6.716 6.737 0 15.047 0s15.047 6.716 15.047 15c0 8.284-6..889-1.695-1.673-2.229-2.95-2.229-5.111h2.898L8.694 8.667l-5.573 6.222h2.675z"></path>
                <path fill="#282828"
                      d=74-.838-.56-1.773-.56-2.805 0-1.032.186-1.963.56-2.792a6.27 6.27 0 0 1 1.515-2.107 6.593 6.593 0 0 1 2.568.5.941-.748.255-.313.446-.665.573-1.054.128-.389.191-.787.191-1.193z"></path>
                </svg>
            </a>
            
            <a\nhref="https://example.ru">
            <a href=\n"https://example.ru">
            <a target="target"\nhref="https://example.ru">
            <a href="https://example.ru"\ntarget="target">
            <a\t\nhref="https://example.ru">
            <a href="https://example.ru"\n>Гиперссылка</a>
            <a href="https://example.ru">Д\nа\nн\nн\nы\nе</a>
            <a href="https://example.ru">\nЧто-то\n
        """

        self.assertEqual(len(self.extractor.extract_from_html_code(html_code)), 9)

    def test_valid_quoted(self):
        """Проверяет гиперссылки с корректными кавычками."""

        hyperlinks = [
            '<a href="https://example.ru">',
            "<a href='https://example.ru'>",
            '<a href = "https://example.ru">',
            '<a href\t=\t"https://example.ru">',
            '<a HREF="https://example.ru">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_invalid_quoted(self):
        """Проверяет гиперссылки с некорректными кавычками."""

        hyperlinks = [
            '<a href=https://example.ru>',
            "<a href='https://example.ru\">",
            '<a href="https://example.ru\'>',
            '<a href=https://example.ru>'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 0)

    def test_spaces_inside_quotes(self):
        """Проверяет гиперссылки с пробелами внутри ссылки."""

        hyperlinks = [
            '<a href="    https://example.ru">',
            '<a href="https://example.ru    ">',
            '<a href="    https://example.ru    ">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_spaces_near_href_equal_operator(self):
        """Проверяет гиперссылки с пробелами между = после атрибута href."""

        hyperlinks = [
            '<a href ="https://example.ru">',
            '<a href= "https://example.ru">',
            '<a href = "https://example.ru">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_empty_url(self):
        """Проверяет гиперссылки на пустые ссылки."""

        hyperlinks = [
            '<a href="     ">',
            '<a href="">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_with_other_attributes(self):
        """Проверяет гиперссылки с другими атрибутами до href."""

        hyperlinks = [
            '<a target="target" href="https://example.ru">',
            '<a class="hyperlink" href="https://example.ru">',
            '<a href="https://example.ru" target="target">',
            '<a href="https://example.ru" class="hyperlink">',
            '<a target="target" href="https://example.ru" class="hyperlink">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_with_unicode_characters(self):
        """Проверяет гиперссылки с символами из Unicode."""

        hyperlinks = [
            '<a href="https://example.рф">',
            '<a href="https://сайт.рф">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_href_with_html_entities(self):
        """Проверяет гиперссылки с сущностями HTML."""

        hyperlinks = [
            '<a href="https://example.ru?a=1&amp;b=2">',
            '<a href="https://example.ru/with%20path/">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_with_different_schemes(self):
        """Проверяет гиперссылки с различными схемами."""

        hyperlinks = [
            '<a href="ftp://example.ru/file.txt">',
            '<a href="tel:+71234567890">',
            '<a href="javascript:void(0)">'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 1)

    def test_invalid_href_name(self):
        """Проверяет гиперссылки с неправильным атрибутом href."""

        hyperlinks = [
            '<a name="name">',
            '<a>Клик</a>',
            '<a></a>',
            '<a data-href=""></a>',
            '<a href=>'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 0)

    def test_other_attributes_with_href_word_are_ignored(self):
        """Проверяет гиперссылки со сломанным тегом <a>."""

        hyperlinks = [
            '<a href="https://example.ru',
            '<a href="https://example.ru>',
            '<a href="https://example.ru" random_attribute',
            '<a href=">',
            '<a href=>'
        ]

        for hyperlink in hyperlinks:
            self.assertEqual(len(self.extractor.extract_from_html_code(hyperlink)), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
