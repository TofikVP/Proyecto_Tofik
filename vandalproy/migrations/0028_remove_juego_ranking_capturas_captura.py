# Generated by Django 5.2 on 2025-05-23 10:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vandalproy', '0027_alter_genero_nombre_alter_genero_nombre_en_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='juego_ranking',
            name='capturas',
        ),
        migrations.CreateModel(
            name='Captura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='juegos_ranking/capturas/')),
                ('descripcion', models.CharField(blank=True, max_length=200)),
                ('juego', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='capturas', to='vandalproy.juego_ranking')),
            ],
        ),
    ]
