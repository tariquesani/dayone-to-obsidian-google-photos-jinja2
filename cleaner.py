import os
from config.config import Config

# Load the configuration
Config.load_config("config.yaml")

def search_files(root_folder, search_text):
    files_to_delete = []  # List to store files that match the search text
    count = 0  # Counter for matching files
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(foldername, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        if search_text in file.read():
                            print(filepath)  # Print the full file path
                            files_to_delete.append(filepath)  # Add to the list
                            count += 1  # Increment the counter
                except Exception as e:
                    print(f"Error reading file {filepath}: {e}")
    
    print(f"\nTotal number of files found with '{search_text}': {count}")
    
    if count > 0:
        # Ask the user if they want to delete the files
        delete_prompt = input("Do you want to delete these files? (y/n): ").lower()
        
        if delete_prompt in ['y', 'yes']:
            for file in files_to_delete:
                try:
                    os.remove(file)
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")
        else:
            print("No files were deleted.")

# Define the root folder and the search text
root_folder = Config.get("JOURNAL_FOLDER")
search_text = 'dayone-moment'

# Call the function
search_files(root_folder, search_text)
