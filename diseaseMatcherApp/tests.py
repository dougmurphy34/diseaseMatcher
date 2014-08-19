from django.test import TestCase
from django.core.urlresolvers import reverse

# Create your tests here.

class AbstractListTests(TestCase):
    def test_list_view_without_abstracts(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractList'))
        self.assertEqual(response.status_code, 200)