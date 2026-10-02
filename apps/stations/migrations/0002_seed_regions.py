from django.db import migrations

REGIONS = [
    ("Adamawa", "Adamaoua"), ("Centre", "Centre"), ("East", "Est"),
    ("Far North", "Extrême-Nord"), ("Littoral", "Littoral"), ("North", "Nord"),
    ("North-West", "Nord-Ouest"), ("West", "Ouest"), ("South", "Sud"),
    ("South-West", "Sud-Ouest"),
]


def seed(apps, schema_editor):
    Region = apps.get_model("stations", "Region")
    for en, fr in REGIONS:
        Region.objects.get_or_create(name_en=en, defaults={"name_fr": fr})


class Migration(migrations.Migration):
    dependencies = [("stations", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]