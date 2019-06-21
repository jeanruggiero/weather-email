from django.core.management.base import BaseCommand
from django.core.mail import send_mail
import os
import requests
import json
import datetime
import statistics
from ...models import Subscriber


class WeatherReport():

    def __init__(self, temperature, precip, summary):
        self.temperature = temperature
        self.precip = precip
        self.summary = summary


def current_weather_request(**kwargs):
    """
    Returns the current weather queried using the params specified in **kwargs. The weather is
    returned as a WeatherReport object with SI units.
    """
    base_url = 'https://api.weatherbit.io/v2.0/'

    params = kwargs
    params['units'] = 'I'
    params['key'] = os.environ.get('WEATHER_API_KEY')

    query_string = 'current?'
    query_string += '&'.join(key + '=' + str(value) for key, value in params.items())
    response = requests.get(base_url + query_string)

    data = json.loads(response.content.decode())['data'][0]
    return WeatherReport(data['temp'], data['precip'], data['weather']['description'])


def get_historical_weather(location):
    """
    Returns the average daily temperature in deg F for the previous 7 days.
    """

    base_url = 'http://api.apixu.com/v1/'

    params = dict()
    params['key'] = os.environ.get('HISTORICAL_API_KEY')
    params['q'] = '{},{}'.format(location.latitude, location.longitude)

    year = datetime.datetime.now().year
    current_day = datetime.datetime.now().day
    month = datetime.datetime.now().month
    temperatures = []

    for day in range(current_day-7, current_day-1):
        params['dt'] = '{:%Y-%m-%d}'.format(datetime.date(year, month, day))

        query_string = 'history.json?'
        query_string += '&'.join(key + '=' + str(value) for key, value in params.items())

        response = requests.get(base_url + query_string)
        temperatures.append(json.loads(response.content.decode())['forecast']['forecastday'][0]['day']['avgtemp_f'])

    return statistics.mean(temperatures)


def get_current_weather(location):
    """
    Returns the weather for a given location and optional time. If time argument
    is not provided, the current weather will be returned.
    """
    return current_weather_request(lat=location.latitude, lon=location.longitude)


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


def email_body(weather, location):
    return f"The weather in {location} is currently {weather.temperature} deg F and {weather.summary}."


class Command(BaseCommand):
    help = 'Sends an email to all currently subscribed email addresses.'


    def handle(self, *args, **kwargs):
        subscribers = Subscriber.objects.order_by('location')
        locations = {subscriber.location for subscriber in subscribers}
        current_weather = {location: get_current_weather(location) for location in locations}
        historical_weather = {location: get_historical_weather(location) for location in locations}

        for subscriber in subscribers:

            subject = email_subject(current_weather[subscriber.location],
                                    historical_weather[subscriber.location])

            body = email_body(current_weather[subscriber.location], subscriber.location)

            send_mail(subject,
                      body,
                      'jeanruggiero@gmail.com',
                      [subscriber.email])

