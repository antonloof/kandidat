from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@require_POST
def measure(request):
	return HttpResponse('{"id": 1}')

urlpatterns = [
	path('admin/', admin.site.urls),
	path('measure', measure),
]
