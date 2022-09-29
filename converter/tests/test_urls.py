from http import HTTPStatus

from django.test import Client, TestCase


class ConverterUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.url_templates = {
            '/get_offers/': 'converter/index.html',
            '/': 'converter/index.html',
        }

        cls.urls = [
            '/payment_methods/',
        ]

    def test_urls_available_and_uses_correct_templates(self):
        """Urls available and use correct template."""
        for address, template in self.url_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_available(self):
        """Urls available.

        For urls without template.
        """
        for address in self.urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
