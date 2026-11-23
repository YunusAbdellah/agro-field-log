from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class FieldPlot(models.Model):
    SOIL_CHOICES = [
        ("Lehm", "Lehm (Loam)"),
        ("Sand", "Sand (Sandy)"),
        ("Ton", "Ton (Clay)"),
        ("Schluff", "Schluff (Silt)"),
        ("Mischboden", "Mischboden (Mixed)"),
    ]

    name = models.CharField(max_length=120)
    area_ha = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    soil_type = models.CharField(max_length=40, choices=SOIL_CHOICES, default="Lehm")
    current_crop = models.CharField(max_length=120)
    season_year = models.IntegerField(default=2026)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, default=Decimal("50.07200"))
    longitude = models.DecimalField(max_digits=8, decimal_places=5, default=Decimal("8.48700"))
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.current_crop}, {self.area_ha} ha)"


class FieldActivity(models.Model):
    ACTIVITY_TYPES = [
        ("sowing", "Sowing / Aussaat"),
        ("fertilization", "Fertilization / Düngung"),
        ("crop_protection", "Crop Protection / Pflanzenschutz"),
        ("irrigation", "Irrigation / Bewässerung"),
        ("harvest", "Harvest / Ernte"),
        ("soil_check", "Soil Check / Bodenprobe"),
    ]

    UNIT_CHOICES = [
        ("kg/ha", "kg/ha"),
        ("L/ha", "L/ha"),
        ("mm", "mm"),
        ("t/ha", "t/ha"),
        ("unit", "unit"),
    ]

    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_type = models.CharField(max_length=32, choices=ACTIVITY_TYPES)
    activity_date = models.DateField(default=timezone.localdate)
    product_or_input = models.CharField(max_length=160)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    unit = models.CharField(max_length=16, choices=UNIT_CHOICES, default="kg/ha")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_date", "-id"]

    def __str__(self):
        return f"{self.plot.name} - {self.get_activity_type_display()} ({self.activity_date})"


class AlertRule(models.Model):
    RULE_TYPES = [
        ("high_input_rate", "High Single Input Rate"),
        ("inactivity_days", "Plot Inactivity (Days)"),
        ("rain_before_fieldwork", "Rain Forecast Before Fieldwork"),
    ]

    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="alert_rules",
        null=True,
        blank=True,
    )
    rule_type = models.CharField(max_length=40, choices=RULE_TYPES)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        scope = self.plot.name if self.plot else "Global"
        return f"[{scope}] {self.rule_type} >= {self.threshold_value}"


class FieldAlert(models.Model):
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    rule_type = models.CharField(max_length=40)
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default="warning")
    message = models.CharField(max_length=280)
    is_resolved = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["is_resolved", "-triggered_at"]

    def __str__(self):
        status = "Resolved" if self.is_resolved else "Open"
        return f"[{status}] {self.plot.name}: {self.message}"
