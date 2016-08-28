#!/usr/bin/env python3

from datetime import datetime
import time
import requests
import yaml
from bs4 import BeautifulSoup

headers = {'user-agent': 'WeatherBot/0.1'}

last_id = 0

current_weather_key = '/weather '
forecast_weather_key = '/forecast '

with open('weather.yaml') as conf_file:
    conf = yaml.load(conf_file) 
    api_id = conf['api_id']

def get_weather(city_id):
    weather_req = requests.get('http://api.openweathermap.org/data/2.5/weather?appid=%s&q=%s'
            % (api_id, city_id))
    weather_data = weather_req.json()

    if 'weather' in weather_data:
        glob = weather_data['weather'][0]['description']
    else:
        glob = 'unknown'
    if 'main' in weather_data:
        temp = float(weather_data['main']['temp']) - 273.15
        press = weather_data['main']['pressure']
        humidity = weather_data['main']['humidity']
    else:
        temp = float('nan')
        press = 'unknown'
        humidity = 'unknown'
    if 'wind' in weather_data:
        wind = weather_data['wind']['speed']
    else:
        wind = 'unknown'
    if 'name' in weather_data:
        city_name = weather_data['name']
    else:
        city_name = 'unknown'

    return 'Current weather at %s: %s, %.1f°C, %s %%, %s hPa, %s m/s' % (city_name,
            glob, temp, humidity, press, wind)

while True:
    backend = requests.get('http://faab.euromussels.eu:80//data/backend.xml',
        headers=headers)

    soup = BeautifulSoup(backend.text, 'xml')

    cur_id = 0

    for post in soup.find_all('post'):

        id = int(post.get('id'))

        if id > last_id:
            if id > cur_id: 
                cur_id = id

            message = post.find('message').text
            if message.startswith(current_weather_key):
                parsed_date = datetime.strptime(post.get('time'),
                        '%Y%m%d%H%M%S')
                city_id = message[len(current_weather_key):]
                weather = get_weather(city_id)
                
                msg = '%s %s' % (parsed_date.strftime('%H:%M:%S'), weather)

                print(msg)

                requests.post('http://faab.euromussels.eu:80//add.php', data =
                        {'message': msg})



    if cur_id > 0:
        last_id = cur_id

    time.sleep(60)


