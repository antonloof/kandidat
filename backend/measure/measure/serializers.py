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
            "name",
            "steps_per_measurement",
            "error",
        )

    def validate(self, data):
        connections = []
        for i in range(1, 5):
            default = None
            key = f"connection_{i}"
            if self.instance is not None:
                default = getattr(self.instance, key)
            connections.append(data.get(key, default))

        if len(set(connections)) != len(connections):
            raise serializers.ValidationError(f"All connections must be unique. Got: {connections}")
        return data


class RhValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RhValue
        fields = ("id", "measurement_id", "value", "angle")
