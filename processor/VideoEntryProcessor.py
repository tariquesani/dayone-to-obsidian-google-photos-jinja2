from datetime import datetime, timezone
import os
from moviepy.editor import VideoFileClip
from PIL import Image

from processor.EntryProcessor import EntryProcessor, MAX_SIZE, saved_uploads, update_saved_uploads

DURATION_ERROR = 1
THUMBNAILS_FOLDER = "thumbnails"

class VideoEntryProcessor(EntryProcessor):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def generate_thumbnail(self, p, max_size=MAX_SIZE):
        video_path = os.path.join(self.path, '%s.%s' % (p['identifier'], p["type"]))
        if os.path.exists(video_path):
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(0)
            result = Image.fromarray(frame)
            # Checking if rotated video messed up aspect ratio
            if hasattr(clip, 'rotation') and clip.rotation in [90, 270]:
                result = result.resize((clip.h, clip.w), Image.Resampling.LANCZOS)
            result.thumbnail(max_size, Image.LANCZOS)
            thumbnails_folder = os.path.join(self.path, THUMBNAILS_FOLDER)
            if not os.path.isdir(thumbnails_folder):
                print("Creating video thumbnail folder: %s" % thumbnails_folder)
                os.mkdir(thumbnails_folder)
            thumbnail_name = '%s.jpg' % p['identifier']
            thumbnail_path = os.path.join(thumbnails_folder, thumbnail_name)
            print("Saving thumbnail to " + thumbnail_path)
            result.save(thumbnail_path)
            return os.path.join(THUMBNAILS_FOLDER, thumbnail_name)
        else:
            print("Error: %s does not exist!" % video_path)
            return None

    def get_entry_info(self, entry):
        identifier = entry["identifier"]
        video_type = entry["type"]
        if "%s.%s" % (identifier, video_type) in saved_uploads:
            correct_video_url = saved_uploads["%s.%s" % (identifier, video_type)]
            local_thumbnail_link = os.path.join(THUMBNAILS_FOLDER, '%s.jpg' % entry['identifier'])
        else:
            possible_videos = []
            correct_video_url = None
            if "date" in entry:
                # search if the photo already exists in Google Photos
                found_videos = self.get_GPhotos(entry["date"], "video")
                for video in found_videos:
                    if not ("width" in video["mediaMetadata"].keys()) or int(video["mediaMetadata"]["width"]) == entry["width"] and int(video["mediaMetadata"]["height"]) == entry["height"]:
                        possible_videos.append(video)
                if len(possible_videos) > 0:
                    print("Which video matches %s/%s.%s ?\n0: None" % (self.path, identifier, video_type))
                    for i in range(len(possible_videos)):
                        print("%d: %s" % (i + 1, possible_videos[i]["productUrl"]))
                    user_input = int(input("Enter choice (no error handling for bad input):"))
                    if user_input > 0:
                        correct_video_url = possible_videos[user_input - 1]['productUrl']

            # upload the photo to Google Photos
            if correct_video_url == None:
                correct_video_url = self.upload_to_GPhotos(self.path, "%s.%s" % (identifier, video_type),
                                                           entry["date"] if "date" in entry else datetime.now(
                                                               timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"), self.title)

            saved_uploads["%s.%s" % (identifier, video_type)] = correct_video_url
            update_saved_uploads()

            local_thumbnail_link = self.generate_thumbnail(entry)

        local_thumbnail_link = self.generate_thumbnail(entry)
        if local_thumbnail_link is None:
            local_thumbnail_link = "FILE NOT FOUND"

        video_basic_info = f"[![]({local_thumbnail_link})]({correct_video_url})\n"

        # Keep duration displayed below to signify its a video instead of a photo
        if "duration" in entry:
            video_basic_info += "Duration: {}\n".format(self.get_duration(entry))

        return video_basic_info
