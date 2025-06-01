import re
from datetime import datetime, timedelta
import os
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.transport.requests import AuthorizedSession

from config.config import Config

creds = None
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
MAX_SIZE = (800, 1200)

# Load the configuration
Config.load_config("config.yaml")

saved_input_path = 'secrets/savedInput.json'
if os.path.exists(saved_input_path):
    with open(saved_input_path, 'r') as f:
        saved_input = json.load(f)
else:
    saved_input = {}


def update_saved_input():
    with open(saved_input_path, 'w') as f:
        json.dump(saved_input, f)


saved_uploads_path = 'secrets/savedUploadLinks.json'
if os.path.exists(saved_uploads_path):
    with open(saved_uploads_path, 'r') as f:
        saved_uploads = json.load(f)
else:
    saved_uploads = {}


def update_saved_uploads():
    with open(saved_uploads_path, 'w') as f:
        json.dump(saved_uploads, f)


if not os.path.exists('secrets/'):
    os.mkdir('secrets')

if os.path.exists('secrets/savedToken.json'):
    creds = Credentials.from_authorized_user_file(
        'secrets/savedToken.json', SCOPES)

print(creds.token_state)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            flow = InstalledAppFlow.from_client_secrets_file(
                Config.get("GOOGLE_PHOTOS_CREDS"), SCOPES)
            creds = flow.run_local_server()
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            Config.get("GOOGLE_PHOTOS_CREDS"), SCOPES)
        creds = flow.run_local_server()

    # Save the credentials for the next run
    with open('secrets/savedToken.json', 'w') as token:
        token.write(creds.to_json())

authed_session = AuthorizedSession(creds)


