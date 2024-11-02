from rest_framework import serializers
from .models import City, WeatherRequest

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'latitude', 'longitude']


class WeatherRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRequest
        fields = ['id', 'kind', 'city', 'time', 'temp', 'pressure', 'wind_speed']


class WeatherSerializer(serializers.Serializer):
    temp = serializers.FloatField()
    pressure = serializers.FloatField()
    wind_speed = serializers.FloatField()