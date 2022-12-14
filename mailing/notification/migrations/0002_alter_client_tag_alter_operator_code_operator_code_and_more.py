# Generated by Django 4.1.4 on 2022-12-12 14:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notification.tag'),
        ),
        migrations.AlterField(
            model_name='operator_code',
            name='operator_code',
            field=models.PositiveSmallIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='tag',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(regex='^[\\d\\w]+$')], verbose_name='Тег'),
        ),
    ]