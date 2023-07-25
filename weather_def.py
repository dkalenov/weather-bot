from datetime import datetime, timedelta # classes for manipulating dates, times and a duration
import requests # interacting with API
from config import OPEN_WEATHER_MAP_API_KEY

# Setting emoji according to the weather changing
code_to_smile_list = {
                'Clear': '\U00002600',
                'Clouds': '\U00002601',
                'Rain': '\U0001F327',
                'Drizzle': '\U00002614',
                'Thunderstorm': '\U000026A1',
                'Snow': '\U0001F328',
                'Mist': '\U0001F32B'
            }

# getting a current weather forecast
def get_current_weather(city: str):

    # accessing the openweather API
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # extracting the JSON data
    data = r.json()

    # extracting values from JSON Objects
    city = data['name'] + ',' + ' ' + data['sys']['country']
    temp = data['main']['temp']
    weather_description = data['weather'][0]['main']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']
    feels_like = data['main']['feels_like']
    sunrise_timestamp = datetime.fromtimestamp(data['sys']['sunrise'])
    sunset_timestamp = datetime.fromtimestamp(data['sys']['sunset'])
    length_of_the_day = datetime.fromtimestamp(data['sys']['sunset']) - datetime.fromtimestamp(data['sys']['sunrise'])

    # get weather_description emoji
    wd = code_to_smile_list.get(weather_description, f'\U0001F937')

    # displaying the weather forecast to the user
    weather_forecast = (
        f'*** {datetime.now().strftime("%a %d %b %Y, %H:%M")} ***\n'
        f'      Weather in {city}:\n\n - Temp: {temp}°C, {weather_description}{wd}\n'
        f' - Humidity: {humidity}%\n - Pressure: {pressure}mmHg\n - Wind: {wind}m/s\n'
        f' - Feels like: {feels_like}°C\n - Sunrise: {sunrise_timestamp}\n - Sunset: {sunset_timestamp}\n'
        f' - Length of the day: {length_of_the_day}'
    )
    # return the weather forecast to the user
    return weather_forecast


# getting the weather forecast for 24 hours
def get_24_hours_weather(city):
    # OWM issues a weather report with an interval of 3 hours, so to display the weather for 24 hours we need to send 8 requests
    cnt = 8

    # accessing the openweather API
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt={cnt}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # extracting values from JSON Objects
    data = r.json()
    forecast_list = data['list']

    #  creating a dictionary to iterate over each item in forecast_list, and extract the timestamp for each item
    #  for converting ['dt'] data into a date
    forecast_hours24 = {datetime.fromtimestamp(forecast24['dt']).date(): [] for forecast24 in forecast_list}
    for forecast24 in forecast_list:
        forecast_hours24[datetime.fromtimestamp(forecast24['dt']).date()].append(forecast24)

    forecast24_reply = f"{city} weather forecast for the next 24 hours:\n"

    # extracting values from JSON Objects
    for day, forecast_3hours_list in forecast_hours24.items():
        forecast24_reply += f"\n\U000025FB {day.strftime('%A, %B %d')}\n"
        for forecast_3hours in forecast_3hours_list:
            time = datetime.fromtimestamp(forecast_3hours['dt']).strftime('%I:%M %p')
            temp = forecast_3hours['main']['temp']
            wind = forecast_3hours['wind']['speed']
            feels_like = forecast_3hours['main']['feels_like']
            weather_description = forecast_3hours['weather'][0]['main']

            # get forecast_weather emoji
            wd = code_to_smile_list.get(weather_description, f'\U0001F937')

            # collecting the weather forecast info
            forecast24_reply += (
                f"{time}:\n - Temp: {temp}°C;  {weather_description}{wd}\n"
                f" - Wind: {wind}m/s;  Feels like: {feels_like}°C\n"
            )
    # return the weather forecast to the user
    return forecast24_reply


# getting the weather forecast for 5 days
def get_5days_forecast(city):
    DAYS = 5
    # accessing the openweather API
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # extracting values from JSON Objects
    data = r.json()
    weather_5days_list = data['list']

    # initializing an empty list  to store the daily weather information
    daily_weather = []
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) # setting the time part to 00:00:00

    # iterating for DAYS number of times. Each iteration represents a day in the forecast
    for d in range(DAYS):
        daily = []
        day = today + timedelta(days=d) # the current date

        #  checking if the date of the item matches the current day
        for data in weather_5days_list:
            utc_time = datetime.utcfromtimestamp(data['dt']) # current UTC time
            # extracting values from JSON Objects, if the date matches
            if utc_time.date() == day.date():
                temp = data['main']['temp']
                weather_description = data['weather'][0]['main']
                wind = data['wind']['speed']
                feels_like = data['main']['feels_like']
                # add values to daily list
                daily.append({'temp': temp, 'weather_description': weather_description, 'wind': wind, 'feels_like': feels_like})
        # calculating average values for temperature, wind and feels_like condition
        avg_temp = round(sum([d['temp'] for d in daily]) / max(1, len(daily)), 1)
        desc = daily[0]['weather_description'] if len(daily) > 0 else 'N/A'
        avg_wind = round(sum([d['wind'] for d in daily]) / max(1, len(daily)), 1)
        avg_feels_like = round(sum([d['feels_like'] for d in daily]) / max(1, len(daily)), 1)

        # add values to daily_weather list
        daily_weather.append({'date': day.strftime('%A, %B %d'), 'temp': avg_temp, 'weather_description': weather_description,
                                  'wind': avg_wind, 'feels_like': avg_feels_like})

    # replying string with the city name and a header for the 5-day weather forecast
    reply = f"{city} weather forecast for 5 days:\n\n"

    # getting day_weather emoji and collecting the weather forecast info for each day
    for day_weather in daily_weather:
        wd = code_to_smile_list.get(day_weather['weather_description'], f'\U0001F937')
        reply += (
            f"\U000025FB{day_weather['date']}:\n - Temp: {day_weather['temp']}°C;  {day_weather['weather_description'].capitalize()}{wd}\n" \
            f" - Wind: {day_weather['wind']}m/s;  Feels like: {day_weather['feels_like']}°C\n\n")

    # return the weather forecast to the user
    return reply
