from machine import Pin, ADC
import time
import dht
import ujson
import network
import urequests as requests

# WiFi credentials
WIFI_SSID = "bukansaya"
WIFI_PASS = "empatlimaenam"

# Ubidots credentials
DEVICE_ID = "codecado"
TOKEN = "BBUS-BzRZEWnxy555pRBZdfGr6IRcB6U4Bz"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID

# Flask API URL (ganti dengan IP Flask yang sesuai)
API_URL = "http://192.168.202.60:5000/sensor"

# Inisialisasi sensor dan LED
sensor = dht.DHT11(Pin(4))
ldr = ADC(Pin(36))
ldr.atten(ADC.ATTN_11DB)
led = Pin(5, Pin.OUT)

# Fungsi koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 15  # Tunggu maksimal 15 detik
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print("Connected! IP Address:", wlan.ifconfig()[0])
    else:
        print("WiFi connection failed!")

# Fungsi deteksi siang/malam
def get_light_status():
    ldr_value = ldr.read()
    if ldr_value < 2000:
        return "Night", ldr_value
    else:
        return "Day", ldr_value

# Fungsi mengirim data ke Ubidots
def send_data_to_ubidots(temperature, humidity, light_status, ldr_value):
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "light_status": light_status,
        "ldr_value": ldr_value
    }
    try:
        response = requests.post(UBIDOTS_URL, json=data, headers=headers)
        print("Data sent to Ubidots!")
    except Exception as e:
        print("Failed to send data to Ubidots:", e)

# Fungsi mengirim data ke MongoDB melalui Flask API
def send_data_to_mongo(temperature, humidity, light_status, ldr_value):
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "light_status": light_status,
        "ldr_value": ldr_value,
        "timestamp": time.time()
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print("Data sent to MongoDB!")
    except Exception as e:
        print("Failed to send data to MongoDB:", e)

# Mulai koneksi WiFi
connect_wifi()

# Loop utama
while True:
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        light_status, ldr_value = get_light_status()

        # Kontrol LED: Nyalakan saat malam atau suhu > 40°C
        if light_status == "Night" or temperature > 40:
            led.value(1)
        else:
            led.value(0)

        print(f"Temperature: {temperature}C, Humidity: {humidity}%, Light: {light_status}, LDR: {ldr_value}")
        send_data_to_ubidots(temperature, humidity, light_status, ldr_value)
        send_data_to_mongo(temperature, humidity, light_status, ldr_value)

        time.sleep(5)  # Kirim data setiap 5 detik
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
