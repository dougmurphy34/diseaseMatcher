from __future__ import absolute_import

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .views import home_page
from .models import Abstract, Matches, MatchLocations, Annotator

"""

Core testing principle:
for every class and standalone method of your application there should exist a unit test,
and for every view or page in your application there should exist an integration test.

- See more at: http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/#sthash.byci2VYz.dpuf

Fixtures are located at fixtures/diseaseMatcherApp_views_testdata.json
Users are not in fixture (because not in diseaseMatcherApp but django.contrib.auth) and must be created manually for testing

*************************Test names must start with "test"***************************

From Pycharm context menu, select "Run tests.py with coverage" to see how much of the app code is getting tested.

"""


# Factory pattern for testing module.
def create_annotator(username):
    return Annotator.objects.create(username=username, password='fun')


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_app_root_url_resolves_to_home_page_view(self):
        found = resolve('/diseaseMatcher/')
        self.assertEqual(found.func, home_page)


class AbstractDetailTests(TestCase):

    fixtures = ['diseaseMatcherApp_views_testdata.json']

    def test_detail_view_with_real_pk(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(20,)))
        self.assertContains(response, 'hyperparathyroidism', status_code=200)

    def test_detail_view_with_bad_pk(self):
        #Is there a way to make this a pretty error message, instead of a 404?  Seems impossible when passing args
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_using_fixtures(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(4,)))
        self.assertContains(response, "Kniest")
        self.assertEqual(response.context['abstract'].abstract_id, 9066888)

    def test_post_one_disease_entered(self):
        #TODO: the server is refusing self.client.post requests in testing, although they work in the app proper.  Why?
        ## ---- Removing login_required from process_matches still gives a 405.
        ## Removing this from the post (, 'csrfmiddlewaretoken': 'p4kklc5RDt1ngTcCgERNEofAcvqeSSh9')
                # since django's test web server turns off csrf by default
        an_abstract = Abstract.objects.get(pk=44)
        an_annotator = create_annotator('Josephus')
        an_annotator.save()

        textContainingJSONMatches = "{'fragile X syndrome': 6, 'FMR1': 18}"

        resp = self.client.post(reverse('diseaseMatcherApp:abstractDetail', kwargs={'pk': 44}),
                                {'userInput': '', 'userMatches': textContainingJSONMatches, 'inputSoFar': "Gout",
                                 'abstract_pk': an_abstract.id})
        #self.assertEqual(resp.status_code, 302)  ##code 302 is a redirect


class LoginTests(TestCase):
    def test_can_post_login_information(self):
        response = self.client.post(reverse('login'), {'username': 'dog', 'password': 'cat'})
        self.assertEqual(response.status_code, 200)

    def test_login_works_with_correct_info(self):
        my_user = create_annotator('this_guy')  #factory method always uses password 'fun'
        my_user.save()

        #this logs the user in
        response = self.client.post(reverse('login'), {'username': 'this_guy', 'password': 'fun'})

        #this page requires login and should return 200 when logged in but redirect with 302 when not
        response2 = self.client.get(reverse('diseaseMatcherApp:playAgain'))
        #self.assertEqual(response2.status_code, 200)  #TODO: This is redirecting, which seems wrong


class PlayAgainPageTest(TestCase):
    def test_confirm_url_requires_login(self):
        resp = self.client.get(reverse('diseaseMatcherApp:playAgain'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/accounts/login/?next=/diseaseMatcher/play_again/')

    def test_url_loads_if_user_authenticated(self):
        resp = self.client.get(reverse('diseaseMatcherApp:playAgain'))
        #self.assertTrue(resp.context['abstract_choice'] < 1000)  #TODO: 'NoneType' object has no attribute '__getitem__'


class ProcessMatchesTest(TestCase):
    fixtures = ['diseaseMatcherApp_views_testdata.json']

    def test_manual_create_and_save_match_good_data(self):
        an_abstract = Abstract.objects.get(pk=88)  #Text in title: "TP53"
        self.assertRegexpMatches(an_abstract.title, 'Duarte')
        match_text = "TP53"
        annotator = create_annotator("myTestUser")
        length = 13
        offset = 73
        location = 2
        time = 6
        this_match = Matches.objects.create(abstract=an_abstract, annotator=annotator, text_matched=match_text,
                                            match_length=length, match_time=time, gold_standard_match=None)
        this_match.save()
        this_location = MatchLocations.objects.create(match=this_match, match_location=location, match_offset=offset)
        this_location.save()

        #self.assertEqual(this_match.match_text, "phantasmagoria")  #"superDisease"

    #TODO: test a failed match creation (ie, test data validation)

    def test_process_one_match_in_title(self):
        #TODO: the server is refusing self.client.post requests in testing, although they work in the app proper.  Why?

        #create a user and an abstract
        this_abstract = Abstract.objects.get(pk=5)  #'hypoplasia' in both title and abstract text
        this_annotator = create_annotator("Joe")
        this_annotator.save()

        userMatchesJSON = "{'hypoplasia': 8}"

        resp = self.client.post(reverse('diseaseMatcherApp:abstractDetail', kwargs={'pk': this_abstract.id}),
                                {'inputSoFar': 'hypoplasia', 'abstract_pk': this_abstract.id, 'user.id': this_annotator.id,
                                 'userMatches': userMatchesJSON})
        #self.assertEqual(resp.status_code, 302)
        #self.assertEqual(Matches.objects.get(pk=1).text_matched, 'hypoplasia')
        #self.assertContains(resp, "again")

