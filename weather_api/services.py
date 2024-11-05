import requests
import datetime
from django.conf import settings

from .models import City, WeatherRequest
from django.core.cache import cache

class CityNotFound(Exception):
    pass

class GeoDecoderAPIService:
    API_KEY = settings.GEO_DECODER_API_KEY # '1988adbd-ce7e-4322-9c3c-5728ea289416'

    def get_url(self, city_name):
        return 'https://geocode-maps.yandex.ru/1.x/?apikey={}&geocode={}&format=json'.format(self.API_KEY, city_name)

    def find_city_coords(self, city_name):
        resp = requests.get(self.get_url(city_name)).json()
        if resp['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == '0':
            raise CityNotFound
        lat, long = resp['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
        return (float(lat), float(long))

class WeatherAPIService:
    headers = {
        'X-Yandex-Weather-Key': settings.WEATHER_API_KEY # 'a3fe20fe-1a21-451e-87ca-f9d0ab096a77'
    }
    cache_seconds = 30 * 60
    def get_url(self, lat, long):
        return 'https://api.weather.yandex.ru/v2/forecast?lat={}&lon={}'.format(lat, long)

    def get_weather(self, lat, long):
        cache_key = 'weather_{}_{}'.format(lat, long)
        cached = cache.get(cache_key)
        if cached:
            return cached
        resp = requests.get(self.get_url(lat, long), headers=self.headers).json()
        result = {
            'temp': resp['fact']['temp'],
            'pressure': resp['fact']['pressure_mm'],
            'wind_speed': resp['fact']['wind_speed']
        }
        cache.set(cache_key, result, self.cache_seconds)
        return result

class WeatherService:
    @staticmethod
    def get_city_coords(city_name):
        try:
            city = City.objects.get(name=city_name)
            return (city.latitude, city.longitude)
        except City.DoesNotExist:
            api = GeoDecoderAPIService()
            lat, long = api.find_city_coords(city_name)
            city = City.objects.create(name=city_name, latitude=lat, longitude=long)
            return (city.latitude, city.longitude)

    @staticmethod
    def get_weather(city_name, kind='api'):
        lat, long = WeatherService.get_city_coords(city_name)
        api = WeatherAPIService()
        weather = api.get_weather(lat, long)
        new_request = WeatherRequest.objects.create(
            kind=kind,
            city=City.objects.get(name=city_name), 
            temp=weather['temp'], 
            pressure=weather['pressure'], 
            wind_speed=weather['wind_speed']
        )
        return weather  