from django.urls import include, path
from rest_framework.routers import DefaultRouter
from agro.views import (
    AlertRuleViewSet,
    FieldActivityViewSet,
    FieldAlertViewSet,
    FieldPlotViewSet,
    HealthCheckView,
)

router = DefaultRouter()
router.register(r"plots", FieldPlotViewSet, basename="plot")
router.register(r"activities", FieldActivityViewSet, basename="activity")
router.register(r"alerts", FieldAlertViewSet, basename="alert")
router.register(r"rules", AlertRuleViewSet, basename="rule")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("", include(router.urls)),
]
