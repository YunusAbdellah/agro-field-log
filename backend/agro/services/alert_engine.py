from decimal import Decimal
from django.utils import timezone
from agro.models import AlertRule, FieldActivity, FieldAlert, FieldPlot
from agro.services.weather_service import get_rainfall_forecast_mm

DEFAULT_MAX_INPUT_RATE = Decimal("180.00")
DEFAULT_INACTIVITY_DAYS = 21
DEFAULT_RAIN_THRESHOLD_MM = Decimal("8.00")


def _create_alert_if_not_open(plot: FieldPlot, rule_type: str, severity: str, message: str):
    exists = FieldAlert.objects.filter(
        plot=plot,
        rule_type=rule_type,
        message=message,
        is_resolved=False,
    ).exists()
    if not exists:
        FieldAlert.objects.create(
            plot=plot,
            rule_type=rule_type,
            severity=severity,
            message=message,
        )


def evaluate_activity_alerts(activity: FieldActivity):
    plot = activity.plot
    rule = (
        AlertRule.objects.filter(plot=plot, rule_type="high_input_rate", is_active=True).first()
        or AlertRule.objects.filter(plot__isnull=True, rule_type="high_input_rate", is_active=True).first()
    )
    threshold = rule.threshold_value if rule else DEFAULT_MAX_INPUT_RATE

    if activity.activity_type in ("fertilization", "crop_protection", "irrigation") and activity.quantity > threshold:
        msg = (
            f"High input rate ({activity.quantity} {activity.unit}) for {activity.product_or_input} "
            f"exceeds threshold ({threshold} {activity.unit})."
        )
        _create_alert_if_not_open(plot, "high_input_rate", "warning", msg)

    if activity.activity_type in ("fertilization", "crop_protection"):
        weather = get_rainfall_forecast_mm(plot.latitude, plot.longitude)
        rain_mm = Decimal(str(weather["precipitation_24h_mm"]))
        rain_rule = (
            AlertRule.objects.filter(plot=plot, rule_type="rain_before_fieldwork", is_active=True).first()
            or AlertRule.objects.filter(plot__isnull=True, rule_type="rain_before_fieldwork", is_active=True).first()
        )
        rain_threshold = rain_rule.threshold_value if rain_rule else DEFAULT_RAIN_THRESHOLD_MM
        if rain_mm >= rain_threshold:
            msg = (
                f"Forecast rain ({rain_mm} mm / 24h via {weather['source']}) may cause runoff/wash-off "
                f"after {activity.get_activity_type_display().lower()}."
            )
            _create_alert_if_not_open(plot, "rain_before_fieldwork", "info", msg)


def evaluate_inactivity_alerts(reference_date=None):
    today = reference_date or timezone.localdate()
    for plot in FieldPlot.objects.all():
        rule = (
            AlertRule.objects.filter(plot=plot, rule_type="inactivity_days", is_active=True).first()
            or AlertRule.objects.filter(plot__isnull=True, rule_type="inactivity_days", is_active=True).first()
        )
        max_days = int(rule.threshold_value) if rule else DEFAULT_INACTIVITY_DAYS

        latest = FieldActivity.objects.filter(plot=plot).order_by("-activity_date").first()
        if latest:
            days_since = (today - latest.activity_date).days
        else:
            days_since = max_days + 1

        if days_since > max_days:
            msg = f"No field activity logged for {days_since} days (limit: {max_days} days)."
            _create_alert_if_not_open(plot, "inactivity_days", "warning", msg)
