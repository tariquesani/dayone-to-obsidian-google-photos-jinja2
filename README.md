# dayone-to-obsidian-Google-Photos
Convert a [Day One](https://dayoneapp.com/) JSON export into individual entries for [Obsidian](https://obsidian.md) with the [Google Photos plugin](https://forum.obsidian.md/t/google-photos-integration-for-obsidian/51062) installed. Each entry is created as a separate page. 

## Additional features from [@LucyDYu](https://github.com/LucyDYu/dayone-to-obsidian)
* Supports importing videos, PDFs, audios, in addition to photos.
* Allows adding metadata for media, such as photo creation date and location (if available).
* Supports various media types, including jpeg, png, mov, mp4, and so on (audio type is fixed to m4a due to lack of type information in JSON).
* Easy configuration using YAML.
* Displays locations on a map for the entire entry and individual photos, audios, and videos (requires [the map view plugin](https://github.com/esm7/obsidian-map-view)).
* Includes datetime, weather, and tags in the frontmatter.
* Supports additional tags to display in Obsidian separate from other note tags. (default = From/DayOne)

## Additional features from me
* Photos and videos will be uploaded to Google Photos, and just the external link will be kept in your notes as per the Google Photos plugin.
* If a photo or video already in Google Photos seems to match the DayOne export, the script prompts the user to confirm the match instead of reuploading the file
* Supports multiple DayOne journals (DayOne Premium)
* Allows renaming untitled DayOne entries with user input

## Example 
### Entry in Day One:
```markdown
# Hello Obsidian
This is an example entry with a lot of text and media.

## Photo
![[imagefile.jpeg]]

## Audio
![[audiofile.m4a]]

## PDF
![[PDFfile.pdf]]

## Video
![[videofile.mp4]]

```
### Run the script: prompting the user to confirm matching photos and videos in Google Photos
![dayone-to-obsidian8](https://github.com/ezratock/dayone-to-obsidian-Google-Photos/assets/41342771/4c06c125-eaeb-461e-8638-dd5ecfc7b6fc)

### Entry after Conversion
filename: Hello Obsidian
```markdown
---
date: 2018-01-02 18:58:49 Tuesday
weather: City 13°C Mostly Cloudy
tags: From/DayOne, DayOne/Audio
locations: 
---
# Hello Obsidian
This is an example entry with a lot of text and media.

## Photo
[![](imagethumbnail.jpeg)](https://photos.google.com/image_in_Google_Photos)

## Audio
Duration: 00:01:48
Date: 2018-01-01T15:24:17Z
Recording Device: iPhone Microphone
Location: [Place, City, Country](geo:latitude,longitude)
![[audiofile.m4a]]

## PDF
Title: PDF title
![[PDFfile.pdf]]

## Video
[![](thumbnails/videothumbnail.jpeg)](https://photos.google.com/video_in_Google_Photos)
Duration: 00:00:21

---
[Place, City, Country](geo:latitude,longitude)

```

## Requirements
* Python 3

## Optional requirements
* Obsidian [Icons Plugin](https://github.com/visini/obsidian-icons-plugin) to display calendar marker at start of page heading

## Day One version
This script works with version 2024.13 of Day One. It has not been tested with any other versions.

## Setup

**DO NOT do this in your current vault. Create a new vault for the purpose of testing. You are responsible for ensuring against data loss**
**This script deletes folders if run a second time** (however, choices that the user inputs are saved to the `secrets` directory. This means the script can be stopped midway through and picked back up at any time.)
**This script renames files**
**This script resizes images in the DayOne export (to 400x400 by default)**
1. Export your journal from [Day One in JSON format](https://help.dayoneapp.com/en/articles/440668-exporting-entries) 
2. Expand that zip file
3. Adjust the *ROOT* variable in `config.yaml` to point to the location where your zip file was expanded and Journal.json exists. You should also have several media folders here if there were photos audios etc in your journal. Additional settings can also be configured in `config.yaml`.
4. Adjust the *GOOGLE_PHOTOS_CREDS* variable in `config.yaml` to point to the location of your Google Photos API Credentials JSON as shown below.
   1. In your Google Cloud Console, click `Photos Library API` (which should already show up if you followed the [instructions](https://github.com/alangrainger/obsidian-google-photos/blob/main/docs/Setup.md) to install the Google Photos plugin in Obsidian)
   2. Click `CREDENTIALS` > `CREATE CREDENTIALS` > `OAuth client ID`

      ![dayone-to-obsidian4](https://github.com/ezratock/dayone-to-obsidian-Google-Photos/assets/41342771/1cc832be-5a5f-430c-b380-5c255528a588)
   4. Choose `Desktop app` and click `CREATE`

      ![dayone-to-obsidian5](https://github.com/ezratock/dayone-to-obsidian-Google-Photos/assets/41342771/1599a723-299e-4706-ac34-e6eca7642f58)
   6. Click `DOWNLOAD JSON`

      ![dayone-to-obsidian6](https://github.com/ezratock/dayone-to-obsidian-Google-Photos/assets/41342771/786abd33-7877-4fde-840c-8481e008101e)
   8. Adjust the *GOOGLE_PHOTOS_CREDS* variable in `config.yaml` to point to that JSON file. It makes sense to save your credentials JSON in the secrets/ directory because then it will already be added to .gitignore
5. If you **not** are using the [Icons Plugin](https://github.com/visini/obsidian-icons-plugin) to display calendar marker at start of page heading set *icons = False*
6. Run the script
   1. Change to the project directory:
      ```
      cd /path/to/dayone-to-obsidian
      ```
   2. Install the required dependencies:
      ```shell
      pip install -r requirements.txt
      ```
      This command will install the necessary packages listed in the `requirements.txt` file. Alternatively, you can use:
      ```shell
      python3 -m pip install -r requirements.txt
      ```
   3. Run the `splitfile.py` script:
      ```shell
      python splitfile.py
      ```
7. Check results in Obsidian
8. If happy, move the folders to whatever vault you want them in. The contents are stored across the outputted journal folders, the `photos`, `audios`, and `pdfs` folders in the root folder, and the `thumbnails` folder in the root/`videos` folder.

## Features
* Processes all entries, including any blank ones you may have.
* If multiple entries on a day, each additional entry is treated seperately
* Adds metadata for whatever exists
   * Location 
   * Datetime
   * Tags
   * Weather
* Tags can be prefixed (default = DayOne/) to show as subtags in Obsidian separate from other note tags
* Photos and videos inserted as Google Photos links
