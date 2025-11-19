''' supplier_database.py file that will host sample database of material price '''
# SIMULATED DATABASE for IOT Component Supplier Prices -- SAMPLE database

# Sample IOT components
COMPONENTS = {
    "ESP32_WIFI": "ESP32 WiFi Microcontroller Module",
    "RELAY_5V": "5V Relay Switch Module",
    "TEMP_SENSOR": "DHT22 Temperature & Humidity Sensor",
    "POWER_5V": "5V 2A Power Supply",
    "LCD_DISPLAY": "16x2 LCD Display Module"
}

# Three suppliers with different pricing
SUPPLIER_PRICES = {
    "Supplier_A_Electronics": {
        "ESP32_WIFI": {"current_price": 4.50, "last_month_price": 4.20},
        "RELAY_5V": {"current_price": 1.80, "last_month_price": 1.75},
        "TEMP_SENSOR": {"current_price": 3.20, "last_month_price": 3.00},
        "POWER_5V": {"current_price": 2.50, "last_month_price": 2.40},
        "LCD_DISPLAY": {"current_price": 5.80, "last_month_price": 5.50}
    },
    "Supplier_B_Components": {
        "ESP32_WIFI": {"current_price": 4.30, "last_month_price": 4.25},
        "RELAY_5V": {"current_price": 1.95, "last_month_price": 1.90},
        "TEMP_SENSOR": {"current_price": 3.40, "last_month_price": 2.90},
        "POWER_5V": {"current_price": 2.45, "last_month_price": 2.42},
        "LCD_DISPLAY": {"current_price": 6.00, "last_month_price": 5.80}
    },
    "Supplier_C_Global": {
        "ESP32_WIFI": {"current_price": 4.60, "last_month_price": 4.55},
        "RELAY_5V": {"current_price": 1.75, "last_month_price": 1.70},
        "TEMP_SENSOR": {"current_price": 3.50, "last_month_price": 3.45},
        "POWER_5V": {"current_price": 2.30, "last_month_price": 2.25},
        "LCD_DISPLAY": {"current_price": 5.70, "last_month_price": 5.65}
    }
}

def get_all_prices_for_component(component_code: str) -> dict: #retrieve component price, returns a dictionary 
    if component_code not in COMPONENTS:
        return {
            "status": "error",
            "error_message": f"Component '{component_code}' not found"
        }

    all_prices = []
    for supplier_name in SUPPLIER_PRICES.keys():
        price_data = SUPPLIER_PRICES[supplier_name][component_code]
        all_prices.append({
            "supplier": supplier_name,
            "current_price": price_data["current_price"],
            "last_month_price": price_data["last_month_price"]
        })

    return {
        "status": "success",
        "component_code": component_code,
        "component_name": COMPONENTS[component_code],
        "prices": all_prices
    }
