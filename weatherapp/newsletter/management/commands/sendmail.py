from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import os
import requests
import json
import datetime
import statistics
from ...models import Subscriber


class ApiError(Exception): pass


class CurrentWeatherGetter:
    """
    Encapsulates code to get the current weather.
    """
    base_url = 'https://api.weatherbit.io/v2.0/current?'

    def __init__(self, location):
        self.location = location
        self.weather = self.request_weather()

    @property
    def params(self):
        """
        Returns a dict containing the parameters required for the HTTP GET request
        for current weather.
        """
        return {'units': 'I',
                'lat': self.location.latitude,
                'lon': self.location.longitude,
                'key': os.environ.get('WEATHER_API_KEY')}

    @property
    def query_string(self):
        """
        Returns a query string for the HTTP GET request.
        """
        return '&'.join(key + '=' + str(value) for key, value in self.params.items())

    @staticmethod
    def parse_response(response):
        """
        Parses the response from the weatherbit api and returns the weather data in dict form.
        """
        return json.loads(response.content.decode())['data'][0]

    def request_weather(self):
        """
        Performs an HTTP GET request using the base_url and query_string.
        """
        try:
            response = requests.get(self.base_url + self.query_string)
            return self.parse_response(response)
        except:
            raise ApiError('Current weather request failed.')

    @property
    def temperature(self):
        """Returns current temperature in deg F."""
        return self.weather['temp']

    @property
    def precip(self):
        """Returns current precipitation type."""
        return self.weather['precip']

    @property
    def summary(self):
        """Returns a summary of the weather."""
        return self.weather['weather']['description']


class HistoricalTemperatureGetter:
    """
    Encapsulates code to get the current weather.
    """

    base_url = 'http://api.apixu.com/v1/history.json?'

    def __init__(self, location):
        self.location = location
        self.date = datetime.date.today()

    def params(self, date):
        """
        Returns a dict containing the parameters required for the HTTP GET request
        for historical weather. date arg is a python date object.
        """

        return {'key': os.environ.get('HISTORICAL_API_KEY'),
                'q': '{},{}'.format(self.location.latitude, self.location.longitude),
                'dt': '{:%Y-%m-%d}'.format(date)}

    @staticmethod
    def query_string(params):
        """
        Returns a query string for the HTTP GET request.
        """
        return '&'.join(key + '=' + str(value) for key, value in params.items())

    @staticmethod
    def parse_response(response):
        """
        Parses the response from the apixu API and returns the temperature in deg F.
        """
        return json.loads(response.content.decode())['forecast']['forecastday'][0]['day']['avgtemp_f']

    def request_temperature(self, date):
        """
        Requests historical weather from the apixu api and returns average temperature on the
        specified day.
        """
        try:
            response = requests.get(self.base_url + self.query_string(self.params(date)))
            return self.parse_response(response)
        except:
            raise ApiError('Historical weather request failed.')

    @property
    def typical_temperature(self):
        """
        Returns the average temperature in deg F over the previous 7 days.
        """
        dates = [self.date - datetime.timedelta(days=x) for x in range(1, 8)]
        return statistics.mean(self.request_temperature(date) for date in dates)


class EmailSender:
    """
    Class to send a weather-powered email to a subscriber.
    """

    def __init__(self, current_weather_getter, historical_temperature_getter, subscriber):

        self.current_weather_getter = current_weather_getter
        self.historical_temperature_getter = historical_temperature_getter
        self.subscriber = subscriber

        self.temperature = current_weather_getter.temperature
        self.precip = current_weather_getter.precip
        self.summary = current_weather_getter.summary

        self.typical_temperature = self.historical_temperature_getter.typical_temperature

    @property
    def subject(self):
        """
        Returns an email subject based on how the current weather at the recipient's location
        compares with the average weather at that location.
        """
        if self.summary in ['Clear sky', 'Few clouds', 'Scattered clouds'] or \
                self.typical_temperature - self.temperature <= -5:
            return "It's nice out! Enjoy a discount on us."
        elif self.precip or self.typical_temperature - self.temperature >= 5:
            return "Not so nice out? That's okay, enjoy a discount on us."
        else:
            return "Enjoy a discount on us."

    @property
    def body(self):
        """
        Returns an email body consisting of a subscriber's location and the current weather
        at that location.
        """
        return f"The weather in {self.subscriber.location} is currently {self.temperature} " + \
                f"deg F and {self.summary}."

    def send(self):
        """
        Sends a weather-driven email.
        """
        send_mail(self.subject, self.body, 'jeanruggiero@gmail.com', [self.subscriber.email])


class Command(BaseCommand):
    help = 'Sends an email to all currently subscribed email addresses.'

    def handle(self, *args, **kwargs):
        for subscriber in Subscriber.objects.order_by('location'):

            current_weather_getter = CurrentWeatherGetter(subscriber.location)
            historical_temperature_getter = HistoricalTemperatureGetter(subscriber.location)
            email_sender = EmailSender(current_weather_getter, historical_temperature_getter, subscriber)

            email_sender.send()
