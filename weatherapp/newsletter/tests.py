from django.test import TestCase
from .models import Subscriber, Location
from unittest.mock import MagicMock, patch
import datetime
import requests
from django.core.mail import send_mail

from .management.commands.sendmail import *


@patch("os.environ.get", MagicMock(return_value='api_key'))
class CurrentWeatherGetterTests(TestCase):

    location = MagicMock()
    location.latitude = 5
    location.longitude = -10

    current_weather_getter = CurrentWeatherGetter(location)

    def test_params(self):
        self.assertEqual(self.current_weather_getter.params,
            {'units': 'I', 'lat': 5, 'lon': -10, 'key': 'api_key'})

    def test_query_string(self):
        self.assertEqual(self.current_weather_getter.query_string,
                         "units=I&lat=5&lon=-10&key=api_key")

    def test_request_weather(self):
        self.current_weather_getter.parse_response = MagicMock()
        request_mock = MagicMock()
        with patch('requests.get', request_mock):
            self.current_weather_getter.request_weather()
        request_mock.assert_called_with(
            "https://api.weatherbit.io/v2.0/current?units=I&lat=5&lon=-10&key=api_key")


@patch("os.environ.get", MagicMock(return_value='api_key'))
class HistoricalTemperatureGetterTests(TestCase):

    location = MagicMock()
    location.latitude = 5
    location.longitude = -10

    historical_temperature_getter = HistoricalTemperatureGetter(location)

    def test_params(self):
        date = datetime.date(year=2000, month=1, day=2)
        self.assertEqual(self.historical_temperature_getter.params(date),
                         {'key': 'api_key', 'q': '5,-10', 'dt': '2000-01-02'})

    def test_query_string(self):
        self.assertEqual(self.historical_temperature_getter.query_string(
            {'key': 'api_key', 'q': '5,-10', 'dt': '2000-03-04'}), "key=api_key&q=5,-10&dt=2000-03-04")

    def test_request_temperature(self):
        self.historical_temperature_getter.parse_response = MagicMock()
        request_mock = MagicMock()
        with patch('requests.get', request_mock):
            date = datetime.date(year=2000, month=1, day=2)
            self.historical_temperature_getter.request_temperature(date)
        request_mock.assert_called_with(
            'http://api.apixu.com/v1/history.json?key=api_key&q=5,-10&dt=2000-01-02')

    def test_typical_temperature(self):
        self.historical_temperature_getter.request_temperature = MagicMock(side_effect=[1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(self.historical_temperature_getter.typical_temperature, 4)


class EmailSenderTests(TestCase):

    def setUp(self):
        current_weather_getter = MagicMock()
        current_weather_getter.temperature = 61
        current_weather_getter.precip = 0
        current_weather_getter.summary = 'Weather summary'
        historical_temperature_getter = MagicMock()
        historical_temperature_getter.typical_temperature = 60
        subscriber = MagicMock()
        subscriber.location = 'Seattle'
        subscriber.email = 'Not an email'
        self.email_sender = EmailSender(current_weather_getter, historical_temperature_getter, subscriber)

    def test_subject_sunny(self):
        self.email_sender.summary = 'Clear sky'
        self.assertEqual(self.email_sender.subject,
                         "It's nice out! Enjoy a discount on us.")

    def test_subject_warm(self):
        self.email_sender.temperature = 65
        self.assertEqual(self.email_sender.subject,
                         "It's nice out! Enjoy a discount on us.")

    def test_subject_cold(self):
        self.email_sender.temperature = 55
        self.assertEqual(self.email_sender.subject,
                         "Not so nice out? That's okay, enjoy a discount on us.")

    def test_subject_precip(self):
        self.email_sender.precip = 1
        self.assertEqual(self.email_sender.subject,
                         "Not so nice out? That's okay, enjoy a discount on us.")

    def test_subject_normal(self):
        self.assertEqual(self.email_sender.subject, "Enjoy a discount on us.")

    def test_body(self):
        self.assertEqual(self.email_sender.body,
                         'The weather in Seattle is currently 61 deg F and Weather summary.')


