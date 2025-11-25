import pandas as pd
import json
from datetime import datetime
import os
import glob

def create_rule_analysis_df(file_path, DOMAIN, STACK, attributes, output_cols, output_strings, number_of_output_cols, current_datetime):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

    # Split content into individual rules
    rules = content.split('\nRule: ')
    if rules[0].startswith('Rule: '):
        rules[0] = rules[0][6:]  # Remove 'Rule: ' from the first rule

    data = []

    for rule in rules:
        if not rule.strip():
            continue

        rule_dict = {}
        lines = rule.strip().split('\n')
        line_count = len(lines) - number_of_output_cols

        rule_dict['DOMAIN'] = DOMAIN
        rule_dict['STACK'] = STACK
        rule_dict['RULE'] = lines[0].rsplit('_', 1)[0].strip()
        rule_dict['LINE_COUNT'] = str(line_count)
        rule_dict['DownloadDate'] = current_datetime

        #Get rule outputs
        outputs = []
        for out_col, out_str in zip(output_cols, output_strings):
            for line in lines[1:number_of_output_cols]:
                line = line.strip()
                line = line.rstrip(',')
                if out_str in line:
                    outputs.append(out_str.strip() + " "+ line.replace(out_str,""))
                    rule_dict[out_col] = line.replace(out_str,"")
                    break
        rule_dict['RULE_OUTPUT'] = '; '.join(outputs)

        policy_text = '\n'.join(lines[number_of_output_cols:])
        rule_dict['POLICY_TEXT'] = policy_text
        rule_dict['CHAR_COUNT'] = str(len(policy_text))

        attribute_order = []
        for line in lines[number_of_output_cols:]:
            line = line.strip()
            for attr in attributes:
                if attr in line:
                    attribute_order.append(attr)
        rule_dict['ORDER_OF_ATTRIBUTES'] = ", ".join(attribute_order)
        rule_dict['ATTRIBUTES_USED'] = ', '.join(dict.fromkeys(attribute_order))


        for attr in attributes:
            attr_value = []
            for line in lines[number_of_output_cols:]:
                line = line.strip()
                if attr in line:
                    attr_value.append(line.replace(attr, ""))
            attribute_value = ' \n'.join(attr_value)
            rule_dict[attr] = attribute_value

        data.append(rule_dict)

    df = pd.DataFrame(data)
    return df

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the script directory
os.chdir(script_dir)

# Get all .txt files in the directory
all_txt_files = glob.glob("*.txt")

if not all_txt_files:
    print("No .txt files found in the directory")
    exit(1)

# Combined data from all files
all_policy_data = []

current_datetime = datetime.now().strftime('%Y%m%d%H%M')
output_cols = ['boxClass', 'minHeight', 'minLength', 'minWidth',
               'batteryStatements', 'secondaryLabels', 'unidStatements', 'palletLabels', 'packLabels',
               'hazmatLabelStatementsIdentifier']
output_strings = [' boxClass |', ' minHeight |', ' minLength |', ' minWidth |',
                  ' batteryStatements |', ' secondaryLabels |', ' unidStatements |', ' palletLabels |', ' packLabels |',
                  ' hazmatLabelStatementsIdentifier |']
attributes = ['OriginOrgUnit', 'DestinationCountry', 'DestinationPostalCode', 'hazmat_exception',
              'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'sioc_capable',
              'regulated_sioc_override', 'package_level',
              'Country', 'is_international', 'battery_cell_composition',
              'program_participation']

# Process each file
for input_file in all_txt_files:
    print(f"\nProcessing file: {input_file}")

    # Process the file and add its data to the combined list
    file_path = os.path.join(script_dir, input_file)

    # Extract filename and domain information
    filename = input_file.split('.')[0]
    DOMAIN = filename.split('_')[0]
    STACK = filename.split('_')[1]
    DownloadDate = current_datetime

    match DOMAIN:
        case 'TRANSPORTATION':
            number_of_output_cols = 5
        case 'SHIPOPTION':
            number_of_output_cols = 3
        case 'BOX':
            number_of_output_cols = 5
        case 'RETURNS':
            number_of_output_cols = 2
        case 'LABELING':
            number_of_output_cols = 7
        case 'STORAGE':
            number_of_output_cols = 4
        case 'DONATION':
            number_of_output_cols = 3
        case 'MESSAGING':
            number_of_output_cols = 2
        case 'WASTE':
            number_of_output_cols = 5
        case 'WASTEPROFILE':
            number_of_output_cols = 2
        case _:
            raise ValueError(f"Unknown domain: {DOMAIN}")
    df = create_rule_analysis_df(file_path, DOMAIN, STACK, attributes, output_cols, output_strings, number_of_output_cols, current_datetime)

    # Defining the column order
    base_columns = ['DOMAIN', 'STACK', 'RULE', 'RULE_OUTPUT', 'POLICY_TEXT', 'ATTRIBUTES_USED', 'ORDER_OF_ATTRIBUTES', 'LINE_COUNT', 'CHAR_COUNT', 'DownloadDate']

    # Create final column order list
    final_column_order = ['Serial_Number'] + base_columns + output_cols + attributes

    # Ensure all columns exist in the DataFrame
    for col in final_column_order:
        if col not in df.columns:
            df[col] = None  # or '' for empty string

    # Sort DataFrame by RULE column and reorder columns
    df_sorted = df.sort_values('RULE')[final_column_order]
    all_policy_data.extend(df_sorted.to_dict('records'))

# Sort all combined data
all_policy_data = sorted(all_policy_data,
                        key=lambda x: (x['DOMAIN'],
                                      x['STACK'],
                                      x['RULE'],
                                      x['POLICY_TEXT'],
                                      x['RULE_OUTPUT']))

# Add Serial Number column with reset per unique DOMAIN_STACK_RULE
current_key = None
counter = 0

for record in all_policy_data:
    # Create unique key for DOMAIN_STACK_RULE combination
    key = f"{record['DOMAIN']}_{record['STACK']}_{record['RULE']}"

    # Reset counter when we encounter a new DOMAIN_STACK_RULE combination
    if key != current_key:
        current_key = key
        counter = 1
    else:
        counter += 1

    # Add serial number to the record
    record['Serial_Number'] = f"{key}_{counter:05d}"

# Create output filename with full path
output_filename = os.path.join(script_dir, f'masterpolicydata_{current_datetime}.json')


# Create output filename with full path
output_filename = os.path.join(script_dir, f'masterpolicydata_{current_datetime}.json')

# Write combined JSON file
try:
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_policy_data, f, indent=4, ensure_ascii=False)
    print(f"\nProcessing complete. Combined data saved as: {output_filename}")
    print(f"Total number of files processed: {len(all_txt_files)}")
    print(f"Total number of policies: {len(all_policy_data)}")
except Exception as e:
    print(f"\nError writing output file: {e}")
