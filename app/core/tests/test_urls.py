from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import home


class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, home)
    def test_home_url_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    def test_home_url_uses_correct_template(self):
        """Test that home URL uses correct template"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')



