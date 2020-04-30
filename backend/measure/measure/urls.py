from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

from measure.views import MeasurementView, RhValueView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("measurement", MeasurementView.as_view({"get": "list", "post": "measure"})),
    path(
        "measurement/<int:pk>",
        MeasurementView.as_view({"get": "retrieve", "patch": "partial_update"}),
    ),
    path("rh_value", RhValueView.as_view({"get": "list"})),
]
