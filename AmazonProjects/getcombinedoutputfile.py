import json
import os
import glob
from collections import OrderedDict


def combine_json_files(input_pattern, output_file):
    priority_columns = [
        "UNIQUE_KEY",
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

    for col in priority_columns:
        all_columns[col] = None

    # First pass: collect all unique column names and data
    for filename in glob.glob(input_pattern):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                for key in item.keys():
                    if key not in priority_columns:
                        all_columns[key] = None
            combined_data.extend(data)

    column_list = list(all_columns.keys())

    # Sort combined_data by DOMAIN and STACK
    combined_data.sort(key=lambda x: (x.get('DOMAIN', ''), x.get('STACK', '')))

    # Second pass: standardize the data and add unique keys
    standardized_data = []
    current_domain = None
    current_stack = None
    record_count = 0

    for item in combined_data:
        domain = item.get('DOMAIN', '')
        stack = item.get('STACK', '')

        # Reset counter when domain or stack changes
        if domain != current_domain or stack != current_stack:
            record_count = 1
            current_domain = domain
            current_stack = stack
        else:
            record_count += 1

        standardized_item = OrderedDict()
        # Add unique key
        standardized_item["UNIQUE_KEY"] = f"{domain}_{stack}_RECORD_{str(record_count).zfill(6)}"

        # Add all other fields
        for col in column_list[1:]:  # Skip UNIQUE_KEY as we already added it
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
input_pattern = 'PolicyTextFilesForMerging/*.json'
output_file = 'PolicyTextFilesForMerging/combined_output.json'
combine_json_files(input_pattern, output_file)
