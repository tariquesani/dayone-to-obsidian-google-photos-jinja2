import logging
import traceback
import dateutil.parser
import pytz  # pip install pytz
import os
import shutil
import time
import json
import re
import sys 

from processor.AudioEntryProcessor import AudioEntryProcessor
from processor.EntryProcessor import EntryProcessor
from processor.PdfEntryProcessor import PdfEntryProcessor
from processor.PhotoEntryProcessor import PhotoEntryProcessor
from processor.VideoEntryProcessor import VideoEntryProcessor
from processor.VideoEntryProcessor import THUMBNAILS_FOLDER
from config.config import Config
from processor.utils import setup_jinja2_env

def rename_media(root, subpath, media_entry, filetype):
    pfn = os.path.join(root, subpath, '%s.%s' % (media_entry['md5'], filetype))
    if os.path.isfile(pfn):
        newfn = os.path.join(root, subpath, '%s.%s' % (media_entry['identifier'], filetype))
        print('Renaming %s to %s' % (pfn, newfn))
        os.rename(pfn, newfn)


DEFAULT_TEXT = Config.get("DEFAULT_TEXT", "")
GOOGLE_PHOTOS_CREDS = Config.get("GOOGLE_PHOTOS_CREDS")

# Initialize the EntryProcessor class variables
EntryProcessor.initialize()

# Set this as the location where your Journal.json file is located
root = Config.get("ROOT")
icons = True  # Set to true if you are using the Icons Plugin in Obsidian

# name of folder where journal entries will end up
rootJournalFolder = Config.get("JOURNAL_FOLDER")
# fn = os.path.join(root, Config.get("JOURNAL_JSON"))

# Clean out existing journal folder, otherwise each run creates new files
if os.path.isdir(rootJournalFolder):
    print("Deleting existing folder: %s" % rootJournalFolder)
    shutil.rmtree(rootJournalFolder)
# Give time for folder deletion to complete. Only a problem if you have the folder open when trying to run the script
time.sleep(2)

if not os.path.isdir(rootJournalFolder):
    print("Creating root journal folder: %s" % rootJournalFolder)
    os.mkdir(rootJournalFolder)

if icons:
    print("Icons are on")
    dateIcon = "`rir:Calendar2`"
else:
    print("Icons are off")
    dateIcon = ""  # make 2nd level heading

dayOneJournals = [x for x in os.listdir(root) if x.endswith(".json")]

print("Begin processing entries")

