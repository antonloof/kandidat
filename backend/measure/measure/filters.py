import django_filters
from measure.models import RhValue, Measurement


class RhValueFilter(django_filters.FilterSet):
    class Meta:
        model = RhValue
        fields = {"measurement_id": ["exact"]}


class MeasurementFilter(django_filters.FilterSet):
    class Meta:
        model = Measurement
        fields = {"open": ["exact"]}
