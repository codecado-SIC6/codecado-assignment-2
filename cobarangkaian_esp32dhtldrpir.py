from machine import Pin, ADC
import time
import dht
import ujson
import utime as time
import urequests as requests

DEVICE_ID = "codecado-sic6"
TOKEN = "BBUS-Od5RtNenrZA88ROs8iPiL4nCnsPNXC"

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


def send_data_to_ubidots(temperature, humidity, light_status, ldr_value):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "light_status": light_status,
        "ldr_value": ldr_value
    }
    response = requests.post(url, json=data, headers=headers)
    #print("Response:", response.text)
    print("Done Sending Data to Ubidots!")


def get_light_status():
    day = 0
    night = 1
    ldr_value = ldr.read()
    if ldr_value < 3000:  # Threshold untuk menentukan siang/malam
        return day, ldr_value
    else:
        return night, ldr_value


# Connect to WiFi
do_connect()

while True:
    try:
        sensor.measure()  # Membaca parameter dari sensor DHT11
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        light_status, ldr_value = get_light_status()  

        # Kontrol LED: Nyalakan saat malam atau suhu > 40°C
        day = 0
        night = 1
        if light_status == night or temperature > 40:
            led.value(1)
        else:
            led.value(0)

        print(f"Temperature: {temperature}C, Humidity: {humidity}%, Light: {light_status}, LDR: {ldr_value}")
        send_data_to_ubidots(temperature, humidity, light_status, ldr_value)
        
        time.sleep(1)
    except Exception as e:
        print(e)
