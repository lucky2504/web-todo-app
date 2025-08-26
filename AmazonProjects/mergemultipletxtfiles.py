import os
import json
from datetime import datetime


def merge_files():
    # Get inputs from user
    folder_path = "Text Dump DATA"
    keyword = input("Enter the keyword to search for: ")

    # Validate folder path
    if not os.path.exists(folder_path):
        print("Error: The specified folder does not exist!")
        return

    datetime_string = datetime.now().strftime('%Y%m%d%H%M')

    # Create output file name
    output_file = f"{keyword}_{datetime_string}.json"

    # Initialize list to store all objects
    merged_data = []

    try:
        # Initialize counter for processed files
        files_processed = 0

        # Iterate through all files in the specified folder
        for filename in os.listdir(folder_path):
            # Check if file is JSON and contains keyword in filename
            if filename.endswith('.json') and keyword.lower() in filename.lower():
                file_path = os.path.join(folder_path, filename)
                print(f"Processing file: {filename}")

                # Read JSON file
                with open(file_path, 'r', encoding='utf-8') as infile:
                    data = json.load(infile)
                    merged_data.extend(data)
                    files_processed += 1

        if merged_data:
            # Write merged data to output file in the specified folder
            output_path = os.path.join(folder_path, output_file)
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(merged_data, outfile, indent=4)

            print(f"\nMerge complete!")
            print(f"Files processed: {files_processed}")
            print(f"Total records merged: {len(merged_data)}")
            print(f"Output written to: {output_path}")
        else:
            print(f"\nNo files found with '{keyword}' in their name")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    merge_files()

