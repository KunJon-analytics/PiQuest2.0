from __future__ import unicode_literals
import re
import json

from django.db import models
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify
from django.conf import settings



class Category(models.Model):

    category = models.CharField(
        verbose_name=_("Category"),
        max_length=31, blank=True,
        unique=True, null=True)

    slug = models.SlugField(
        max_length=31, blank=False, unique=True,
        help_text=_("a user friendly url"),
        verbose_name=_("user friendly url"))

    description = models.TextField()

    image = models.ImageField(
        default='category_default.jpg', upload_to='category_pic')

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['category']

    def __str__(self):
        return self.category




class SubCategory(models.Model):

    sub_category = models.CharField(
        verbose_name=_("Sub-Category"),
        max_length=31, blank=True, null=True, unique=True)

    category = models.ForeignKey(
        Category, null=True, blank=True,
        verbose_name=_("Category"), on_delete=models.CASCADE)

    slug = models.SlugField(
        max_length=31, blank=False, unique=True,
        help_text=_("a user friendly url"),
        verbose_name=_("user friendly url"))

    class Meta:
        verbose_name = _("Sub-Category")
        verbose_name_plural = _("Sub-Categories")
        ordering = ['sub_category']

    def __str__(self):
        return self.sub_category.title() + " (" + self.category.category.title() + ")"


class Quiz(models.Model):

    title = models.CharField(
        verbose_name=_("Title"), unique=True,
        max_length=60, blank=False)

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True, help_text=_("a description of the quiz"))

    master = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='quizzes', on_delete=models.CASCADE)

    image = models.ImageField(default='quiz_default.jpg', upload_to='quiz_pic')

    reward = models.FloatField(null=True, blank=True)

    number_of_winners = models.IntegerField(null=True, blank=True)

    url = models.SlugField(
        max_length=60, blank=False,
        help_text=_("a user friendly url"),
        verbose_name=_("user friendly url"))

    pub_date = models.DateField('date created', auto_now_add=True)

    category = models.ForeignKey(
        Category, null=True, blank=True,
        verbose_name=_("Category"), on_delete=models.CASCADE)

    tags = models.ManyToManyField(Category, blank=True, related_name='quizzes')

    projects = models.ManyToManyField(
        'projects.Project', blank=True, related_name='quizzes')

    random_order = models.BooleanField(
        blank=False, default=False,
        verbose_name=_("Random Order"),
        help_text=_("Display the questions in "
                    "a random order or as they "
                    "are set?"))

    max_questions = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("Max Questions"),
        help_text=_("Number of questions to be answered on each attempt."))

    answers_at_end = models.BooleanField(
        blank=False, default=False,
        help_text=_("Correct answer is NOT shown after question."
                    " Answers displayed at the end."),
        verbose_name=_("Answers at end"))

    exam_paper = models.BooleanField(
        blank=False, default=False,
        help_text=_("If yes, the result of each"
                    " attempt by a user will be"
                    " stored. Necessary for marking."),
        verbose_name=_("Exam Paper"))

    single_attempt = models.BooleanField(
        blank=False, default=False,
        help_text=_("If yes, only one attempt by"
                    " a user will be permitted."
                    " Non users cannot sit this exam."),
        verbose_name=_("Single Attempt"))

    pass_mark = models.SmallIntegerField(
        blank=True, default=0,
        verbose_name=_("Pass Mark"),
        help_text=_("Percentage required to pass exam."),
        validators=[MaxValueValidator(100), MinValueValidator(1)])

    success_text = models.TextField(
        blank=True, help_text=_("Displayed if user passes."),
        verbose_name=_("Success Text"))

    fail_text = models.TextField(
        verbose_name=_("Fail Text"),
        blank=True, help_text=_("Displayed if user fails."))

    draft = models.BooleanField(
        blank=True, default=True,
        verbose_name=_("Draft"),
        help_text=_("If yes, the quiz is not displayed"
                    " in the quiz list and can only be"
                    " taken by users who can edit"
                    " quizzes."))

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")
        ordering = ['-pub_date', 'title']
        get_latest_by = 'pub_date'

    def __str__(self):
        return "{} on {}" .format(self.title, self.pub_date.strftime('%Y-%M-%D'))


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting a quiz.
    Replaces the session system used by anon users.

    Question_order is a list of integer pks of all the questions in the
    quiz, in order.

    Question_list is a list of integers which represent id's of
    the unanswered questions in csv format.

    Incorrect_questions is a list in the same format.

    Sitting deleted when quiz finished unless quiz.exam_paper is true.

    User_answers is a json object in which the question PK is stored
    with the answer the user gave.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sittings',
                             verbose_name=_("User"), on_delete=models.CASCADE)

    quiz = models.ForeignKey(Quiz, verbose_name=_(
        "Quiz"), on_delete=models.CASCADE)

    question_order = models.CharField(
        max_length=1024,
        verbose_name=_("Question Order"),
        validators=[validate_comma_separated_integer_list])

    question_list = models.CharField(
        max_length=1024,
        verbose_name=_("Question List"),
        validators=[validate_comma_separated_integer_list])

    incorrect_questions = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name=_("Incorrect questions"),
        validators=[validate_comma_separated_integer_list])

    current_score = models.IntegerField(verbose_name=_("Current Score"))

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name=_("Complete"))

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name=_("User Answers"))

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name=_("Start"))

    end = models.DateTimeField(null=True, blank=True, verbose_name=_("End"))


class Winner(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    claimed = models.BooleanField(default=False)
    wallet_address = models.CharField(max_length=35, blank=True, null=True)
    recipient = models.CharField(max_length=35, blank=True, null=True)
    amount = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.user)
