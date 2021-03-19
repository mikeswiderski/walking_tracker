import re

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response


def parse_search(search_phrase):

    re_par = re.match(r"\s*\(\s*(.+)\)\s+(or|and)\s+\(\s*(.+)\)", search_phrase, re.IGNORECASE)
    re_no_par = re.match(r"\s*(\S+)\s+(eq|ne|lt|gt)\s+(\S+\s?\S*)", search_phrase, re.IGNORECASE)

    if re_par is not None:
        search_phrase = re_par.groups()
    elif re_no_par is not None:
        search_phrase = re_no_par.groups()
    else:
        raise ValidationError('Wrong value for search_phrase')

    left, op, right = search_phrase

    if op.upper() == 'AND':
        return parse_search(left) & parse_search(right)
    elif op.upper() == 'OR':
        return parse_search(left) | parse_search(right)
    elif op.upper() == 'EQ':
        return Q(**{left: right})
    elif op.upper() == 'NE':
        return ~Q(**{left: right})
    elif op.upper() == 'GT':
        return Q(**{left + "__gt": right})
    elif op.upper() == 'LT':
        return Q(**{left + "__lt": right})
    else:
        raise ValidationError('Wrong value for op')


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
