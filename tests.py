import unittest
from requests import RequestException
from unittest.mock import patch, mock_open, MagicMock

from main import Hyperlink, HyperlinkExtractor

from errors import EmptyValueForMethodError


class TestHyperlink(unittest.TestCase):
    def test_absolute_url(self):
        link = Hyperlink("https://example.com/path/to/page.html")

        self.assertTrue(link.is_absolute)
        self.assertEqual(link.absolute, "https://example.com/path/to/page.html")
        self.assertEqual(link.scheme, "https")
        self.assertEqual(link.domain, "example.com")
        self.assertEqual(link.path, "/path/to/page.html")

    def test_relative_url_with_base(self):
        link = Hyperlink("/relative/path", base_url="https://example.com/base/")

        self.assertFalse(link.is_absolute)
        self.assertEqual(link.absolute, "https://example.com/relative/path")
        self.assertEqual(link.scheme, "https")
        self.assertEqual(link.domain, "example.com")
        self.assertEqual(link.path, "/relative/path")

    def test_relative_url_without_base(self):
        link = Hyperlink("/relative/path")

        self.assertFalse(link.is_absolute)
        self.assertIsNone(link.absolute)
        self.assertIsNone(link.scheme)
        self.assertIsNone(link.domain)
        self.assertIsNone(link.path)

    def test_protocol_relative_url(self):
        link = Hyperlink("//evil.com/hack", base_url="https://example.com")

        self.assertFalse(link.is_absolute)  # urlparse считает //evil.com схемой пустой
        self.assertEqual(link.absolute, "https://evil.com/hack")
        self.assertEqual(link.domain, "evil.com")

    # def test_internal_link_detection(self):
    #     tests = [
    #         ("https://example.com/page", "https://example.com", True),
    #         ("https://sub.example.com", "https://example.com", False),
    #         ("https://example.com", "https://example.com", True),
    #         ("//example.com", "https://example.com", True),
    #         ("//sub.example.com", "https://example.com", False),
    #         ("/internal", "https://example.com", True),
    #     ]
    #
    #     for url, base, expected in tests:
    #         with self.subTest(url=url):
    #             link = Hyperlink(url, base_url=base)
    #
    #             self.assertEqual(link.is_internal, expected)
    #
    # def test_subdomain_is_not_internal(self):
    #     link = Hyperlink("https://blog.example.com", base_url="https://example.com")
    #
    #     self.assertFalse(link.is_internal)
    #
    # def test_anchor_only(self):
    #     link = Hyperlink("#section", base_url="https://example.com/page")
    #
    #     self.assertFalse(link.is_absolute)
    #     self.assertEqual(link.absolute, "https://example.com/page#section")
    #     self.assertTrue(link.is_internal)
    #
    # def test_mailto(self):
    #     link = Hyperlink("mailto:user@example.com", base_url="https://example.com")
    #
    #     self.assertTrue(link.is_absolute)
    #     self.assertEqual(link.absolute, "mailto:user@example.com")
    #     self.assertIsNone(link.domain)
    #     self.assertIsNone(link.is_internal)

    def test_spaces_in_url(self):
        link = Hyperlink("   https://example.com/spaces   ", base_url="https://example.com")

        self.assertEqual(link.url, "https://example.com/spaces")
        self.assertTrue(link.is_absolute)

    def test_info_property(self):
        link = Hyperlink("/test", base_url="https://example.com")

        info = link.info

        self.assertIsInstance(info, dict)
        self.assertEqual(info["url"], "/test")
        self.assertEqual(info["absolute_url"], "https://example.com/test")
        # self.assertTrue(info["is_internal"])

class TestHTMLLinkExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = HyperlinkExtractor(base_url="https://example.com/")

    def test_extract_from_html_basic(self):
        html = '''
        <a href="https://example.com/abs">Abs</a>
        <a href="/rel">Rel</a>
        <a href="  /spaced  ">Spaced</a>
        <a href='single.html'>Single quotes</a>
        '''

        links = self.extractor.extract_from_html(html)

        self.assertEqual(len(links), 4)
        urls = [l.url for l in links]
        self.assertIn("https://example.com/abs", urls)
        self.assertIn("/rel", urls)
        self.assertIn("/spaced", urls)
        self.assertIn("single.html", urls)

    def test_unique_flag(self):
        html = '''
        <a href="/dup">1</a>
        <a href="/dup">2</a>
        <a href="/dup">3</a>
        '''

        links_with_dup = self.extractor.extract_from_html(html, unique=False)
        links_unique = self.extractor.extract_from_html(html, unique=True)

        self.assertEqual(len(links_with_dup), 3)
        self.assertEqual(len(links_unique), 1)
        self.assertEqual(links_unique[0].url, "/dup")

    def test_extract_from_file(self):
        html_content = '<a href="/from_file">Test</a>'

        with patch("builtins.open", mock_open(read_data=html_content)):
            links = self.extractor.extract_from_file("fake.html")

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].url, "/from_file")
        self.assertEqual(links[0].absolute, "https://example.com/from_file")

    def test_extract_from_url_success(self):
        mock_response = MagicMock()
        mock_response.text = '<a href="/from_url">OK</a>'
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response) as mocked_get:
            links = self.extractor.extract_from_url()

        mocked_get.assert_called_once_with("https://example.com", timeout=25)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].url, "/from_url")

    def test_extract_from_url_no_base_url(self):
        extractor_no_base = HyperlinkExtractor()

        with self.assertRaises(EmptyValueForMethodError) as cm:
            extractor_no_base.extract_from_url()

        self.assertEqual(str(cm.exception), str(EmptyValueForMethodError("base_url")))

    def test_extract_from_url_request_exception(self):
        extractor = HyperlinkExtractor(base_url="https://example.com")

        with patch.object(extractor, "extract_from_url") as mock_fetch_html:
            mock_fetch_html.side_effect = RequestException("Connection error")

            with self.assertRaises(RequestException) as cm:
                extractor.extract_from_url()

        self.assertIsInstance(cm.exception, RequestException)

    def test_validate_links_static(self):
        links = [
            Hyperlink("https://example.com/1", base_url="https://example.com"),
            Hyperlink("/2", base_url="https://example.com"),
        ]

        result = HyperlinkExtractor.validate_hyperlinks(links)

        self.assertEqual(len(result), 2)
        self.assertIn("absolute_url", result[0])
        # self.assertIn("is_internal", result[0])
        # self.assertTrue(result[1]["is_internal"])

    def test_empty_html(self):
        links = self.extractor.extract_from_html("")
        self.assertEqual(links, [])

    def test_no_a_tags(self):
        html = "<div>No links here</div>"
        links = self.extractor.extract_from_html(html)
        self.assertEqual(links, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)