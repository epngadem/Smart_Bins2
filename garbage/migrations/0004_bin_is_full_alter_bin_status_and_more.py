# Generated by Django 5.1.2 on 2024-11-13 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garbage', '0003_delete_bindata'),
    ]

    operations = [
        migrations.AddField(
            model_name='bin',
            name='is_full',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bin',
            name='status',
            field=models.CharField(blank=True, default='Empty', max_length=50),
        ),
        migrations.AlterField(
            model_name='datacollection',
            name='signal_strength',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
