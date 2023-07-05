from processor.EntryProcessor import EntryProcessor


class PdfEntryProcessor(EntryProcessor):
    def get_entry_info(self, entry):
        # Select important attributes and format them into a string
        identifier = entry["identifier"]
        pdf_type = entry["type"]
        pdf_basic_info = ""
        # If you only need embeddings of media and not any additional info,
        # you can remove the following section.
        # You can also add or remove attributes from the JSON.
        # START of Section.
        if "pdfName" in entry:
            pdf_basic_info += "Title: {}\n".format(entry["pdfName"])
        # END of Section.

        pdf_basic_info += f"![[{identifier}.{pdf_type}]]\n"
        return pdf_basic_info

