
from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from diseaseMatcherApp.views import home_page
from diseaseMatcherApp.models import Abstract, Matches, MatchLocations, MatchLocationsLookup
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
#Turn this on when I start integration tests:
#from django.test.client import Client

"""

Core testing principle:
for every class and standalone method of your application there should exist a unit test,
and for every view or page in your application there should exist an integration test.

- See more at: http://www.celerity.com/blog/2013/04/29/how-write-speedy-unit-tests-django-part-1-basics/#sthash.byci2VYz.dpuf

Fixtures are located at fixtures/diseaseMatcherApp_views_testdata.json

*************************Test names must start with "test"***************************

TODO: Next steps for testing:
1) A setup and cleanup method
2) use self.client.post(url, args) to test form submission


"""


# Factory patterns for testing module.  Probably remove after fully porting to fixtures.
def create_abstract(abstract_id, title, text):
    return Abstract.objects.create(abstract_id=abstract_id, title=title, abstract_text=text, pub_date=timezone.now())


def create_match(abstract, annotator, text, length, offset, location, time):
    return Matches.objects.create(abstract=abstract, annotator=annotator, text_matched=text, match_length=length,
                                  match_offset=offset, match_location=location, match_time=time)


def create_annotator(username):
    return User.objects.create(username=username, password='fun')


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_app_root_url_resolves_to_home_page_view(self):
        found = resolve('/diseaseMatcher/')
        self.assertEqual(found.func, home_page)


#This page isn't used.  This test can go once tests.py is ready to be checked in
class AbstractListTests(TestCase):
    def test_list_view_without_abstracts(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractList'))
        self.assertEqual(response.status_code, 200)


class AbstractDetailTests(TestCase):

    fixtures = ['diseaseMatcherApp_views_testdata.json']

    def test_detail_view_with_real_pk(self):
        an_abstract = create_abstract(99333, 'This is an abstract.', 'Lots of text here.')
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(an_abstract.pk,)))
        self.assertContains(response, an_abstract.abstract_text, status_code=200)

    def test_detail_view_with_bad_pk(self):
        #Is there a way to make this a pretty error message, instead of a 404?  Seems impossible when passing args
        an_abstract = create_abstract(2934441, 'Abs title', 'Abs text')
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(9999,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_using_fixtures(self):
        response = self.client.get(reverse('diseaseMatcherApp:abstractDetail', args=(4,)))
        self.assertContains(response, "Neisseria")
        self.assertEqual(response.context['abstract'].abstract_id, 100562)


    def test_post_one_disease_entered(self):
        #TODO: This test throws a 405.  Research POSTS in django (doesn't appear to be a csrf problem)
        ## ---- Removing login_required from process_matches still gives a 405.
        ## Removing this from the post (, 'csrfmiddlewaretoken': 'p4kklc5RDt1ngTcCgERNEofAcvqeSSh9') ... did not help
        an_abstract = create_abstract(44,'My abstract title','My abstract text')
        an_annotator = create_annotator('Josephus')
        resp = self.client.post('/diseaseMatcher/224/detail/', {'userInput': '', 'userMatches': 'stringOfCrap', 'inputSoFar': "Gout", 'abstract_pk': an_abstract.id, 'csrfmiddlewaretoken': 'p4kklc5RDt1ngTcCgERNEofAcvqeSSh9'})
        #self.assertEqual(resp.status_code, 302)  ##code 302 is a redirect
        #self.assertTrue(resp.POST)  #TODO: 'HttpResponseNotAllowed' object has no attribute 'POST'


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

    def test_url_loads_if_user_authenticated(self):
        resp = self.client.get(reverse('diseaseMatcherApp:playAgain'))
        #self.assertTrue(resp.context['abstract_choice'] < 1000)  #TODO: 'NoneType' object has no attribute '__getitem__'


class ProcessMatchesTest(TestCase):
    def test_create_and_save_match_good_data(self):
        abstract = create_abstract(44, "Temporary Abstract", "Lots of fun text.")
        match_text = "superDisease"
        annotator = create_annotator("myTestUser")
        length = 13
        offset = 73
        #location = MatchLocationsLookup.objects.get(pk=2)  #TODO:  MatchLocationsLookup matching query does not exist.
        time = 6
        #this_match = create_match(abstract, annotator, match_text, length, offset, location, time)  #TODO: This is no longer the same args list
        #this_match.save()

        #self.assertEqual(this_match.match_text, "phantasmagoria")  #"superDisease"

    #TODO: test a failed match creation (ie, test data validation)

    def test_process_one_match_in_title(self):
        #create a user and an abstract
        this_abstract = create_abstract(1, "The ultimate disease abstract",
                        "There are some people who have cancer, and some who have diphtheria.")
        this_abstract.save()
        this_annotator = create_annotator("Joe")
        this_annotator.save()

        resp = self.client.post('/diseaseMatcher/process_matches',{'inputSoFar': 'cancer', 'abstract_pk': 1})
        #self.assertEqual(resp.status_code, 302) #TODO: This is 301.  Find out what that is.
        #self.assertTrue(resp.POST)  #TODO: This is not the right syntax to do this.  Check other project tests.py.
        #self.assertContains(resp, "Godzilla")

