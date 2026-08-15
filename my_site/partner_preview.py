"""Получение изображения для карточки партнёра из метаданных страницы."""

import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_PAGE_SIZE = 1_000_000


def _validate_public_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('разрешены только публичные HTTP/HTTPS-ссылки')
    try:
        addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443)
    except socket.gaierror as error:
        raise OSError('домен не найден') from error
    for address in addresses:
        if not ipaddress.ip_address(address[4][0]).is_global:
            raise ValueError('ссылка ведёт во внутреннюю или служебную сеть')


class _SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _PreviewParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = {}

    def handle_starttag(self, tag, attrs):
        values = {key.lower(): value for key, value in attrs if key and value}
        if tag.lower() == 'meta':
            key = (values.get('property') or values.get('name') or '').lower()
            if key in ('og:image', 'og:image:url', 'twitter:image', 'twitter:image:src'):
                self.images.setdefault(key, values.get('content'))
        elif tag.lower() == 'link' and 'image_src' in values.get('rel', '').lower():
            self.images.setdefault('image_src', values.get('href'))


def fetch_preview_image(url, timeout=5):
    """Возвращает абсолютный URL Open Graph/Twitter-изображения или None."""
    _validate_public_url(url)
    request = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; PartnerPreview/1.0)',
        'Accept': 'text/html,application/xhtml+xml',
    })
    opener = build_opener(_SafeRedirectHandler())
    with opener.open(request, timeout=timeout) as response:
        if response.headers.get_content_type() not in ('text/html', 'application/xhtml+xml'):
            return None
        body = response.read(MAX_PAGE_SIZE + 1)
        if len(body) > MAX_PAGE_SIZE:
            raise ValueError('страница слишком большая для обработки')
        encoding = response.headers.get_content_charset() or 'utf-8'
        final_url = response.geturl()
    parser = _PreviewParser()
    parser.feed(body.decode(encoding, errors='replace'))
    for key in ('og:image', 'og:image:url', 'twitter:image', 'twitter:image:src', 'image_src'):
        image_url = parser.images.get(key)
        if image_url:
            absolute_url = urljoin(final_url, image_url.strip())
            if urlparse(absolute_url).scheme in ('http', 'https'):
                return absolute_url
    return None