class EntryProcessor:
    additional_tags = []
    tag_prefix = ""
    default_filename = ""
    SEARCH_WINDOW = Config.get("GOOGLE_PHOTOS_SEARCH_WINDOW")

    @classmethod
    def initialize(cls):
        cls.additional_tags = Config.get("ADDITIONAL_TAGS", [])
        cls.tag_prefix = Config.get("TAG_PREFIX", "")
        cls.default_filename = Config.get("DEFAULT_FILENAME", "")
        cls.force_upload = Config.get("FORCE_UPLOAD", False)
        cls.upload_to_google_photos = Config.get("UPLOAD_TO_GOOGLE_PHOTOS", True)

    def __init__(self):
        self.media_dict = {}  # Initialize dict in the constructor

    def add_entry_to_dict(self, media):
        identifier = media["identifier"]
        if identifier in self.media_dict:
            raise ValueError(
                f"Identifier {identifier} already exists in the dictionary.")
        else:
            self.media_dict[identifier] = media

    def replace_entry_id_with_info(self, term):
        return self.get_entry_info(self.media_dict[term.group(2)])

    def get_entry_info(self, entry):
        return str(entry)

    def upload_to_GPhotos(self, file_location, file_name, date, title):
        # Check if uploading to Google Photos is disabled in config
        if hasattr(self, 'upload_to_google_photos'):
            upload_enabled = self.upload_to_google_photos
        elif hasattr(EntryProcessor, 'upload_to_google_photos'):
            upload_enabled = EntryProcessor.upload_to_google_photos
        else:
            upload_enabled = True
        if not upload_enabled:
            print(f"UPLOAD_TO_GOOGLE_PHOTOS is False, skipping upload for {file_name}.")
            return "://"

        file_path = os.path.join(file_location, file_name)
        if os.path.exists(file_path):
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                date = date_obj.strftime("%m/%d/%Y")
            except ValueError:
                date = ""
            with open(file_path, "rb") as f:
                contents = f.read()

                print("Uploading %s to Google Photos" % file_path)
                response = authed_session.post(
                    "https://photoslibrary.googleapis.com/v1/uploads",
                    headers={},
                    data=contents)
                upload_token = response.text

                response = authed_session.post(
                    'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
                    headers={'content-type': 'application/json'},
                    json={
                        "newMediaItems": [{
                            "description": title + " " + date,
                            "simpleMediaItem": {
                                "uploadToken": upload_token,
                                "fileName": "%s" % file_name
                            }
                        }]
                    }
                )
                try:
                    return_url = response.json()['newMediaItemResults'][0]['mediaItem']['productUrl']
                except (KeyError, IndexError, TypeError):
                    return_url = "://"
                print("New URL: " + return_url)
                return return_url
        else:
            print("Error: cannot find %s to upload to Google Photos" % file_path)
            return "UPLOAD NOT FOUND"

    def set_GPhotos_title(self, title):
        self.title = title

    def get_GPhotos(self, date, mime_prefix):
        date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        lower_limit = date_obj - timedelta(days=self.SEARCH_WINDOW)
        upper_limit = date_obj + timedelta(days=self.SEARCH_WINDOW)

        nextPageToken = None
        idx = 0
        mediaItems = []
        while True:
            idx += 1
            response = authed_session.post(
                'https://photoslibrary.googleapis.com/v1/mediaItems:search',
                headers={'content-type': 'application/json'},
                json={
                    "pageSize": 100,
                    "pageToken": nextPageToken,
                    "filters": {
                        "dateFilter": {
                            "ranges": [{
                                "startDate": {
                                    "year": lower_limit.year,
                                    "month": lower_limit.month,
                                    "day": lower_limit.day,
                                },
                                "endDate": {
                                    "year": upper_limit.year,
                                    "month": upper_limit.month,
                                    "day": upper_limit.day,
                                }
                            }]
                        }
                    }
                })

            response_json = response.json()
            if len(response_json) != 0:
                if "mediaItems" in response_json:
                    for media in response_json["mediaItems"]:
                        if media["mimeType"].startswith(mime_prefix):
                            mediaItems.append(media)

            if not "nextPageToken" in response_json:
                break

            nextPageToken = response_json["nextPageToken"]
        return mediaItems

    @staticmethod
    def get_location(entry: dict):
        if 'location' not in entry:
            return ""

        # Add location
        locations = []

        for locale in ['userLabel', 'placeName', 'localityName', 'administrativeArea', 'country']:
            if locale == 'placeName' and 'userLabel' in entry['location']:
                continue
            elif locale in entry['location']:
                locations.append(entry['location'][locale])
        location_in_dict = ", ".join(locations)
        return location_in_dict

    @staticmethod
    def get_coordinates(entry: dict):
        if 'location' in entry:
            coordinates = str(entry['location']['latitude']) + \
                ',' + str(entry['location']['longitude'])
            return coordinates

    @staticmethod
    def get_location_coordinate(entry: dict):
        location = EntryProcessor.get_location(entry)
        coordinates = EntryProcessor.get_coordinates(entry)
        if coordinates in ['', [], None]:
            location_string = location
        else:
            location_string = '[' + location + '](geo:' + coordinates + ')'
        return location_string

    @staticmethod
    def get_duration(media_entry: dict):
        duration_seconds = int(media_entry["duration"])
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    @staticmethod
    def get_weather(entry):
        weather = ""
        if 'weather' in entry:
            weather_entry = entry['weather']
            if 'temperatureCelsius' in weather_entry and 'conditionsDescription' in weather_entry:
                temperature = int(weather_entry['temperatureCelsius'])
                description = weather_entry['conditionsDescription']
                if 'location' in entry and 'localityName' in entry['location']:
                    weather_location = entry['location']['localityName']
                    weather += f"{weather_location} "
                weather += f"{temperature}°C {description}"
        return weather

    @staticmethod
    def get_tags(entry):
        tag_list = []

        tag_list.extend(EntryProcessor.additional_tags)
        if 'tags' in entry:
            for t in entry['tags']:
                if len(t) == 0:
                    continue
                tag_list.append("%s%s" % (EntryProcessor.tag_prefix,
                                t.replace(' ', '-').replace('---', '-')))
            if entry['starred']:
                tag_list.append("%sstarred" % EntryProcessor.tag_prefix)

        if len(tag_list) > 0:
            return ", ".join(tag_list)

        return ""

    @staticmethod
    def get_title(entry):

        if 'text' not in entry:
            return EntryProcessor.default_filename

        entry_text = entry['text']
        # Split the text into lines
        lines = entry_text.split("\n")

        # Find the first line that doesn't start with ![]
        entry_title = None
        for t_line in lines:
            if len(t_line) > 0 and not re.match(r"!\[\]", t_line):
                entry_title = t_line
                entry['text'] = re.sub(
                    re.escape(entry_title) + '\n', '', entry['text'], count=1)
                break
        if entry_title is None or len(entry_title) == 0:
            entry_title = EntryProcessor.default_filename

        # Remove all markdown headers
        if re.search(r"^#+\s*", entry_title.strip()) is None or entry_title.startswith("# ["):
            if entry_title in saved_input:
                entry_title = saved_input[entry_title]
            else:
                key = entry_title
                new_title = str(input("Title not found in: %s\nEnter new title (or leave blank to use %s): " % (
                    entry_title.strip(), entry_title.strip())))
                entry_title = entry_title if new_title == "" else new_title
                saved_input[key] = entry_title
                update_saved_input()

        else:
            entry_title = re.sub(r"^#+\s*", "", entry_title.strip())

        # Replace disallowed characters with spaces
        filename = re.sub(r'[\\/:\*\?"<>|#^\[\]]', '', entry_title).strip()

        # filename max length
        return filename[:255]
