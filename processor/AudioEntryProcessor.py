from processor.EntryProcessor import EntryProcessor


class AudioEntryProcessor(EntryProcessor):

    def get_entry_info(self, entry):
        # Select important attributes and format them into a string
        identifier = entry["identifier"]
        audio_basic_info = ""

        # If you only need embeddings of media and not any additional info,
        # you can remove the following section.
        # You can also add or remove attributes from the JSON.
        # START of Section.
        if "title" in entry:
            audio_basic_info += "Title: {}\n".format(entry["title"])
        if "duration" in entry:
            audio_basic_info += "Duration: {}\n".format(self.get_duration(entry))
        if "date" in entry:
            audio_basic_info += "Date: {}\n".format(entry["date"])
        if "recordingDevice" in entry:
            audio_basic_info += "Recording Device: {}\n".format(entry["recordingDevice"])
        if "location" in entry:
            audio_basic_info += "Location: {}\n".format(self.get_location_coordinate(entry))
        # END of Section.

        audio_basic_info += f"![[{identifier}.m4a]]\n"
        return audio_basic_info
