# Generated by Django 3.0.3 on 2020-04-10 09:33

from django.db import migrations, models
import measure.models


class Migration(migrations.Migration):

    dependencies = [
        ("measure", "0007_auto_20200407_0936"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement",
            name="steps_per_measurment",
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
