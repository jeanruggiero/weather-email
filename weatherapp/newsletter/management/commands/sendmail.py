from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.http import HttpRequest
import os
import requests
import json
from ...models import Subscriber


# class WeatherReport():
#
#     def __init__(self, temperature, precip):
#         temperature = temperature
#         precip = precip


def degCtodegF(temperature):
    """
    Converts temperature from deg C to deg F.
    """
    return temperature * 9/5 + 32


def get_weather(location, time=None):
    """
    Returns the weather for a given location and optional time. If time argument
    is not provided, the current weather will be returned.
    """
    base_url = 'https://api.weatherbit.io/v2.0/'

    if time:
        pass
    else:
        query_string = f'current?lat={location.latitude}&lon={location.longitude}&units=I&key={os.environ.get("WEATHER_API_KEY")}'
    response = requests.get(base_url+query_string)
    data = json.loads(response.content.decode())['data'][0]

    return data['temp'], data['precip'], data['weather']['description']



class Command(BaseCommand):
    help = 'Lists all currently subscribed email addresses.'


    def handle(self, *args, **kwargs):
        subscribers = Subscriber.objects.order_by('location')
        locations = {subscriber.location for subscriber in subscribers}
        weather = {location: get_weather(location) for location in locations}
        for subscriber in subscribers:

            body = f"The weather in {str(subscriber.location)} is currently " + \
                f"{weather[subscriber.location][0]} deg F and " + \
                f"{weather[subscriber.location][2]}."

            send_mail('Test',
                      body,
                      'jeanruggiero@gmail.com',
                      [subscriber.email])

