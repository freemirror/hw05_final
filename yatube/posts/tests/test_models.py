from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текстовый пост который больше пятнадцати знаков',
            author=cls.user,
        )

    def test_post_models_have_correct_object_names(self):
        """Проверка метода __str__ у модели Post"""
        post = PostModelTest.post
        correct_model_name = 'Текстовый пост '
        with self.subTest(value=correct_model_name):
            self.assertEqual(
                post.__str__(), correct_model_name)

    def test_group_models_have_correct_object_names(self):
        """Проверка метода __str__ у модели Group"""
        group = PostModelTest.group
        correct_model_name = 'Тестовая группа'
        with self.subTest(value=correct_model_name):
            self.assertEqual(
                group.__str__(), correct_model_name)

    def test_post_models_have_correct_verbose_names(self):
        """Проверка verbose_name у модели Post"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации поста',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_group_models_have_correct_verbose_names(self):
        """Проверка verbose_name у модели Group"""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес для страницы с задачей',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_post_models_have_correct_help_text(self):
        """Проверка help_text у модели Post"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'О чем хотите написать пост',
            'pub_date': 'Измените дату публикации поста',
            'author': 'Выберете автора поста',
            'group': 'Выберете группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_group_models_have_correct_help_text(self):
        """Проверка help_text у модели Group"""
        group = PostModelTest.group
        field_help_text = {
            'title': 'Дайте короткое название группе',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Опишите о чем данная группа',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
