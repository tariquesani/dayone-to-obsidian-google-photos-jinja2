from processor.EntryProcessor import EntryProcessor


class PhotoEntryProcessor(EntryProcessor):
    def get_entry_info(self, entry):
        # Select important attributes and format them into a string
        identifier = entry["identifier"]
        photo_type = entry["type"]
        photo_basic_info = f"![[{identifier}.{photo_type}]]\n"
        # If you only need embeddings of media and not any additional info,
        # you can remove the following section.
        # You can also add or remove attributes from the JSON.
        # START of Section.
        if "date" in entry:
            photo_basic_info += "Date: {}\n".format(entry["date"])
        if "location" in entry:
            photo_basic_info += "Location: {}\n".format(self.get_location_coordinate(entry))
        # END of Section.

        return photo_basic_info

