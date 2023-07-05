from processor.EntryProcessor import EntryProcessor


class VideoEntryProcessor(EntryProcessor):
    def get_entry_info(self, entry):
        # Select important attributes and format them into a string
        identifier = entry["identifier"]
        video_type = entry["type"]
        video_basic_info = f"![[{identifier}.{video_type}]]\n"
        # If you only need embeddings of media and not any additional info,
        # you can remove the following section.
        # You can also add or remove attributes from the JSON.
        # START of Section.
        if "title" in entry:
            video_basic_info += "Title: {}\n".format(entry["title"])
        if "duration" in entry:
            video_basic_info += "Duration: {}\n".format(self.get_duration(entry))
        if "date" in entry:
            video_basic_info += "Date: {}\n".format(entry["date"])
        if "location" in entry:
            video_basic_info += "Location: {}\n".format(self.get_location_coordinate(entry))
        # END of Section.
        return video_basic_info
