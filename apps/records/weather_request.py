import requests
from django.conf import settings


def get_weather(latitude, longitude):

    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    appid = settings.WEATHER_API_KEY
    params = dict(lat=latitude, lon=longitude, appid=appid)
    response = requests.get(url=api_url, params=params)
    if response.status_code == 200:
        r = response.json()
        description = r['weather'][0]['description']
        return description
    else:
        response.raise_for_status()
