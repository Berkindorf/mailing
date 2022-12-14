import pytz

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields.related import ForeignKey

from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):

    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    id = models.AutoField(primary_key=True)
    number = PhoneNumberField(
        unique=True,
        verbose_name='Номер телефона',
    )
    operator_code = models.ForeignKey(
        'Operator_code',
        on_delete=models.CASCADE,
        related_name='clients',
    )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.SET_NULL,
        related_name='clients',
        blank=True, null=True
    )
    timezone = models.CharField(max_length=32, choices=TIMEZONES)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    operator_codes = models.ManyToManyField('Operator_code')
    tags = models.ManyToManyField('Tag')
    text = models.TextField(
        verbose_name='Текст сообщения для для доставки клиенту',
    )
    start_datetime = models.DateTimeField(
        verbose_name='Дата и время запуска рассылки',
    )
    finish_datetime = models.DateTimeField(
        verbose_name='Дата и время окончания рассылки',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def save(self, *args, **kwargs):
        if self.start_datetime >= self.finish_datetime:
            raise ValidationError('Start cannot be later than finish')
        super(Notification, self).save(*args, **kwargs)

    def set_tags(self, tags):
        for id in tags:
            self.tags.add(id)

    def set_operator_codes(self, operator_codes):
        for id in operator_codes:
            self.operator_codes.add(id)


class Operator_code(models.Model):
    id = models.AutoField(primary_key=True)
    operator_code = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Код оператора'
        verbose_name_plural = 'Коды операторов'


class Message(models.Model):

    SENT_CHOICES = [
        (False, 'Не отправлено'),
        (True, 'Отправлено'),
    ]

    id = models.AutoField(primary_key=True)
    notification = ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Рассылка',
    )
    client = ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Клиент',
    )
    created = models.DateTimeField(
        verbose_name='Дата и время создания (отправки)',
    )
    status = models.BooleanField(
        choices=SENT_CHOICES,
        default=False,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.CharField(
        max_length=100,
        unique=True,
        validators=[RegexValidator(regex=r'^[\d\w]+$')],
        verbose_name='Тег',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
