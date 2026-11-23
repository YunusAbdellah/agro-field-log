from rest_framework import serializers
from agro.models import AlertRule, FieldActivity, FieldAlert, FieldPlot


class FieldActivitySerializer(serializers.ModelSerializer):
    activity_type_label = serializers.CharField(source="get_activity_type_display", read_only=True)

    class Meta:
        model = FieldActivity
        fields = [
            "id",
            "plot",
            "activity_type",
            "activity_type_label",
            "activity_date",
            "product_or_input",
            "quantity",
            "unit",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FieldPlotSerializer(serializers.ModelSerializer):
    activities_count = serializers.IntegerField(source="activities.count", read_only=True)
    open_alerts_count = serializers.SerializerMethodField()

    class Meta:
        model = FieldPlot
        fields = [
            "id",
            "name",
            "area_ha",
            "soil_type",
            "current_crop",
            "season_year",
            "latitude",
            "longitude",
            "notes",
            "activities_count",
            "open_alerts_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_open_alerts_count(self, obj):
        return obj.alerts.filter(is_resolved=False).count()


class FieldAlertSerializer(serializers.ModelSerializer):
    plot_name = serializers.CharField(source="plot.name", read_only=True)

    class Meta:
        model = FieldAlert
        fields = [
            "id",
            "plot",
            "plot_name",
            "rule_type",
            "severity",
            "message",
            "is_resolved",
            "triggered_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "triggered_at", "resolved_at"]


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = ["id", "plot", "rule_type", "threshold_value", "is_active"]
