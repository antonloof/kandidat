from rest_framework import serializers

from measure.models import Measurment


class MeasurmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Measurment
		fields = ("id", "open", "created_at", "mobility", "sheet_resistance")


