from rest_framework import serializers

from measure.models import Measurement, RhValue


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = (
            "id",
            "open",
            "created_at",
            "mobility",
            "sheet_resistance",
            "amplitude",
            "angle_freq",
            "phase",
            "offset",
            "connection_1",
            "connection_2",
            "connection_3",
            "connection_4",
            "current_limit",
        )
    
    def validate(self, data):
        connections = [data[f"connection_{i}"] for i in range(1, 5)]
        if len(set(connections)) != len(connections):
            raise serializers.ValidationError(
                f"All connections must be unique. Got: {connections}"
            )
        return data


class RhValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RhValue
        fields = ("measurement_id", "value")
