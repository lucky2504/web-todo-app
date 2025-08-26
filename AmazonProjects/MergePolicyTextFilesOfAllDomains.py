import json
import os
import glob
from collections import OrderedDict

def combine_json_files(input_pattern, output_file):
    # Define priority columns in desired order
    priority_columns = [
        "DOMAIN",
        "STACK",
        "RULE",
        "RULE_OUTPUT",
        "POLICY_TEXT",
        "ATTRIBUTES_USED",
        "ORDER_OF_ATTRIBUTES",
        "LINE_COUNT",
        "CHAR_COUNT",
        "DownloadDate"
    ]

    combined_data = []
    all_columns = OrderedDict()

    # First add priority columns to OrderedDict
    for col in priority_columns:
        all_columns[col] = None

    # First pass: collect all unique column names while preserving order
    for filename in glob.glob(input_pattern):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                for key in item.keys():
                    if key not in priority_columns:  # Only add non-priority columns
                        all_columns[key] = None
            combined_data.extend(data)

    # Convert OrderedDict keys to a list for easier handling
    column_list = list(all_columns.keys())

    # Second pass: standardize the data
    standardized_data = []
    for item in combined_data:
        standardized_item = OrderedDict()
        for col in column_list:
            standardized_item[col] = item.get(col, "")
        standardized_data.append(standardized_item)

    # Write the combined data to the output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(standardized_data, outfile, indent=2)

    print(f"Combined data written to {output_file}")
    print(f"Total number of columns: {len(column_list)}")
    print(f"Total number of records: {len(standardized_data)}")
    print("\nColumn order:")
    for i, col in enumerate(column_list, 1):
        prefix = "* " if col in priority_columns else "  "
        print(f"{prefix}{i}. {col}")

# Usage
input_pattern = 'PolicyTextFilesForMerging/*.json'  # Replace with your actual path
output_file = 'PolicyTextFilesForMerging/combined_output.json'   # Replace with your desired output path
combine_json_files(input_pattern, output_file)
