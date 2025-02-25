from machine import Pin, ADC
import time
import dht
import ujson
import network
import urequests as requests

# WiFi credentials
WIFI_SSID = "bukansaya"
WIFI_PASS = "empatlimaenam"

# URL Flask API (ganti dengan IP Flask yang sesuai)
API_URL = "http://192.168.1.100:5000/sensor"

# Inisialisasi sensor
sensor = dht.DHT11(Pin(4))
ldr = ADC(Pin(36))
ldr.atten(ADC.ATTN_11DB)
led = Pin(5, Pin.OUT)

# Fungsi koneksi WiFi dengan retry
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
def check_day_night():
    ldr_value = ldr.read()
    print("LDR Value:", ldr_value)
    if ldr_value < 1000:
        led.value(1)  # Nyalakan LED jika malam
        return "night"
    else:
        led.value(0)  # Matikan LED jika siang
        return "day"

# Fungsi mengirim data dengan retry
def send_data(temperature, humidity, day_night):
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time(),
        "day_night": day_night
    }
    headers = {'Content-Type': 'application/json'}

    for attempt in range(3):  # Coba kirim ulang hingga 3 kali jika gagal
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            print("Data Sent:", response.json())
            return
        except Exception as e:
            print(f"Failed to send data (attempt {attempt+1}):", e)
            time.sleep(2)  # Tunggu 2 detik sebelum mencoba lagi

# Mulai koneksi WiFi
connect_wifi()

# Loop utama
while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        day_night = check_day_night()

        print(f"Temperature: {temp}C, Humidity: {hum}%, Time: {day_night}")
        send_data(temp, hum, day_night)

        time.sleep(5)  # Kirim data setiap 5 detik

    except Exception as e:
        print("Error:", e)
        time.sleep(5)
