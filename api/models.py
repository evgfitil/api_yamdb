from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(
        max_length=30,
        unique=True
    )


class Genre(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(
        max_length=30,
        unique=True
    )


class Title(models.Model):
    name = models.CharField(max_length=90)
    year = models.IntegerField()
    description = models.TextField(
        max_length=200,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='categories'
    )


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    email = models.EmailField(_('email address'), blank=False, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        )
    confirmation_code = models.CharField(max_length=100, blank=True, )

    def __str__(self):
        return self.username


class Review(models.Model):
    SCORE_CHOICES = zip(range(1, 11), range(1, 11))
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(choices=SCORE_CHOICES, default=1)
    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True,
    )


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации комментария',
        auto_now_add=True
    )
