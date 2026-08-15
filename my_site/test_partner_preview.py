from unittest import mock

from django.test import SimpleTestCase

from .partner_preview import _PreviewParser, _validate_public_url


class PartnerPreviewTest(SimpleTestCase):
    def test_parser_prefers_open_graph_metadata(self):
        parser = _PreviewParser()
        parser.feed('<meta property="og:image" content="/images/card.jpg">')

        self.assertEqual(parser.images['og:image'], '/images/card.jpg')

    @mock.patch('my_site.partner_preview.socket.getaddrinfo')
    def test_private_network_is_rejected(self, getaddrinfo):
        getaddrinfo.return_value = [(None, None, None, None, ('127.0.0.1', 443))]

        with self.assertRaisesMessage(ValueError, 'внутреннюю'):
            _validate_public_url('https://example.test/private')
