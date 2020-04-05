from rest_framework import serializers

from measure.models import Measurment, RhValue


class MeasurmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Measurment
		fields = ("id", "open", "created_at", "mobility", "sheet_resistance")


class RhValueSerializer(serializers.ModelSerializer):
		class Meta:
			model = RhValue
			fields = ("measurment_id", "value")

