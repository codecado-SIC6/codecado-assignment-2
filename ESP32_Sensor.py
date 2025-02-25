from machine import Pin, ADC
import time
import dht
import ujson
import utime as time
import urequests as requests
import network

# WiFi credentials
WIFI_SSID = "bukansaya"
WIFI_PASS = "empatlimaenam"

# Ubidots credentials
UBIDOTS_DEVICE_ID = "codecado-sic6"
UBIDOTS_TOKEN = "BBUS-BzRZEWnxy555pRBZdfGr6IRcB6U4Bz"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + UBIDOTS_DEVICE_ID

# Flask API URL (ganti dengan IP Flask yang sesuai)
FLASK_API_URL = "http://192.168.202.60:5000/sensor"

# Inisialisasi sensor dan LED
led = Pin(5, Pin.OUT)
sensor = dht.DHT11(Pin(4))
ldr = ADC(Pin(36))  # Sensor LDR terhubung ke pin ADC


def connect_wifi():
    """
    Fungsi untuk ESP32 connect ke WiFi 
    """
    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect('dipaaa', 'honeymon')
        while not sta_if.isconnected():
            pass
    print('Network config:', sta_if.ifconfig())

def send_data_to_ubidots(temperature, humidity, light_status, ldr_value):
    """
    Mengirimkan data ke platform Ubidots

    Args:
        temperature (integer): Besar suhu yang didapat dari sensor DHT11
        humidity (integer): Besar kelembapan yang didapat dari sensor DHT11
        light_status (integer): Status lampu hidup/mati (1/0)
        ldr_value (integer): Besar nilai cahaya yang ditangkap sensor LDR
    """
    headers = {"Content-Type": "application/json", "X-Auth-Token": UBIDOTS_TOKEN} # Header untuk akses Ubidots
    
    # Membuat data sensor ke format JSON 
    data = {
        "temp": temperature,
        "humidity": humidity,
        "light_status": light_status,
        "ldr_value": ldr_value
    }
    
    # Mengirimkan (POST) data ke Ubidots
    response = requests.post(UBIDOTS_URL, json=data, headers=headers)
    
    # Mengecek hasil response
    print("Response:", response.text)
    print("Done Sending Data to Ubidots!")
    
def send_data_to_mongo(temperature, humidity, light_status, ldr_value):
    """
    Mengirimkan data sensor ke database di MongoDB melalui Flask app.

    Args:
        temperature (integer): Besar suhu yang didapat dari sensor DHT11
        humidity (integer): Besar kelembapan yang didapat dari sensor DHT11
        light_status (integer): Status lampu hidup/mati (1/0)
        ldr_value (integer): Besar nilai cahaya yang ditangkap sensor LDR
    """
    # menyusun data sensor ke format JSON yang diinginkan 
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "light_status": light_status,
        "ldr_value": ldr_value,
        "timestamp": time.time()
    }
    
    headers = {"Content-Type": "application/json"} # Header untuk akses Flask
    try:
        # Mengirim (POST) data ke database melalui Flask app
        response = requests.post(FLASK_API_URL, json=payload, headers=headers)
        print("Data sent to MongoDB!")
    except Exception as e:
        # Error handling
        print("Failed to send data to MongoDB:", e)

def get_light_status():
    """
    Mendapatkan status pencahayaan. 
    Jika terang/siang/day, maka LED mati. 
    Jika gelap/malam/night, maka LED hidup.

    Returns:
        ldr_value (integer): value cahaya yang ditangkap LDR sensor.  
        day/night (bool) : value nya 0 untuk day dan 1 untuk night.
    """
    day = 0
    night = 1
    ldr_value = ldr.read() # Membaca data sensor LDR
    if ldr_value < 3000:  # Threshold untuk menentukan siang/malam
        return day, ldr_value
    else:
        return night, ldr_value


# Connect to WiFi
connect_wifi()

# Main loop
while True:
    try:
        sensor.measure()  # Membaca parameter dari sensor DHT11
        temperature = sensor.temperature()  # Membaca data temperature (suhu)
        humidity = sensor.humidity()  # Membaca data humidity (kelembapan)
        light_status, ldr_value = get_light_status()  # Mendapat status pencahayaan dan LED

        # Kontrol LED: Nyalakan saat malam atau suhu > 40°C
        day = 0
        night = 1
        if light_status == night or temperature > 40:
            led.value(1)
        else:
            led.value(0)

        # Print hasil data yang akan dikirim
        print(f"Temperature: {temperature}C, Humidity: {humidity}%, Light: {light_status}, LDR: {ldr_value}")
        
        # Mengirim data ke Ubidots
        send_data_to_ubidots(temperature, humidity, light_status, ldr_value)
        
        # Mengirim data ke database di MongoDB
        send_data_to_mongo(temperature, humidity, light_status, ldr_value)
        
        time.sleep(1)
    except Exception as e:
        print(e)