# Generated by Django 3.0.3 on 2020-04-07 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("measure", "0006_auto_20200405_1616"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement", name="description", field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="measurement",
            name="name",
            field=models.CharField(default="test", max_length=100),
            preserve_default=False,
        ),
    ]