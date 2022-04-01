from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Дайте короткое название группе'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес для страницы с задачей',
        help_text=('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания')
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Опишите о чем данная группа'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='О чем хотите написать пост'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации поста',
        help_text='Измените дату публикации поста',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        help_text='Выберете автора поста',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Выберете группу',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='О чем хотите написать комментарий'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        help_text='Выберете автора комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        help_text='Выберете пост',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
        help_text='Измените дату публикации комментария',
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        help_text='Выберете пользователя',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Выберете автора',
        on_delete=models.CASCADE,
        related_name='following',
    )
