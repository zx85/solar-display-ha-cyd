import json

# This is now for the Solis Cloud Monitoring HACS integration


@service
def get_solar_data():
    states = {}
    state_list = {
        "solar_in": "sensor.hall_solis_inverter_inverter_ac_power",  # current solar power
        "power_used": "sensor.hall_solis_inverter_home_load_power",  # current consumption
        "grid_in": "sensor.hall_solis_inverter_grid_active_power",  # current grid power
        "battery_per": "sensor.hall_solis_inverter_battery_soc",  # % battery remaining
        "export_today": "sensor.hall_solis_inverter_grid_export_today",  # exported today
        "solar_today": "sensor.hall_solis_inverter_inverter_generation_today",  # solar today
        "grid_in_today": "sensor.hall_solis_inverter_grid_import_today",  # grid today
        "runtime_today": "sensor.hall_solis_inverter_inverter_runtime_today",
        "cur_rate": "sensor.octopus_energy_electricity_18p0906942_1012934837063_current_rate",  # current Octopus rate
        "solis_charging": "input_boolean.solar_battery_charging",  # Solis charging
        "solis_discharging": "input_boolean.solar_battery_discharging",  # Solis discharging
        "power_up": "input_boolean.octopus_power_up_active",  # Octopus Power ups
        "car_charging": "select.myenergi_zappi_2_charge_mode",  # Zappi charge mode
    }
    for state_label, state_name in state_list.items():
        states[state_label] = state.get(state_name)
    states["timestamp"] = state.get(state_list["runtime_today"])
    try:
        states["bins"] = state.getattr(sensor.upcoming_bins)["bins"]
    except:
        states["bins"] = ""
    presence_string = ""
    for person in ["james", "Beth", "Chris", "Lenni"]:
        if state.get(f"device_tracker.{person.lower()}_phone") == "home":
            presence_string += (person[:1]).replace("L", "LE")
    states["presence"] = presence_string
    state.set("input_text.solar_display_data", value=states["timestamp"], info=states)
