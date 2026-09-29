import network
import urequests
import time
import json
from machine import Pin

# Wokwi entry point. Current direction of data flow is API -> ESP32 -> LEDs:
# this program polls GET /predict/latest and does not read/send sensor values.
# =========================
# WIFI
# =========================

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# PUT YOUR LOCALTUNNEL URL HERE
# Replace the host with the active localtunnel HTTPS hostname.
SERVER_URL = "https://violet-groups-lie.loca.lt/predict/latest"
POLL_INTERVAL_SECONDS = 5
# =========================
# LED + BUZZER
# =========================

green_led = Pin(12, Pin.OUT)
yellow_led = Pin(14, Pin.OUT)
red_led = Pin(27, Pin.OUT)
buzzer = Pin(26, Pin.OUT)
wifi = network.WLAN(network.STA_IF)


def set_signals(risk):
    # Map the API's LOW/MEDIUM/HIGH output to the Wokwi GPIO LEDs/buzzer.
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)
    buzzer.value(0)

    if risk == "LOW":
        green_led.value(1)
    elif risk == "MEDIUM":
        yellow_led.value(1)
    elif risk == "HIGH":
        red_led.value(1)
        buzzer.value(1)
    elif risk != "OFF":
        raise ValueError("Unknown risk from API: " + str(risk))


def connect_wifi():
    if wifi.isconnected():
        return

    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):
        if wifi.isconnected():
            print("WiFi connected; IP:", wifi.ifconfig()[0])
            return
        time.sleep(1)
    raise OSError("WiFi connection timed out")


while True:
    response = None
    try:
        connect_wifi()
        # SERVER_URL must use the active tunnel URL to reach the local FastAPI
        # server; response['risk'] is then passed to set_signals() below.
        response = urequests.get(
            SERVER_URL,
            headers={"bypass-tunnel-reminder": "true"},
            timeout=10,
        )
        if response.status_code != 200:
            raise OSError("API returned HTTP " + str(response.status_code))

        result = response.json()
        risk = str(result["risk"]).upper()
        if risk not in ("LOW", "MEDIUM", "HIGH"):
            raise ValueError("API returned an invalid risk classification")

        print("API risk:", risk, "confidence:", result.get("confidence"))
        set_signals(risk)
    except Exception as error:
        set_signals("OFF")
        print("Prediction request failed; LEDs off:", error)
    finally:
        if response is not None:
            response.close()

    time.sleep(POLL_INTERVAL_SECONDS)