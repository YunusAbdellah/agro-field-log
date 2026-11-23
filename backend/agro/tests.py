from datetime import timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from agro.models import FieldActivity, FieldAlert, FieldPlot
from agro.services.alert_engine import evaluate_inactivity_alerts


class AgroLogAPITests(APITestCase):
    def setUp(self):
        self.plot = FieldPlot.objects.create(
            name="Testschlag Nord",
            area_ha=Decimal("10.00"),
            soil_type="Lehm",
            current_crop="Winterweizen",
            season_year=2026,
        )

    def test_create_plot_and_list(self):
        url = reverse("plot-list")
        payload = {
            "name": "Testschlag Süd",
            "area_ha": "6.50",
            "soil_type": "Sand",
            "current_crop": "Sommergerste",
            "season_year": 2026,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FieldPlot.objects.count(), 2)

    def test_high_input_triggers_alert(self):
        url = reverse("activity-list")
        payload = {
            "plot": self.plot.id,
            "activity_type": "fertilization",
            "activity_date": "2026-04-15",
            "product_or_input": "NPK Dünger",
            "quantity": "240.00",
            "unit": "kg/ha",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            FieldAlert.objects.filter(plot=self.plot, rule_type="high_input_rate", is_resolved=False).exists()
        )

    def test_plot_summary_endpoint(self):
        FieldActivity.objects.create(
            plot=self.plot,
            activity_type="fertilization",
            activity_date="2026-04-10",
            product_or_input="KAS 27",
            quantity="90.00",
            unit="kg/ha",
        )
        FieldActivity.objects.create(
            plot=self.plot,
            activity_type="fertilization",
            activity_date="2026-04-20",
            product_or_input="KAS 27",
            quantity="60.00",
            unit="kg/ha",
        )
        url = reverse("plot-summary", args=[self.plot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_activities"], 2)
        self.assertEqual(response.data["totals_by_unit"]["kg/ha"], 150.0)

    def test_inactivity_alert_and_resolve(self):
        FieldActivity.objects.create(
            plot=self.plot,
            activity_type="sowing",
            activity_date="2026-01-01",
            product_or_input="Saatgut",
            quantity="150.00",
            unit="kg/ha",
        )
        evaluate_inactivity_alerts(reference_date=FieldActivity.objects.first().activity_date + timedelta(days=40))
        alert = FieldAlert.objects.filter(plot=self.plot, rule_type="inactivity_days", is_resolved=False).first()
        self.assertIsNotNone(alert)

        resolve_url = reverse("alert-resolve", args=[alert.id])
        res = self.client.post(resolve_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_resolved"])
