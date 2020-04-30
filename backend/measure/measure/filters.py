import django_filters
from django.db import models

from measure.models import RhValue, Measurement


class RhValueFilter(django_filters.FilterSet):
    class Meta:
        model = RhValue
        fields = {"measurement_id": ["exact"]}


class MeasurementFilter(django_filters.FilterSet):
    class Meta:
        model = Measurement
        fields = {
            "open": ["exact"],
            "name": ["icontains"],
            "created_at": ["gt", "lt"],
        }

        filter_overrides = {
            models.DateTimeField: {"filter_class": django_filters.IsoDateTimeFilter}
        }
