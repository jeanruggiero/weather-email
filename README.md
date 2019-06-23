# weather-email
A Django app that includes a user interface for newsletter signup and a command line interface for sending emails to all recipients with content based on the recipient's weather.

# To run this app:
1. Start by cloning this project.
2. Set the following environment variables:<br>
`GMAIL_PASSWORD`: email host password<br>
`GMAIL_USER`: email host user<br>
`WEATHER_API_KEY`: [weatherbit.io](https://www.weatherbit.io/api) API key<br>
`HISTORICAL_API_KEY`: [apixu](https://www.apixu.com/api.aspx) API key

3. Run the following from the command line inside the project directory
```
pip install requirements.txt
python weatherapp/manage.py runserver
```
