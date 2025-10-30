# on-board goodies
import sys
import os
import gc
import uasyncio
import urequests as requests
from time import sleep, gmtime, localtime
import network
from machine import Pin, reset

# Class that puts things on the screen
from include.solar_display import SolarDisplay

# Global variables so it can be persistent
solar_usage = {}
# led_bright = 800
CRED_FILE = const("config/credentials.env")
SOLIS_FILE = const("config/solis.env")

clear_btn = Pin(0, Pin.IN, Pin.PULL_UP)
bl_pin = Pin(21, Pin.OUT)
bl_state = True
# hours to turn the backlight off and on again
BL_NIGHT_START = const(23)
BL_NIGHT_END = const(5)

display=SolarDisplay()

bl_pin.on()
gc.collect()


# Local time doings
def stringTime(thisTime):
    year, month, date, hour, minute, second, week_day, year_day = thisTime
    week_day_lookup = b"MonTueWedThuFriSatSun"
    month_lookup = b"JanFebMarAprMayJunJulAugSepOctNovDec"
    stringTime = (
        week_day_lookup.decode()[week_day * 3 : week_day * 3 + 3]
        + ", "
        + f"{date:02}"
        + " "
        + month_lookup.decode()[(month - 1) * 3 : (month - 1) * 3 + 3]
        + " "
        + f"{year:02}"
        + " "
        + f"{hour:02}"
        + ":"
        + f"{minute:02}"
        + ":"
        + f"{second:02}"
        + " GMT"
    )
    return stringTime


def get_ha(ha_info):
    headers={"Authorization": "Bearer "+ha_info['ha_token'].decode("utf-8"),
             "content-type": "application/json"}
    solar_dict = {}
    ha_url = ha_info["ha_url"].decode("utf-8")+"/api/states/input_text.solar_display_data"
    print(f"Getting data...")
    try:
        gc.collect()
        resp=requests.get(url=ha_url,headers=headers,timeout=10)
        solar_dict=resp.json()['attributes']['info']
        print(f"Here's what I got: {solar_dict}")
    except Exception as e:
        print(f" ... o no!\nI couldn't get the data from {ha_url}")
        print(f"Exception: {e}")

    return solar_dict

def validate_data(solar_usage):
    # Sanity check printing business
    for each_param in ["timestamp",
                       "solar_in",
                       "battery_per",
                       "grid_in",
                       "power_used",
                       "solar_today",
                       "export_today",
                       "grid_in_today",
                       "presence",
                       "cur_rate",
                       "solis_charging",
                       "solis_discharging",
                       "power_up"]:
        if each_param in solar_usage:
            print(f"{each_param} is {solar_usage[each_param]}")
        # Extra bit to sort out occasional negative export
            if each_param=="export_today":
                if float(solar_usage[each_param])<0:
                    solar_usage[each_param]="0.0"   
        else:
            print(f"{each_param} is empty - skipping this run")
            return False
    return solar_usage

def backlight_control(timestamp):
    global bl_state
    timestamp_hour=timestamp.split("T")[1][:2]
    if timestamp_hour==("%02d" % (BL_NIGHT_END)) and not(bl_state):
        print("Turning backlight on")
        bl_state=True
        bl_pin.on()
    if timestamp_hour==("%02d" % (BL_NIGHT_START)) and bl_state:
        print("Turning backlight off")
        bl_state=False
        bl_pin.off()

# Display function - does all the doings
def display_data(solar_usage,force=False):
    if solar_usage:=validate_data(solar_usage):
      print("Valid data received..")
      if solar_usage['timestamp']!=solar_usage['prev_timestamp'] or force:
        print("Timestamp changed - refreshing full display")
        gc.collect()
        display.solar_data(solar_usage)
        backlight_control(solar_usage["timestamp"]) # do stuff with the backlight
        # Update the previous values if they're different
        if solar_usage['timestamp']!=solar_usage['prev_timestamp']:
          solar_usage["prev_battery_int"] = int(float(solar_usage["battery_per"]))
          solar_usage["prev_timestamp"] = solar_usage["timestamp"]
      else:
        # Just update the presence
        print("Timestamp hasn't changed - only updating presence")
        display.presence(solar_usage)

    else: # data not valid
      display.status_invalid_data()

