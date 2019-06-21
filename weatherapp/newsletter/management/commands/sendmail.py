from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import os
import requests
import json
import datetime
import statistics
from ...models import Subscriber


class CurrentWeatherGetter:
    """
    Encapsulates code to get the current weather.
    """
    base_url = 'https://api.weatherbit.io/v2.0/current?'

    def __init__(self, location):
        self.location = location

    @property
    def params(self):
        """
        Returns a dict containing the parameters required for the HTTP GET request
        for current weather.
        """
        return {'units': 'I',
                'lat': self.location.latitude,
                'lon': self.locatiton.longitude,
                'key': os.environ.get('WEATHER_API_KEY')}

    @property
    def query_string(self):
        """
        Returns a query string for the HTTP GET request.
        """
        return '&'.join(key + '=' + str(value) for key, value in self.params.items())

    def request_weather(self):
        """
        Performs an HTTP GET request using the base_url and query_string.
        """
        response = requests.get(self.base_url + self.query_string)
        return json.loads(response.content.decode())['data'][0]

    @property
    def temperature(self):
        """Returns current temperature in deg F."""
        return self.request_weather()['temp']

    @property
    def precip(self):
        """Returns current precipitation type."""
        return self.request_weather()['precip']

    @property
    def summary(self):
        """Returns a summary of the weather."""
        return self.request_weather()['weather']['description'])


class HistoricalTemperatureGetter:
    """
    Encapsulates code to get the current weather.
    """

    base_url = 'http://api.apixu.com/v1/'

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

    def request_temperature(self, date):
        response = requests.get(self.base_url + self.query_string(self.params(date)))
        return json.loads(response.content.decode())['forecast']['forecastday'][0]['day']['avgtemp_f']



    @property
    def typical_temperature(self):
        # need to figure out range of dates
        return statistics.mean(self.request_temperature(date) for date in range())


class EmailSender:

    def __init__(self, current_weather_getter, historical_weather_getter):

        self.current_weather_getter = current_weather_getter
        self.historical_weather_getter = historical_weather_getter

        self.subscribers = Subscriber.objects.order_by('location')

        # Use a set comprehension for locations such that only one set of API calls is made per unique location
        self.locations = {subscriber.location for subscriber in subscribers}
        self.current_weather = {location: CurrentWeatherGetter(location) for location in locations}
        self.historical_temperature = {location: get_historical_temperature(location) for location in locations}

    def email_subject(current_weather, historical_temperature):
        """
        Returns an email subject based on how the current weather at the recipient's location
        compares with the average weather at that location.
        """

        if current_weather.summary in ['Clear sky', 'Few clouds', 'Scattered clouds'] or \
                historical_temperature - current_weather.temperature >= 5:
            return "It's nice out! Enjoy a discount on us."
        elif current_weather.precip or historical_temperature - current_weather.temperature <= -5:
            return "Not so nice out? That's okay, enjoy a discount on us."
        else:
            return "Enjoy a discount on us."

    @property
    def body(self):
        return f"The weather in {location} is currently {weather.temperature} deg F and {weather.summary}."

    @property
    def subject(self):
        retturn email_subject(current_weather[subscriber.location],
                                historical_temperature[subscriber.location])

    def send_mail_to_all(self):
        for subscriber in self.subscribers:
            send_mail(self.subject, self.body, 'jeanruggiero@gmail.com', [subscriber.email])


class Command(BaseCommand):
    help = 'Sends an email to all currently subscribed email addresses.'


    def handle(self, *args, **kwargs):
        # subscribers = Subscriber.objects.order_by('location')
        # locations = {subscriber.location for subscriber in subscribers}
        # current_weather = {location: get_current_weather(location) for location in locations}
        # historical_temperature = {location: get_historical_temperature(location) for location in locations}

        # for subscriber in subscribers:
        #
        #     # subject = email_subject(current_weather[subscriber.location],
        #     #                         historical_temperature[subscriber.location])
        #     #
        #     # body = email_body(current_weather[subscriber.location], subscriber.location)
        #
        #     send_mail(subject,
        #               body,
        #               'jeanruggiero@gmail.com',
        #               [subscriber.email])

        EmailSender().send_mail_to_all()

