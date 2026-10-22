import re

from django.test import Client, TestCase


class AuthorizationTests(TestCase):
    fixtures = ['diary']

    def test_anonymous_redirects(self):
        for url in ['/', '/entries/1/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))

    def test_csrf_and_session(self):
        client = Client(enforce_csrf_checks=True)
        credentials = {'username': 'test_parser_user', 'password': 'testpassword'}
        self.assertEqual(client.post('/login/', credentials).status_code, 403)
        page = client.get('/login/')
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode())[1]
        response = client.post('/login/', {**credentials, 'csrfmiddlewaretoken': token})
        self.assertEqual(response.status_code, 302)
        self.assertIn('sessionid', client.cookies)
        page = client.get('/')
        self.assertContains(page, 'Последние обновления на сайте')
        self.assertContains(page, 'class="card-body"', count=5)
        self.assertEqual(client.get('/entries/1/').status_code, 200)
        self.assertEqual(client.get('/entries/999/').status_code, 404)
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode())[1]
        self.assertEqual(client.post('/logout/', {'csrfmiddlewaretoken': token}).status_code, 302)
        self.assertEqual(client.get('/').status_code, 302)

    def test_original_diary_pages(self):
        self.client.login(username='test_parser_user', password='testpassword')
        count = 0
        for page in range(1, 9):
            response = self.client.get('/', {'page': page})
            self.assertEqual(response.status_code, 200)
            count += response.content.count(b'class="card-body"')
            self.assertNotIn(b'stackpath.bootstrapcdn.com', response.content)
        self.assertEqual(count, 37)
        self.assertContains(self.client.get('/?page=6'), '06 Июл 1854')
        self.assertEqual(self.client.get('/leo/?page=8').status_code, 200)
        self.assertEqual(self.client.get('/?page=999').status_code, 404)
        self.assertEqual(self.client.get('/missing/').status_code, 404)

    def test_wrong_password_does_not_authenticate(self):
        self.client.post('/login/', {'username': 'test_parser_user', 'password': 'wrong'})
        self.assertEqual(self.client.get('/').status_code, 302)


from django.test import SimpleTestCase, override_settings


@override_settings(ROOT_URLCONF='training_blog.public_urls')
class PublicPracticeTests(SimpleTestCase):
    def test_pagination_preserves_all_posts(self):
        count = 0
        for page in range(1, 9):
            response = self.client.get('/', {'page': page})
            self.assertEqual(response.status_code, 200)
            count += response.content.count(b'class="card mb-3 mt-1 shadow-sm"')
            self.assertNotIn(b'stackpath.bootstrapcdn.com', response.content)
        self.assertEqual(count, 71)

    def test_groups_and_unknown_path(self):
        for slug in ['people', 'write', 'party', 'travel']:
            response = self.client.get('/group/' + slug + '/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'group_descr')
            self.assertContains(response, 'posts_count')
        self.assertEqual(self.client.get('/missing/').status_code, 404)

    def test_stylesheet_for_selector_exercise_is_local(self):
        self.assertContains(self.client.get('/'), 'href="/assets/blog.css"')
        response = self.client.get('/assets/blog.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/css')
        self.assertIn(b'body', response.content)
