import os
import json
import time
import ssl
import wifi
import socketpool
import adafruit_requests
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
import microcontroller


SEND_DATA_PERIOD = 30
ADAFRUIT_API_URL = "https://io.adafruit.com"
PM10_STANDARD_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                   os.getenv("AIO_USERNAME"),
                                                   os.getenv("PM10_STANDARD_FEED_NAME")
                                                   )
PM25_STANDARD_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                    os.getenv("AIO_USERNAME"),
                                                    os.getenv("PM25_STANDARD_FEED_NAME")
                                                    )
PM100_STANDARD_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                       os.getenv("AIO_USERNAME"),
                                                       os.getenv("PM100_STANDARD_FEED_NAME")
                                                       )
PM10_ENV_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                   os.getenv("AIO_USERNAME"),
                                                   os.getenv("PM10_ENV_FEED_NAME")
                                                   )
PM25_ENV_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                    os.getenv("AIO_USERNAME"),
                                                    os.getenv("PM25_ENV_FEED_NAME")
                                                    )
PM100_ENV_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                       os.getenv("AIO_USERNAME"),
                                                       os.getenv("PM100_ENV_FEED_NAME")
                                                       )
PARTICLES03UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                   os.getenv("AIO_USERNAME"),
                                                   os.getenv("PARTICLES03UM_FEED_NAME")
                                                   )
PARTICLES05UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                    os.getenv("AIO_USERNAME"),
                                                    os.getenv("PARTICLES05UM_FEED_NAME")
                                                    )
PARTICLES10UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                       os.getenv("AIO_USERNAME"),
                                                       os.getenv("PARTICLES10UM_FEED_NAME")
                                                       )
PARTICLES25UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                    os.getenv("AIO_USERNAME"),
                                                    os.getenv("PARTICLES25UM_FEED_NAME")
                                                    )
PARTICLES50UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                       os.getenv("AIO_USERNAME"),
                                                       os.getenv("PARTICLES50UM_FEED_NAME")
                                                       )
PARTICLES100UM_FEED_URL = "{}/api/v2/{}/feeds/{}/data".format(ADAFRUIT_API_URL,
                                                       os.getenv("AIO_USERNAME"),
                                                       os.getenv("PARTICLES100UM_FEED_NAME")
                                                       )

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
reset_pin = None
pm25 = PM25_I2C(i2c, reset_pin)

print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"),
                   os.getenv("CIRCUITPY_WIFI_PASSWORD")
                   )
print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
print(f"My local IP address: {wifi.radio.ipv4_address}")
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())


def send_sensor_data(sensor_data_point, feed_location):
    payload = {
        "value": sensor_data_point
    }
    headers = {
        "Content-Type": "application/json",
        "X-AIO-Key": os.getenv("AIO_KEY")
    }
    try:
        response = requests.post(feed_location,
                                 data=json.dumps(payload),
                                 headers=headers
                                 )
        if response.status_code == 200:
            print("{} data sent successfully! {}".format(sensor_data_point, response.content))
        else:
            print("Failed to send {} data. {}".format(sensor_data_point, response.content))
    except wifi.WiFiError as error:
        print("WiFi error occurred:", str(error))
        print("Reconnecting to WiFi...")
        wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"),
                           os.getenv("CIRCUITPY_WIFI_PASSWORD")
                           )
        print("Connected to WiFi.")
        print(f"My IP address: {wifi.radio.ipv4_address}")
    except adafruit_requests.RequestError as error:
        print("Request error occurred:", str(error))
        print("Skipping request.")

print("Found PM2.5 sensor, reading data...")
while True:
    try:
        aqdata = pm25.read()
        pm10standard = aqdata["pm10 standard"]
        pm25standard = aqdata["pm25 standard"]
        pm100standard = aqdata["pm100 standard"]
        pm10env = aqdata["pm10 env"]
        pm25env = aqdata["pm25 env"]
        pm100env = aqdata["pm100 env"]
        particles03 = aqdata["particles 03um"]
        particles05 = aqdata["particles 05um"]
        particles10 = aqdata["particles 10um"]
        particles25 = aqdata["particles 25um"]
        particles50 = aqdata["particles 50um"]
        particles100 = aqdata["particles 100um"]
        send_sensor_data(sensor_data_point=pm10standard, feed_location=PM10_STANDARD_FEED_URL)
        send_sensor_data(sensor_data_point=pm25standard, feed_location=PM25_STANDARD_FEED_URL)
        send_sensor_data(sensor_data_point=pm100standard, feed_location=PM100_STANDARD_FEED_URL)
        send_sensor_data(sensor_data_point=pm10env, feed_location=PM10_ENV_FEED_URL)
        send_sensor_data(sensor_data_point=pm25env, feed_location=PM25_ENV_FEED_URL)
        send_sensor_data(sensor_data_point=pm100env, feed_location=PM100_ENV_FEED_URL)
        send_sensor_data(sensor_data_point=particles03, feed_location=PARTICLES03UM_FEED_URL)
        send_sensor_data(sensor_data_point=particles05, feed_location=PARTICLES05UM_FEED_URL)
        send_sensor_data(sensor_data_point=particles10, feed_location=PARTICLES10UM_FEED_URL)
        send_sensor_data(sensor_data_point=particles25, feed_location=PARTICLES25UM_FEED_URL)
        send_sensor_data(sensor_data_point=particles50, feed_location=PARTICLES50UM_FEED_URL)
        send_sensor_data(sensor_data_point=particles100, feed_location=PARTICLES100UM_FEED_URL)
        print()
        print("Concentration Units (standard)")
        print("---------------------------------------")
        print(
            "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
            % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
        )
        print("Concentration Units (environmental)")
        print("---------------------------------------")
        print(
            "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
            % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
        )
        print("---------------------------------------")
        print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
        print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
        print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
        print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
        print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
        print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
        print("---------------------------------------")
        time.sleep(SEND_DATA_PERIOD)

    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

