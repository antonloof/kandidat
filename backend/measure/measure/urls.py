from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

from measure.views import MeasurmentView


urlpatterns = [
	path('admin/', admin.site.urls),
	path("measurment", MeasurmentView.as_view({"get": "list", "post": "measure"})),
	path("measurment/<int:pk>", MeasurmentView.as_view({"get": "retrieve", "delete": "destroy"})),
]
