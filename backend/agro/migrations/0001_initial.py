from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FieldPlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("area_ha", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("soil_type", models.CharField(choices=[("Lehm", "Lehm (Loam)"), ("Sand", "Sand (Sandy)"), ("Ton", "Ton (Clay)"), ("Schluff", "Schluff (Silt)"), ("Mischboden", "Mischboden (Mixed)")], default="Lehm", max_length=40)),
                ("current_crop", models.CharField(max_length=120)),
                ("season_year", models.IntegerField(default=2026)),
                ("latitude", models.DecimalField(decimal_places=5, default=Decimal("50.07200"), max_digits=8)),
                ("longitude", models.DecimalField(decimal_places=5, default=Decimal("8.48700"), max_digits=8)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="FieldActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_type", models.CharField(choices=[("sowing", "Sowing / Aussaat"), ("fertilization", "Fertilization / Düngung"), ("crop_protection", "Crop Protection / Pflanzenschutz"), ("irrigation", "Irrigation / Bewässerung"), ("harvest", "Harvest / Ernte"), ("soil_check", "Soil Check / Bodenprobe")], max_length=32)),
                ("activity_date", models.DateField(default=django.utils.timezone.localdate)),
                ("product_or_input", models.CharField(max_length=160)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("unit", models.CharField(choices=[("kg/ha", "kg/ha"), ("L/ha", "L/ha"), ("mm", "mm"), ("t/ha", "t/ha"), ("unit", "unit")], default="kg/ha", max_length=16)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activities", to="agro.fieldplot")),
            ],
            options={
                "ordering": ["-activity_date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="AlertRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rule_type", models.CharField(choices=[("high_input_rate", "High Single Input Rate"), ("inactivity_days", "Plot Inactivity (Days)"), ("rain_before_fieldwork", "Rain Forecast Before Fieldwork")], max_length=40)),
                ("threshold_value", models.DecimalField(decimal_places=2, max_digits=10)),
                ("is_active", models.BooleanField(default=True)),
                ("plot", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="alert_rules", to="agro.fieldplot")),
            ],
        ),
        migrations.CreateModel(
            name="FieldAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rule_type", models.CharField(max_length=40)),
                ("severity", models.CharField(choices=[("info", "Info"), ("warning", "Warning"), ("critical", "Critical")], default="warning", max_length=16)),
                ("message", models.CharField(max_length=280)),
                ("is_resolved", models.BooleanField(default=False)),
                ("triggered_at", models.DateTimeField(auto_now_add=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("plot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="agro.fieldplot")),
            ],
            options={
                "ordering": ["is_resolved", "-triggered_at"],
            },
        ),
    ]
