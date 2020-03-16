from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from measure.views import start_measurement



urlpatterns = [
	path('admin/', admin.site.urls),
	path('measure', start_measurement),
]
