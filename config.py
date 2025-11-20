# HYPERLINK_PATTERN = r"<a\s+[^>]*?\bhref\s*=\s*(?P<border>[\"'])(?P<url>.*?)(?P=border)" #Без контента

# HYPERLINK_PATTERN = r"<a\s+[^>]*?\bhref\s*=\s*(?P<border>[\"'])(?P<url>.*?)(?P=border)[^>]*?>(?P<content>.*?)<\/a>" # Без re.DOTALL, но без переноса строки

# HYPERLINK_PATTERN = r"<a\s+[^>]*?\bhref\s*=\s*(?P<border>[\"'])(?P<url>[^\"']+)(?P=border)[^>]*?>(?P<content>.*?)<\/a>" # re.DOTALL

# HYPERLINK_PATTERN = r"<a\s+[^>]*?\bhref\s*=\s*(?P<border>[\"'])(?P<url>[^\"']+)(?P=border)[^>]*?>" # re.DOTALL без контента

# HYPERLINK_PATTERN = r"<a\s+(?:[^>]*?\s)?\bhref\s*=\s*(?P<border>[\"'])(?P<url>[^\"']*)(?P=border)[^>]*?>(?P<content>.*?)<\/a>" # re.DOTALL для что-то-href

HYPERLINK_PATTERN = r"<a\s+(?:[^>]*?\s)?\bhref\s*=\s*(?P<border>[\"'])(?P<url>[^\"']*)(?P=border)[^>]*?>" # re.DOTALL без контента для что-то-href
