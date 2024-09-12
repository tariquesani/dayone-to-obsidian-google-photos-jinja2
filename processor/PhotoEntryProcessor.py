from datetime import datetime, timezone
import os
from PIL import Image

from processor.EntryProcessor import EntryProcessor, MAX_SIZE, saved_uploads, update_saved_uploads


class PhotoEntryProcessor(EntryProcessor):
    def __init__(self, path):
        self.path = path
        super().__init__()


    def resize_image(self, p, max_size=MAX_SIZE):
        input_path = os.path.join(self.path, '%s.%s' % (p['identifier'], p["type"]))
        # Save images organised by year, year-month
        img_date = datetime.strptime(p['date'],"%Y-%m-%dT%H:%M:%SZ")
        year_dir = os.path.join(self.path, str(img_date.year))
        month_dir = os.path.join(year_dir, img_date.strftime('%m-%B'))

        if not os.path.isdir(year_dir):
            os.mkdir(year_dir)
            
        if not os.path.isdir(month_dir):
            os.mkdir(month_dir)

        output_path = os.path.join(month_dir, '%s.%s' % (p['identifier'], p["type"]))

        if os.path.exists(input_path):
            print("Resizing thumbnail image: " + input_path)
            with Image.open(input_path) as img:
                img.thumbnail(max_size, Image.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path, "JPEG")
                os.remove(input_path)
        else:
            print("Error: %s does not exist!" % input_path)

    def get_entry_info(self, entry):
        identifier = entry["identifier"]
        photo_type = entry["type"]
        if "%s.%s" % (identifier, photo_type) in saved_uploads:
            correct_photo_url = saved_uploads["%s.%s" % (identifier, photo_type)]
        else:
            possible_photos = []
            correct_photo_url = None
            if "date" in entry:
                # search if the photo already exists in Google Photos
                found_photos = self.get_GPhotos(entry["date"], "image")
                for photo in found_photos:
                    if int(photo["mediaMetadata"]["width"]) == entry["width"] and int(photo["mediaMetadata"]["height"]) == entry["height"]:
                        possible_photos.append(photo)
                if len(possible_photos) > 0:
                    print("Which photo matches %s/%s.%s ?\n0: None" % (self.path, identifier, photo_type))
                    for i in range(len(possible_photos)):
                        print("%d: %s" % (i+1, possible_photos[i]["productUrl"]))
                    user_input = int(input("Enter choice (no error handling for bad input):"))
                    if user_input > 0:
                        correct_photo_url = possible_photos[user_input - 1]['productUrl']

            # upload the photo to Google Photos
            if correct_photo_url == None:
                correct_photo_url = self.upload_to_GPhotos(self.path, "%s.%s" % (identifier, photo_type), entry["date"] if "date" in entry else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"), self.title)

            saved_uploads["%s.%s" % (identifier, photo_type)] = correct_photo_url
            update_saved_uploads()

        self.resize_image(entry)
        local_thumbnail_link = "%s.%s" % (identifier, photo_type)

        photo_basic_info = f"[![]({local_thumbnail_link})]({correct_photo_url})"

        # If you only need embeddings of media and not any additional info,
        # you can remove the following section.
        # You can also add or remove attributes from the JSON.
        # START of Section.
        if "date" in entry:
            photo_basic_info += "`rir:Calendar` {}".format(entry["date"])
        if "location" in entry:
            photo_basic_info += " `rir:MapPin` {} tag:photo\n".format(self.get_location_coordinate(entry))
        # END of Section.

        return photo_basic_info