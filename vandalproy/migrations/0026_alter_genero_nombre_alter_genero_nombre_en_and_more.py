# Generated by Django 5.2 on 2025-05-23 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vandalproy', '0025_genero_plataforma_remove_juego_ranking_genero_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genero',
            name='nombre',
            field=models.CharField(choices=[('shooter', 'Shooter'), ('aventura', 'Aventura'), ('hack and slash', 'Hack & Slash'), ('rpg', 'RPG'), ('jrpg', 'JRPG'), ('plataformas', 'Plataformas'), ('simulador', 'Simulador'), ('soulslike', 'Soulslike'), ('mundo abierto', 'Mundo Abierto'), ('sandbox', 'Sandbox'), ('por turnos', 'Por turnos'), ('ritmo', 'Ritmo'), ('puzzles', 'Puzzles')], max_length=50),
        ),
        migrations.AlterField(
            model_name='genero',
            name='nombre_en',
            field=models.CharField(choices=[('shooter', 'Shooter'), ('adventure', 'Adventure'), ('hack and slash', 'Hack & Slash'), ('rpg', 'RPG'), ('jrpg', 'JRPG'), ('plataform', 'Plataform'), ('simulator', 'Simulator'), ('soulslike', 'Soulslike'), ('open world', 'Open World'), ('sandbox', 'Sandbox'), ('turn based', 'Turn Based'), ('rythm', 'Rythm'), ('puzzle', 'Puzzle')], max_length=50),
        ),
        migrations.AlterField(
            model_name='plataforma',
            name='nombre',
            field=models.CharField(choices=[('nes', 'NES'), ('super nes', 'Super Nes'), ('playstation', 'PlayStation'), ('gamecube', 'GameCube'), ('xbox', 'Xbox'), ('playstation 2', 'PlayStation 2'), ('wii', 'Wii'), ('xbox 360', 'Xbox 360'), ('playstation 3', 'PlayStation 3'), ('xbox one', 'Xbox One'), ('wii u ', 'Wii U'), ('playstation 4', 'PlayStation 4'), ('xbox series x', 'Xbox Series X'), ('nintendo switch', 'Nintendo Switch'), ('playstation 5', 'PlayStation 5'), ('pc', 'PC')], max_length=50),
        ),
    ]
