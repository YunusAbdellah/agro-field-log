from django.contrib import admin
from agro.models import AlertRule, FieldActivity, FieldAlert, FieldPlot

admin.site.register(FieldPlot)
admin.site.register(FieldActivity)
admin.site.register(AlertRule)
admin.site.register(FieldAlert)
