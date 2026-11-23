from collections import defaultdict
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from agro.models import AlertRule, FieldActivity, FieldAlert, FieldPlot
from agro.serializers import (
    AlertRuleSerializer,
    FieldActivitySerializer,
    FieldAlertSerializer,
    FieldPlotSerializer,
)
from agro.services.alert_engine import evaluate_activity_alerts, evaluate_inactivity_alerts


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "agrolog-api"})


class FieldPlotViewSet(viewsets.ModelViewSet):
    serializer_class = FieldPlotSerializer

    def get_queryset(self):
        qs = FieldPlot.objects.all()
        season = self.request.query_params.get("season")
        search = self.request.query_params.get("search")
        if season:
            qs = qs.filter(season_year=season)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(current_crop__icontains=search)
        return qs

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        plot = self.get_object()
        activities = plot.activities.all()
        totals_by_unit = defaultdict(float)
        counts_by_type = defaultdict(int)

        for act in activities:
            totals_by_unit[act.unit] = round(totals_by_unit[act.unit] + float(act.quantity), 2)
            counts_by_type[act.activity_type] += 1

        latest_activity = activities.order_by("-activity_date").first()
        return Response({
            "plot_id": plot.id,
            "plot_name": plot.name,
            "area_ha": float(plot.area_ha),
            "current_crop": plot.current_crop,
            "season_year": plot.season_year,
            "total_activities": activities.count(),
            "last_activity_date": latest_activity.activity_date if latest_activity else None,
            "totals_by_unit": dict(totals_by_unit),
            "counts_by_type": dict(counts_by_type),
            "open_alerts": plot.alerts.filter(is_resolved=False).count(),
        })


class FieldActivityViewSet(viewsets.ModelViewSet):
    serializer_class = FieldActivitySerializer

    def get_queryset(self):
        qs = FieldActivity.objects.select_related("plot").all()
        plot_id = self.request.query_params.get("plot")
        activity_type = self.request.query_params.get("type")
        if plot_id:
            qs = qs.filter(plot_id=plot_id)
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        return qs

    def perform_create(self, serializer):
        activity = serializer.save()
        evaluate_activity_alerts(activity)


class FieldAlertViewSet(viewsets.ModelViewSet):
    serializer_class = FieldAlertSerializer

    def get_queryset(self):
        qs = FieldAlert.objects.select_related("plot").all()
        resolved_param = self.request.query_params.get("resolved")
        if resolved_param is not None:
            is_resolved = resolved_param.lower() == "true"
            qs = qs.filter(is_resolved=is_resolved)
        return qs

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save(update_fields=["is_resolved", "resolved_at"])
        return Response(FieldAlertSerializer(alert).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def scan_inactivity(self, request):
        evaluate_inactivity_alerts()
        open_alerts = FieldAlert.objects.filter(is_resolved=False)
        return Response(FieldAlertSerializer(open_alerts, many=True).data, status=status.HTTP_200_OK)


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
