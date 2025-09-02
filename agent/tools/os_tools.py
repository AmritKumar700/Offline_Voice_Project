import os
import platform
import subprocess
import datetime

def open_application(app_name: str):
    """
    Opens a specified application on the user's operating system.
    :param app_name: The name of the application to open (e.g., 'Chrome', 'TextEdit').
    """
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", "-a", app_name], check=True)
        elif system == "Windows":
            os.startfile(app_name)
        else:  # Linux
            subprocess.run([app_name], check=True)
        return f"Successfully opened {app_name}."
    except Exception as e:
        return f"Error opening application '{app_name}': {e}. Please ensure it's installed and the name is correct."

def get_current_time():
    """Returns the current time in a readable format."""
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."