from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from diseaseMatcherApp.views import home_page
from diseaseMatcherApp.models import Abstract, Annotator, Matches
from django.utils import timezone
#Turn this on when I start integration tests:
#from django.test.client import Client

"""
Core testing principle:
for every class and standalone method of your application there should exist a unit test,
and for every view or page in your application there should exist an integration test.

- See more at: http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/#sthash.byci2VYz.dpuf

"""


# Create your tests here.


def create_abstract(abstract_id, title, text):
    #factory pattern to create abstracts for testing
    return Abstract.objects.create(abstract_id=abstract_id, title=title, abstract_text=text, pub_date=timezone.now())


def create_match(abstract, annotator, text, length, offset):
    return Matches.objects.create(abstract=abstract, annotator=annotator, text_matched=text,match_length=length, match_offset=offset)

def create_annotator(username):
    return Annotator.objects.create(username=username, last_entry_date=timezone.now())

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

    def test_detail_view_with_bad_pk(self):
        #Is there a way to make this a pretty error message, instead of a 404?  Seems impossible when passing args
        an_abstract = create_abstract(2934441, 'Abs title', 'Abs text')
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_post_one_disease_entered(self):
        #TODO: This test is throwing a 405.  I need to learn something about POSTS in django (doesn't appear to be a csrf problem)
        an_abstract = create_abstract(44,'My abstract title','My abstract text')
        an_annotator = create_annotator('Josephus')
        resp = self.client.post('/diseaseMatcher/224/detail/', {'userInput': '', 'inputSoFar': "Gout", 'abstract_pk': an_abstract.pk, 'csrfmiddlewaretoken': 'p4kklc5RDt1ngTcCgERNEofAcvqeSSh9'})
        #self.assertEqual(resp.status_code, 302)  ##code 302 is a redirect
        #self.assertTrue(resp.POST)

class PlayAgainPageTest(TestCase):
    def confirm_url_resolves(self):
        resp = self.client.get('/playAgain/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('abstract_choice' in resp.context)
