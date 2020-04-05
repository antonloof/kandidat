import django_filters
from measure.models import RhValue, Measurment


class RhValueFilter(django_filters.FilterSet):
    class Meta:
        model = RhValue
        fields = {"measurment_id": ["exact"]}


class MeasurmentFilter(django_filters.FilterSet):
    class Meta:
        model = Measurment
        fields = {"open": ["exact"]}