for journalIndex in dayOneJournals:
    journalFolder = os.path.join(rootJournalFolder, journalIndex.replace(".json", ""))
    dash = "\n========================================"
    print(dash + "\nBegin processing " + journalIndex + dash)
    if os.path.isdir(journalFolder):
        print("journalFolder already exists...")
        import pdb
        pdb.set_trace()
    os.mkdir(journalFolder)

    count = 0
    with open(os.path.join(root, journalIndex), encoding='utf-8') as json_file:
        data = json.load(json_file)

        photo_processor = PhotoEntryProcessor(os.path.join(root, "photos"))
        audio_processor = AudioEntryProcessor()
        video_processor = VideoEntryProcessor(os.path.join(root, "videos"))
        pdf_processor = PdfEntryProcessor()

        for entry in data['entries']:
            new_entry = []

            createDate = dateutil.parser.isoparse(entry['creationDate'])
            localDate = createDate.astimezone(
                pytz.timezone(entry['timeZone']))  # It's natural to use our local date/time as reference point, not UTC

            env = setup_jinja2_env(template_path=os.path.join(os.path.dirname(__file__), './templates'))
            template = env.get_template("frontmatter_template.md")

            # Format the date and time with the weekday
            formatted_datetime = createDate.isoformat() + 'Z'

            date_created = formatted_datetime
            coordinates = ''
            
            frontmatter = template.render(date_created=date_created,
                                          weather=EntryProcessor.get_weather(entry),
                                          tags=EntryProcessor.get_tags(entry))

            if frontmatter != "---\n---\n":
                new_entry.append(frontmatter)

            template = env.get_template("content_template.md")

            if sys.platform == "win32":
                 heading = '\n## %s%s\n' % (dateIcon, localDate.strftime("%A, %#d %B %Y at %#I:%M %p").replace(" at 12:00 PM", ""))
            else:
                 heading = ('## %s%s\n' % (dateIcon, localDate.strftime("%A, %-d %B %Y at %-I:%M %p").replace(" at 12:00 PM", "")))  # untested

            # Add body text if it exists (can have the odd blank entry), after some tidying up
            title = EntryProcessor.get_title(entry)

            print("Processing entry: "+ localDate.strftime('%Y-%m-%d-%A'))

            try:
                if 'text' in entry:
                    new_text = entry['text'].replace("\\", "")
                else:
                    new_text = DEFAULT_TEXT

                new_text = new_text.replace("\u2028", "\n")
                new_text = new_text.replace("\u1C6A", "\n\n")
                special_chars = ["<", ">", "|", "="]
                for special_char in special_chars:
                    new_text = new_text.replace(special_char, "\\" + special_char)

                if 'photos' in entry:
                    # Correct photo links. First we need to rename them. The filename is the md5 code, not the identifier
                    # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run
                    # through as then, they are all renamed.
                    # Assuming all jpeg extensions.
                    photo_list = entry['photos']
                    for p in photo_list:
                        photo_processor.add_entry_to_dict(p)
                        rename_media(root, 'photos', p, p['type'])

                    photo_processor.set_GPhotos_title(title)

                    # Now to replace the text to point to the file in obsidian
                    new_text = re.sub(r"(\!\[\]\(dayone-moment:\/\/)([A-F0-9]+)(\))",
                                     photo_processor.replace_entry_id_with_info,
                                     new_text)

                if 'audios' in entry:
                    audio_list = entry['audios']
                    for p in audio_list:
                        audio_processor.add_entry_to_dict(p)
                        rename_media(root, 'audios', p, "m4a")

                    new_text = re.sub(r"(\!\[\]\(dayone-moment:\/audio\/)([A-F0-9]+)(\))",
                                     audio_processor.replace_entry_id_with_info, new_text)

                if 'pdfAttachments' in entry:
                    pdf_list = entry['pdfAttachments']
                    for p in pdf_list:
                        pdf_processor.add_entry_to_dict(p)
                        rename_media(root, 'pdfs', p, p['type'])

                    new_text = re.sub(r"(\!\[\]\(dayone-moment:\/pdfAttachment\/)([A-F0-9]+)(\))",
                                     pdf_processor.replace_entry_id_with_info, new_text)

                if 'videos' in entry:
                    video_list = entry['videos']
                    for p in video_list:
                        video_processor.add_entry_to_dict(p)
                        rename_media(root, 'videos', p, p['type'])

                    video_processor.set_GPhotos_title(title)

                    new_text = re.sub(r"(\!\[\]\(dayone-moment:\/video\/)([A-F0-9]+)(\))",
                                     video_processor.replace_entry_id_with_info, new_text)
                
            except Exception as e:
                logging.error(f"Exception: {e}")
                logging.error(traceback.format_exc())
                pass

            ## Start Metadata section
            # Get location
            location = EntryProcessor.get_location_coordinate(entry)

            content = template.render(title=title,
                                      content=new_text,
                                      location=location)

            new_entry.append(content)

            ## End Metadata section

            # Add GPS, not all entries have this
            # try:
            #     new_entry.append( '- GPS: [%s, %s](https://www.google.com/maps/search/?api=1&query=%s,%s)\n' % ( entry['location']['latitude'], entry['location']['longitude'], entry['location']['latitude'], entry['location']['longitude'] ) )
            # except KeyError:
            #     pass

            # Save entries organised by year, year-month, year-month-day-weekday.md
            yearDir = os.path.join(journalFolder, str(createDate.year))
            monthDir = os.path.join(yearDir, createDate.strftime('%m-%B'))
            
            if not os.path.isdir(yearDir):
                 os.mkdir(yearDir)
            
            if not os.path.isdir(monthDir):
                 os.mkdir(monthDir)

            title = EntryProcessor.get_title(entry)

            # Filename format: "localDate"
            fnNew = os.path.join(monthDir, "%s.md" % (localDate.strftime('%Y-%m-%d-%A')))

            # Here is where we handle multiple entries on the same day. Each goes to it's own file
            if os.path.isfile(fnNew):
                # File exists, need to find the next in sequence and append alpha character marker
                index = 97  # ASCII a
                fnNew = os.path.join(journalFolder, "%s %s.md" % (title, chr(index)))
                while os.path.isfile(fnNew):
                    index += 1
                    fnNew = os.path.join(journalFolder, "%s %s.md" % (title, chr(index)))

            with open(fnNew, 'w', encoding='utf-8') as f:
                for line in new_entry:
                    f.write(line)

            # Set created date and last modified date to entry's date
            if (os.path.exists(fnNew)):
                date_epoch = createDate.timestamp()
                os.utime(fnNew, (date_epoch, date_epoch))
            else:
                print("Write to file failed.")

            count += 1
    print("Journal %s complete. %d entries processed." % (journalIndex, count))

print("\n")
for media_type in [os.path.join("videos", THUMBNAILS_FOLDER), "photos", "pdfs", "audios"]:
    media_folder_path = os.path.join(root, media_type)
    if os.path.exists(media_folder_path):
        print("Copying %s to %s" % (media_type, rootJournalFolder))
        shutil.copytree(media_folder_path, os.path.join(rootJournalFolder, media_type))
    else:
        print("%s folder does not exist" % media_type.capitalize())

print("\nComplete. %d journals processed." % len(dayOneJournals))
