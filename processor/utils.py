from datetime import datetime
import pytz
import jinja2

def datetime_format(value, timezone="UTC", format="%Y-%m-%d %H:%M:%S"):
    """
    Converts an ISO 8601 string to a datetime object and formats it in the specified timezone.
    :param value: ISO 8601 formatted date string (e.g., '2024-09-07T02:18:57Z').
    :param timezone: Timezone name (e.g., 'Asia/Kolkata', 'America/New_York').
    :param format: The date format to output.
    """
    try:
        # Parse the ISO 8601 date string (assume UTC)
        utc_date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        
        # Define the UTC timezone
        utc_zone = pytz.utc
        utc_date = utc_zone.localize(utc_date)

        # Convert to the specified timezone
        target_zone = pytz.timezone(timezone)
        local_date = utc_date.astimezone(target_zone)
        
        # Format the date in the target timezone
        return local_date.strftime(format)
    
    except (ValueError, TypeError, pytz.UnknownTimeZoneError):
        return value  # Return the original value if parsing or timezone conversion fails



def setup_jinja2_env(template_path="."):
    template_loader = jinja2.FileSystemLoader(searchpath=template_path)
    env = jinja2.Environment(loader=template_loader)
    
    # Add the custom filter
    env.filters['datetime_format'] = datetime_format
    
    return env
