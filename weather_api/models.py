from django.db import models

# Create your models here.

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


REQUEST_CHOICES = (
    ('tg', 'Telegram'),
    ('api', 'Web API'),
)

class WeatherRequest(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=3, choices=REQUEST_CHOICES)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    temp = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()

    def __str__(self):
        return [self.city.name, self.date, self.temp, self.pressure, self.wind_speed].join(', ')
