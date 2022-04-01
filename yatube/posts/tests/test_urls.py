from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.author = User.objects.create_user(username='freemirror')
        cls.post = Post.objects.create(
            text='Текстовый пост',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group_slug',
            description='Тестовое описание',
        )
        cls.templates_url_names_guest = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{cls.group.slug}/',
            'posts/profile.html': f'/profile/{cls.user.username}/',
            'posts/post_detail.html': f'/posts/{cls.post.pk}/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_posts_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        for url in self.templates_url_names_guest.values():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_unexistent(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexistent/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url_exists_at_desired_location_for_author_only(self):
        """Страница 'posts/<int:post_id>/edit/ доступна
        автору поста."""
        response = self.author_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_url_redirect_anonymous(self):
        """Страница /posts/1/edit/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_url_redirect_no_author_user(self):
        """Страница /posts/1/edit/ перенаправляет не автора поста."""
        response = self.authorized_client.get(f'/posts/{self.post.pk}'
                                              f'/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_user_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон для
        не авторизованного пользователя."""
        for template, url in self.templates_url_names_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_auth_user_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        для авторизованного пользователя."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_author_post_user_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон для автора
        поста пользователя."""
        response = self.author_client.get(f'/posts/{self.post.pk}'
                                          f'/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
