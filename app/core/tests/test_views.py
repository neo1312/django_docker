from django.test import TestCase
from django.urls import reverse

class HomeViewTests(TestCase):
    def test_home_modules(self):
        """Test that the home view includes the correct modules"""
        response = self.client.get(reverse('home'))
        modules = response.context['modules']
        print (response.context)
        self.assertEqual(modules[0]['name'], "Ventas")
