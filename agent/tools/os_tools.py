import os
import platform
import subprocess
import datetime
from thefuzz import process


def open_application(app_name: str):
    """Deep scans for Apps using fuzzy matching to handle nicknames."""
    if platform.system() != "Darwin":
        return "OS not supported."

    try:
        app_dirs = ['/Applications', '/System/Applications', '/System/Applications/Utilities']
        apps = []
        for d in app_dirs:
            if os.path.exists(d):
                apps.extend([f for f in os.listdir(d) if f.endswith('.app')])

        choices = {f.replace('.app', ''): f for f in apps}
        best_match_key, score = process.extractOne(app_name, list(choices.keys()))

        if score > 75:
            actual_name = choices[best_match_key]
            subprocess.run(["open", "-a", actual_name], check=True)
            return f"Opening {actual_name}."

        return f"I couldn't find an application named '{app_name}'."
    except Exception as e:
        return f"Error: {str(e)}"


def manage_desktop(item_name: str, action: str = "open"):
    """Handles ONLY Desktop files and folders. Prevents system-wide errors."""
    desktop_path = os.path.expanduser("~/Desktop")
    item_path = os.path.join(desktop_path, item_name)

    try:
        if action == "create_folder":
            os.makedirs(item_path, exist_ok=True)
            return f"Folder '{item_name}' created on Desktop."

        if action == "open":
            if os.path.exists(item_path):
                subprocess.run(["open", item_path], check=True)
                return f"Opening '{item_name}' from Desktop."
            return f"File '{item_name}' not found on Desktop."

    except Exception as e:
        return f"Desktop Tool Error: {str(e)}"


def get_current_time():
    return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."