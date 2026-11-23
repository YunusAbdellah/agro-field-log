from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from agro.models import AlertRule, FieldActivity, FieldAlert, FieldPlot


class Command(BaseCommand):
    help = "Seeds realistic agricultural plots, field activities, rules, and sample alerts."

    def handle(self, *args, **options):
        if FieldPlot.objects.exists():
            self.stdout.write(self.style.SUCCESS("Demo data already present; skipping."))
            return

        today = timezone.localdate()

        nord = FieldPlot.objects.create(
            name="Schlag Nord (Main-Taunus)",
            area_ha=Decimal("14.50"),
            soil_type="Lehm",
            current_crop="Winterweizen",
            season_year=2026,
            latitude=Decimal("50.07200"),
            longitude=Decimal("8.48700"),
            notes="Well-drained loam plot near Hattersheim; monitor nitrogen split applications.",
        )
        sued = FieldPlot.objects.create(
            name="Schlag Süd (Rhein-Main)",
            area_ha=Decimal("9.20"),
            soil_type="Sand",
            current_crop="Silomais",
            season_year=2026,
            latitude=Decimal("50.05500"),
            longitude=Decimal("8.46000"),
            notes="Lighter sandy soil; higher irrigation sensitivity during dry spells.",
        )
        ost = FieldPlot.objects.create(
            name="Schlag Ost (Talblick)",
            area_ha=Decimal("11.80"),
            soil_type="Ton",
            current_crop="Winterraps",
            season_year=2026,
            latitude=Decimal("50.09100"),
            longitude=Decimal("8.51200"),
            notes="Clay-rich plot; avoid heavy machinery right after heavy rain.",
        )

        AlertRule.objects.create(
            rule_type="high_input_rate",
            threshold_value=Decimal("180.00"),
            is_active=True,
        )
        AlertRule.objects.create(
            rule_type="inactivity_days",
            threshold_value=Decimal("21.00"),
            is_active=True,
        )

        FieldActivity.objects.create(
            plot=nord,
            activity_type="sowing",
            activity_date=today - timedelta(days=45),
            product_or_input="Winterweizen Saatgut (Qualitätssaatgut)",
            quantity=Decimal("165.00"),
            unit="kg/ha",
            notes="Clean seedbed preparation prior to sowing.",
        )
        FieldActivity.objects.create(
            plot=nord,
            activity_type="fertilization",
            activity_date=today - timedelta(days=12),
            product_or_input="KAS 27 (Kalkammonsalpeter)",
            quantity=Decimal("120.00"),
            unit="kg/ha",
            notes="First spring nitrogen top-dressing.",
        )
        FieldActivity.objects.create(
            plot=sued,
            activity_type="irrigation",
            activity_date=today - timedelta(days=6),
            product_or_input="Tropfbewässerung Sektor A",
            quantity=Decimal("25.00"),
            unit="mm",
            notes="Targeted moisture support on sandy patch.",
        )
        FieldActivity.objects.create(
            plot=ost,
            activity_type="soil_check",
            activity_date=today - timedelta(days=34),
            product_or_input="Nmin & pH Bodenprobe",
            quantity=Decimal("1.00"),
            unit="unit",
            notes="Baseline soil mineral nitrogen check.",
        )

        FieldAlert.objects.create(
            plot=ost,
            rule_type="inactivity_days",
            severity="warning",
            message="No field activity logged for 34 days (limit: 21 days).",
        )

        self.stdout.write(self.style.SUCCESS("Seeded AgroLog demo data successfully."))
