from django.test import TestCase
from .models import Subscriber, Location
from unittest.mock import MagicMock

from .management.commands.sendmail import *


class SubscriberTestCase(TestCase):
    fixtures = ['test_fixture.json']
    def setUp(self):
        pass


class CurrentWeatherTests(TestCase):
    def setUp(self):
        loc = Location(lat=2, lon=5)

    def test_get_current_weather(self):

        self.current_weather_request = MagicMock()
        get_curent_weather(loc)

        self.current_weather_request.assert_called_with(lat=)


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

        def get_historical_temperature(location):
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

            for day in range(current_day - 7, current_day - 1):
                params['dt'] = '{:%Y-%m-%d}'.format(datetime.date(year, month, day))

                query_string = 'history.json?'
                query_string += '&'.join(key + '=' + str(value) for key, value in params.items())

                response = requests.get(base_url + query_string)
                temperatures.append(
                    json.loads(response.content.decode())['forecast']['forecastday'][0]['day']['avgtemp_f'])

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

