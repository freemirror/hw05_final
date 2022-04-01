import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='freemirror')

        cls.group = Group.objects.create(
            title='Погода',
            slug='group_slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.group_without_posts = Group.objects.create(
            title='Ветра',
            slug='group2_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текстовый пост',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,

        )
        cls.urls_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Страницы используют правильные шаблоны."""
        for reverse_name, template in self.urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(first_post.image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(group, self.group)
        self.assertEqual(first_post.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_post = response.context['page_obj'][0]
        user = response.context['user']
        self.assertEqual(first_post.text, 'Текстовый пост')
        self.assertEqual(first_post.group, self.post.group)
        self.assertEqual(first_post.author, self.post.author)
        self.assertEqual(user, self.user)
        self.assertEqual(first_post.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        post = response.context['posts']
        self.assertEqual(post.text, 'Текстовый пост')
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pk, self.post.pk)
        self.assertEqual(post.image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_not_included_into_anotger_group(self):
        """Пост с группой 'Погода' не попал в группу 'Ветра'"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_without_posts.slug}
            )
        )
        self.assertEqual(response.context.get('post'), None)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context['is_edit'])


class PaginatorViewsTest(TestCase):
    first_page_posts = 10
    second_page_posts = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Природа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый_пост ' + str(i),
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_ten_posts(self):
        """На первой странице index должно быть 10 постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_index_page_three_posts(self):
        """На второй странице index должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)

    def test_first_group_list_page_ten_posts(self):
        """На первой странице group_list должно быть 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_group_list_page_three_posts(self):
        """На второй странице group_list должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)

    def test_first_profile_page_ten_posts(self):
        """На первой странице profile должно быть 10 постов"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.first_page_posts)

    def test_second_profile_page_three_posts(self):
        """На второй странице profile должно быть 3 поста"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2')
        self.assertEqual(response.context['page_obj'].end_index(),
                         self.second_page_posts)


class PostСacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки кеша',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_has_been_created(self):
        """После удаления записи в БД, данные доступны на странице
        до очистки кеша."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.content
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост для проверки кеша'
            ).exists()
        )
        self.post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        caсhed_post = response.content
        self.assertEqual(post, caсhed_post)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        claeaned_caсhed_post = response.content
        self.assertNotEqual(post, claeaned_caсhed_post)


class FollowPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.author = User.objects.create_user(username='test_author')
        cls.not_follower = User.objects.create_user(
            username='test_another_author',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост для проверки подписок',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

    def test_follow_and_unfollow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок."""
        follow_count = Follow.objects.count()
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.not_follower.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.not_follower.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_following_posts(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)
        response = self.not_follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.context.get('post'), None)
