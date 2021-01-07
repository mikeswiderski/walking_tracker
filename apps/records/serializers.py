from rest_framework import serializers
from apps.records.models import Record
from apps.records.weather_request import get_weather


class RecordSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(
        max_value=90.0,
        min_value=-90.0,
        help_text='Accepted values: -90.0 to 90.0',
    )
    longitude = serializers.FloatField(
        max_value=180.0,
        min_value=-180.0,
        help_text='Accepted values: -180.0 to 180.0',
    )

    class Meta:
        model = Record
        fields = [
            'id',
            'owner',
            'created',
            'distance',
            'latitude',
            'longitude',
            'weather_conditions',
        ]
        read_only_fields = ['owner', 'weather_conditions']

    def create(self, validated_data):
        weather_conditions = get_weather(
            validated_data['latitude'],
            validated_data['longitude'],
        )
        return Record.objects.create(
            weather_conditions=weather_conditions,
            **validated_data,
        )


class AdminRecordSerializer(RecordSerializer):
    class Meta:
        model = Record
        fields = [
            'id',
            'owner',
            'created',
            'distance',
            'latitude',
            'longitude',
            'weather_conditions',
        ]
        read_only_fields = ['weather_conditions']
