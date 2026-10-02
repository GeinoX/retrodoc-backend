from django.db import migrations

CATEGORIES = [
    ("identity", "Identity", "Identité"),
    ("academic", "Academic", "Académique"),
    ("corporate", "Corporate and business", "Entreprise et affaires"),
    ("financial", "Financial and banking", "Finance et banque"),
    ("vehicle-travel", "Vehicle and travel", "Véhicule et voyage"),
    ("medical", "Medical", "Médical"),
    ("legal-property", "Legal and property", "Juridique et propriété"),
    ("other", "Other", "Autre"),
]


def seed(apps, schema_editor):
    Category = apps.get_model("documents", "DocumentCategory")
    for order, (code, en, fr) in enumerate(CATEGORIES):
        Category.objects.get_or_create(
            code=code, defaults={"name_en": en, "name_fr": fr, "display_order": order}
        )


class Migration(migrations.Migration):
    dependencies = [("documents", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]