import os
from datetime import datetime

current_datetime = datetime.now().strftime('%Y%m%d%H%M')
datetime_string = datetime.now().strftime('%Y%m%d%H%M')

def merge_files():
    # Get input from user
    keyword = input("Enter the keyword to search for: ")
    folder_path = input("Enter the folder path: ")

    # Create output file name
    output_file = f"{keyword}_{datetime_string}.txt"

    try:
        # Check if folder exists
        if not os.path.exists(folder_path):
            raise Exception("Folder does not exist!")

        # Initialize a counter for matching files
        files_found = 0

        # Open output file in write mode
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Iterate through all files in the folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(folder_path, filename)

                    # Read content of each file
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()

                        # Check if keyword exists in the content
                        if keyword.lower() in content.lower():
                            files_found += 1

                            # Write file name as header
                            outfile.write(f"\n=== Content from: {filename} ===\n")
                            outfile.write(content)
                            outfile.write("\n")

        # Provide feedback to user
        if files_found > 0:
            print(f"\nMerge complete! {files_found} files containing '{keyword}' were merged into {output_file}")
        else:
            print(f"\nNo files containing '{keyword}' were found in the specified folder.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    merge_files()
