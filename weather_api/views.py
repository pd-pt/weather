from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer

from .services import WeatherService
from .models import City, WeatherRequest
from .serializers import CitySerializer, WeatherRequestSerializer, WeatherSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class WeatherRequestViewSet(viewsets.ModelViewSet):
    queryset = WeatherRequest.objects.all()
    serializer_class = WeatherRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['kind']
    search_fields = ['city__id', 'city__name']
    ordering_fields = ['city__id', 'city__name', 'time']


class WeatherViewSet(viewsets.GenericViewSet):
    @extend_schema(
        methods=['GET'],
        parameters=[
            OpenApiParameter(name="city_name", required=True, type=str)
        ],
        description='Fetch weather for a given city',
        responses={
            200: WeatherSerializer,
            400: OpenApiResponse(description='Bad Request'),
        }
    )
    @action(methods=['GET'], detail=False)
    def weather(self, request, format=None):
        city_name = request.query_params.get('city_name', None)

        if not city_name:
            raise ParseError('city_name is required')

        try:
            weather = WeatherService.get_weather(city_name)
            return Response(weather, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
