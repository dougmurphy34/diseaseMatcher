from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from diseaseMatcherApp.views import home_page
from diseaseMatcherApp.models import Abstract
from django.utils import timezone

# Create your tests here.


def create_abstract(abstract_id, title, text):
    #factory pattern to create abstracts for testing
    return Abstract.objects.create(abstract_id=abstract_id, title=title, abstract_text=text, pub_date=timezone.now())

class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_app_root_url_resolves_to_home_page_view(self):
        found = resolve('/diseaseMatcher/')
        self.assertEqual(found.func, home_page)


class AbstractListTests(TestCase):
    def test_list_view_without_abstracts(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractList'))
        self.assertEqual(response.status_code, 200)


class AbstractDetailTests(TestCase):
    def test_detail_view_with_real_pk(self):
        an_abstract = create_abstract(99333, 'This is an abstract.', 'Lots of text here.')
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(an_abstract.pk,)))
        self.assertContains(response, an_abstract.abstract_text, status_code=200)

    """ ERROR HANDLING TO BE IMPLEMENTED:
    def test_detail_view_with_bad_pk(self):
        an_abstract = create_abstract(2934441, 'Abs title', 'Abs text')
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(777777,)))
        self.assertContains(response, "Abstract not found", status_code=200)
    """