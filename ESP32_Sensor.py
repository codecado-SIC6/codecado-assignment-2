from machine import Pin, ADC
import time
import dht
import ujson
import utime as time
import urequests as requests

DEVICE_ID = "diphone"
TOKEN = "BBUS-BbyzvD0LJnauOGuqp3hmFBTtZOlhAq"

# Inisialisasi sensor dan LED
led = Pin(5, Pin.OUT)
sensor = dht.DHT11(Pin(4))
ldr = ADC(Pin(36))  # Sensor LDR terhubung ke pin ADC


def do_connect():
    import network
    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect('dipaaa', 'honeymon')
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ifconfig())


def send_data_to_ubidots(temperature, humidity, day_night):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "day_night": day_night,
    }
    response = requests.post(url, json=data, headers=headers)
    #print("Response:", response.text)
    print("Done Sending Data to Ubidots!")


def check_day_night():
    ldr_value = ldr.read()  # Membaca nilai ADC dari sensor LDR
    print("LDR Value:", ldr_value)
    if ldr_value < 1000:  # Nilai threshold untuk malam hari (sesuaikan sesuai kondisi)
        led.value(1)  # Nyalakan LED jika malam
        return "night"
    else:
        led.value(0)  # Matikan LED jika siang
        return "day"


# Connect to WiFi
do_connect()

while True:
    try:
        sensor.measure()  # Membaca parameter dari sensor DHT11
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        day_night = check_day_night()

        print(f"Temperature: {temperature}C, Humidity: {humidity}%, Time: {day_night}")
        send_data_to_ubidots(temperature, humidity, day_night)
        
        time.sleep(1)
    except Exception as e:
        print("Error:", e)
