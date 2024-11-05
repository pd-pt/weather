import pytest
import requests_mock

from .services import GeoDecoderAPIService, WeatherAPIService, WeatherService, CityNotFound
from .models import City, WeatherRequest
from django.conf import settings

import requests
from requests_mock.contrib import fixture
import testtools

class GeocoderAPITest(testtools.TestCase):
     no_city_url = 'https://geocode-maps.yandex.ru/1.x/?apikey={}&geocode=none&format=json'.format(settings.GEO_DECODER_API_KEY)
     city_url = 'https://geocode-maps.yandex.ru/1.x/?apikey={}&geocode=Moscow&format=json'.format(settings.GEO_DECODER_API_KEY)

     def setUp(self):
        super(GeocoderAPITest, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())

     def test_geo_incorrect_city(self):
        """Test handling incorrect city name"""
        self.requests_mock.register_uri('GET', self.no_city_url, json={'response': {'GeoObjectCollection': {'metaDataProperty': {'GeocoderResponseMetaData': {'found': '0'}}}}})
        api = GeoDecoderAPIService()
        self.assertRaises(CityNotFound, lambda: api.find_city_coords(city_name='none'))

     def test_geo_correct_city(self):
        """Test handling correct city name"""
        self.requests_mock.register_uri('GET', self.city_url, json={'response': {'GeoObjectCollection': {'metaDataProperty': {'GeocoderResponseMetaData': {'found': '1'}}, 'featureMember': [{'GeoObject': {'Point': {'pos': '1 2'}}}]}}})
        api = GeoDecoderAPIService()
        lat, long = api.find_city_coords(city_name='Moscow')
        self.assertEqual((2, 1), (lat, long))

@pytest.mark.django_db
class WeatherAPITest(testtools.TestCase):
    url = 'https://api.weather.yandex.ru/v2/forecast?lat=1&lon=2'.format(settings.WEATHER_API_KEY)

    def setUp(self):
        super(WeatherAPITest, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())

    def test_weather_api(self):
        """
        Test correct response from weather api
        """
        self.requests_mock.register_uri('GET', self.url, json={'fact': {'temp': 1, 'pressure_mm': 0, 'wind_speed': 3}})
        api = WeatherAPIService()
        weather = api.get_weather(lat=1, long=2)
        self.assertEqual((1, 0, 3), (weather['temp'], weather['pressure'], weather['wind_speed']))


@pytest.mark.django_db
class WeatherServiceTest(testtools.TestCase):
    geocode_url = 'https://geocode-maps.yandex.ru/1.x/?apikey={}&geocode=Moscow&format=json'.format(settings.GEO_DECODER_API_KEY)
    weather_url = 'https://api.weather.yandex.ru/v2/forecast?lat=2.0&lon=1.0'.format(settings.WEATHER_API_KEY)

    def setUp(self):
        super(WeatherServiceTest, self).setUp() 
        self.requests_mock = self.useFixture(fixture.Fixture())

    def test_weather_service(self):
        """
        Test that all models are created correctly
        """
        self.requests_mock.register_uri('GET', self.geocode_url, json={'response': {'GeoObjectCollection': {'metaDataProperty': {'GeocoderResponseMetaData': {'found': '1'}}, 'featureMember': [{'GeoObject': {'Point': {'pos': '1 2'}}}]}}})
        self.requests_mock.register_uri('GET', self.weather_url, json={'fact': {'temp': 1, 'pressure_mm': 0, 'wind_speed': 3}})

        weather = WeatherService.get_weather(city_name='Moscow')
        city = City.objects.get(name='Moscow')
        self.assertEqual((1, 0, 3), (weather['temp'], weather['pressure'], weather['wind_speed']))
        self.assertEqual(city.latitude, 2.0)
        self.assertEqual(city.longitude, 1.0)
        request = WeatherRequest.objects.filter(city=city).last()
        self.assertEqual(request.temp, 1)
        self.assertEqual(request.pressure, 0)
        self.assertEqual(request.wind_speed, 3)
        self.assertEqual(request.kind, 'api')

