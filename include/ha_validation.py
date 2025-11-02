"""
Home Assistant Data Validation for MicroPython
Validates data returned from Home Assistant API calls to ensure numeric fields
contain valid numbers and not 'unknown' or None values.
"""

import math

def is_valid_number(value):
    """
    Check if a value can be converted to a valid number.
    Returns True for valid numbers (including negative and float), False otherwise.
    """
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return not math.isnan(value)
    if isinstance(value, str):
        if value.lower() in ['unknown', 'none', 'null', 'nan']:
            return False
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    return False

def is_valid_string(value, allowed_values=None):
    """
    Check if a string value is valid (not None, not 'unknown', etc.).
    Optionally check against a list of allowed values.
    """
    if value is None:
        return False
    if not isinstance(value, str):
        return False
    if value.lower() in ['unknown', 'none', 'null']:
        return False
    if allowed_values and value not in allowed_values:
        return False
    return True

def validate_ha_data(data):
    """
    Validate Home Assistant data dictionary.
    Returns a tuple (is_valid, errors, warnings) where:
    - is_valid: True if all critical fields are valid
    - errors: List of validation errors
    - warnings: List of validation warnings (non-critical issues)
    """
    if not isinstance(data, dict):
        return False, ["Data is not a dictionary"], []
    
    errors = []
    warnings = []
    critical_fields = ['grid_in', 'solar_in', 'power_used', 'battery_per', 
                      'solar_today', 'export_today', 'grid_in_today', 'cur_rate']
    
    # Define expected field types
    numeric_fields = ['grid_in', 'solar_in', 'power_used', 'battery_per', 
                     'solar_today', 'export_today', 'grid_in_today', 'cur_rate']
    
    string_fields = {
        'car_charging': ['Stopped', 'Charging', 'Complete'],
        'solis_charging': ['on', 'off'],
        'power_up': ['on', 'off'],
        'solis_discharging': ['on', 'off'],
        'presence': None  # Any non-empty string is valid
    }
    
    # Check for missing critical fields
    for field in critical_fields:
        if field not in data:
            errors.append(f"Missing critical field: {field}")
    
    # Validate numeric fields
    for field in numeric_fields:
        if field in data:
            if not is_valid_number(data[field]):
                if field in critical_fields:
                    errors.append(f"Invalid numeric value in critical field '{field}': {data[field]}")
                else:
                    warnings.append(f"Invalid numeric value in field '{field}': {data[field]}")
    
    # Validate string fields
    for field, allowed_values in string_fields.items():
        if field in data:
            if not is_valid_string(data[field], allowed_values):
                warnings.append(f"Invalid string value in field '{field}': {data[field]}")
    
    # Special validation for timestamp
    if 'timestamp' in data and data['timestamp'] is None:
        warnings.append("Timestamp is None - data may be stale")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def safe_convert_to_float(value, default=0.0):
    """
    Safely convert a value to float, returning default if conversion fails.
    """
    if not is_valid_number(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_convert_to_int(value, default=0):
    """
    Safely convert a value to int, returning default if conversion fails.
    """
    if not is_valid_number(value):
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def filter_valid_data(data):
    """
    Filter and clean the data, returning only valid numeric values.
    Non-numeric values are replaced with 0.0 for floats and 0 for ints.
    """
    if not isinstance(data, dict):
        return {}
    
    numeric_fields = ['grid_in', 'solar_in', 'power_used', 'battery_per', 
                     'solar_today', 'export_today', 'grid_in_today', 'cur_rate']
    
    cleaned_data = {}
    for field, value in data.items():
        if field in numeric_fields:
            cleaned_data[field] = safe_convert_to_float(value)
        else:
            cleaned_data[field] = value
    
    return cleaned_data

def get_data_quality_score(data):
    """
    Calculate a data quality score (0-100) based on the percentage of valid fields.
    """
    if not isinstance(data, dict) or not data:
        return 0
    
    total_fields = len(data)
    valid_fields = 0
    
    for field, value in data.items():
        if field in ['grid_in', 'solar_in', 'power_used', 'battery_per', 
                    'solar_today', 'export_today', 'grid_in_today', 'cur_rate']:
            if is_valid_number(value):
                valid_fields += 1
        elif field in ['car_charging', 'solis_charging', 'power_up', 'solis_discharging']:
            if is_valid_string(value):
                valid_fields += 1
        else:
            # For other fields, just check they're not None
            if value is not None:
                valid_fields += 1
    
    return int((valid_fields / total_fields) * 100)