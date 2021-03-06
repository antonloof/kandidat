# Generated by Django 3.0.3 on 2020-04-05 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("measure", "0004_auto_20200404_1343"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurment",
            name="connection_1",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="measurment",
            name="connection_2",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="measurment",
            name="connection_3",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="measurment",
            name="connection_4",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="measurment",
            name="current_limit",
            field=models.FloatField(default=0.0001),
            preserve_default=False,
        ),
    ]
