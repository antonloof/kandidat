# Generated by Django 3.0.3 on 2020-04-04 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("measure", "0003_auto_20200404_1322"),
    ]

    operations = [
        migrations.RenameField(model_name="measurment", old_name="b", new_name="amplitude",),
        migrations.RenameField(model_name="measurment", old_name="c", new_name="angle_freq",),
        migrations.RenameField(model_name="measurment", old_name="d", new_name="offset",),
        migrations.RemoveField(model_name="measurment", name="a",),
        migrations.AddField(
            model_name="measurment", name="phase", field=models.FloatField(null=True),
        ),
    ]