# Coroutine: get the solis data every 45 seconds
async def timer_ha_data(ha_info):
    global solar_usage
    solar_usage["prev_battery_int"] = 0
    solar_usage["prev_timestamp"] = "0"
    while True:
        display.status_checking()
        await uasyncio.sleep(1)
        gc.collect()
        solar_dict = get_ha(ha_info)
        if "timestamp" in solar_dict:
            display.status_ok()
            solar_usage.update(solar_dict)
            display_data(solar_usage)
        else:
            display.status_failed()
            print("No data returned")
            if "resp" in solar_dict:
                solar_usage["resp"] = solar_dict["resp"]
        await uasyncio.sleep(45)


# Coroutine: reset button
async def wait_clear_button():
    btn_count = 0
    bl_count=60
    btn_max = 75
    bl_max=90
    while True:
        if clear_btn.value() == 1:
            btn_count = 0
        if clear_btn.value() == 0:
            print(f"Pressed - count is {str(btn_count)}")
            bl_count=0
            btn_count+=1
        if btn_count >= btn_max:
            sleep(2)
            os.remove(CRED_FILE)
            reset()
        if not(bl_state): # only do this if the backlight is off
            if bl_count<bl_max:
                bl_count+=1
                bl_pin.on()
            else:
                bl_count=bl_max
                bl_pin.off()
        await uasyncio.sleep(0.04)

async def main(ha_info):
    # Main loop
    # Get the ha data
    display.clear()
    gc.collect()
    await uasyncio.sleep(2)
    uasyncio.create_task(timer_ha_data(ha_info))

    while True:
        await wait_clear_button()

def setup():
    ha_info = {}
    # Now separate credentials
    # global CRED_FILE
    # global SOLIS_FILE

    # populate the ha_info dictionary:
    try:
        with open(CRED_FILE, "rb") as f:
            contents = f.read().split(b",")
            if len(contents) == 4:
                (
                    ha_info["wifi_ssid"],
                    ha_info["wifi_password"],
                    ha_info["ha_url"],
                    ha_info["ha_token"],
                ) = contents
    except OSError:
        print("No or invalid credentials file - please do a full reset and start again")
        sys.exit()
    # Define the URL list

    ha_api={"solar_in":"sensor.solis_ac_output_total_power",     # current solar power
        "power_used": "sensor.solis_total_consumption_power", # current consumption
        "grid_in": "sensor.solis_power_grid_total_power",  # current grid power
        "battery_per": "sensor.solis_remaining_battery_capacity",  # % battery remaining
        "export_today":"sensor.solis_daily_on_grid_energy",          # exported today
        "solar_today":"sensor.solis_energy_today",                   # solar today
        "grid_in_today":"sensor.solis_daily_grid_energy_purchased"}    # imported today
    ha_info['ha_api']=ha_api

    # Configure the network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Connecting..", end="")
    wlan.connect(ha_info["wifi_ssid"], ha_info["wifi_password"])
    ip_address, net_mask, default_gateway, dns = wlan.ifconfig()
    wifi_count = 0
    while ip_address == "0.0.0.0" and wifi_count < 30:
        print(".", end="")
        sleep(1)
        ip_address, net_mask, default_gateway, dns = wlan.ifconfig()
        wifi_count += 1

    if ip_address == "0.0.0.0":
        print("No WiFi connection - please check details in credentials.env")
        sys.exit()
    gc.collect()

    # display IP address
    print("\nWifi connected - IP address is: " + ip_address)
    display.ip_address(ip_address)

    sleep(1)
    # clear down all the doings
    del sys.modules["captive_portal"]
    del sys.modules["captive_dns"]
    del sys.modules["captive_http"]
    del sys.modules["credentials"]
    del sys.modules["server"]
    gc.collect()

    return(ha_info)

if __name__ == "__main__":
    ha_info=setup()

    try:
        # Start event loop and run entry point coroutine
        uasyncio.run(main(ha_info))
    except KeyboardInterrupt:
        pass
