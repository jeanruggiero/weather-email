from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.http import HttpRequest
import os
import requests
import json
import datetime
from ...models import Subscriber


class WeatherReport():

    def __init__(self, temperature, precip, summary):
        temperature = temperature
        precip = precip
        summary = summary


def weather_request(location, current=True):
    """
    Returns the
    :param location:
    :param current:
    :return:
    """
    pass


def get_current_weather(location):
    """
    Returns the weather for a given location and optional time. If time argument
    is not provided, the current weather will be returned.
    """
    base_url = 'https://api.weatherbit.io/v2.0/'

    query_string = f'current?lat={location.latitude}&lon={location.longitude}&units=I&key={os.environ.get("WEATHER_API_KEY")}'
    response = requests.get(base_url+query_string)
    data = json.loads(response.content.decode())['data'][0]

    return data['temp'], data['precip'], data['weather']['description']

def get_historical_weather(location):
    pass



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

