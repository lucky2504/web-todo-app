import pandas as pd


def parse_rule_text(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content into individual rules
    rules = content.split('\nRule: ')
    if rules[0].startswith('Rule: '):
        rules[0] = rules[0][6:]  # Remove 'Rule: ' from the first rule

    data = []
    max_attrs = 0  # Track maximum number of attributes

    for rule in rules:
        if not rule.strip():
            continue

        lines = rule.strip().split('\n')

        # Get rule name
        rule_name = lines[0].split('_')[0]

        # Initialize other fields
        output_mode = ''
        output_destination = ''
        output_smg = ''
        output_tags = ''

        attributes = []  # Store attributes in a list

        for line in lines[1:]:
            line = line.strip()
            if 'mode |' in line:
                output_mode = line.split('|')[0].strip()[:-4] + ": " + line.split('|')[1].strip()
            elif 'destination |' in line:
                output_destination = line.split('|')[0].strip()[:-11] + ": " + line.split('|')[1].strip()
            elif 'smg |' in line:
                output_smg = line.split('|')[0].strip()[:-3] + ": " + line.split('|')[1].strip()
            elif 'tags |' in line:
                output_tags = line.split('|')[0].strip()[:-4] + ": " + line.split('|')[1].strip()
            elif line and not line.startswith('Rule:') and '|' not in line:
                line = line.strip()
                if line:
                    attributes.append(line)

        # Update max_attrs if this rule has more attributes
        max_attrs = max(max_attrs, len(attributes))

        # Create rule dictionary
        rule_dict = {
            'Rules': rule_name,
            'Output mode': output_mode,
            'Output destination': output_destination,
            'Output smg': output_smg,
            'Output tags': output_tags,
        }

        # Add attributes to rule dictionary
        lst = []
        for i, attr in enumerate(attributes, 1):
            rule_dict[f'Attr {i}'] = attr
            if ' ' in attr and 'There' not in attr and not attr.startswith("The total "):
                lst.append(attr.split(' ')[0])
            elif attr.startswith("The total "):
                attr = attr.split(" is ")[0]
                lst.append(attr.split(' ')[-1])

        lst = list(set(lst))
        rule_dict['Attr 0'] = ', '.join(map(str, lst))

        data.append(rule_dict)

    # Ensure all rules have the same number of attribute columns
    for rule_dict in data:
        for i in range(1, max_attrs + 1):
            if f'Attr {i}' not in rule_dict:
                rule_dict[f'Attr {i}'] = ''

    return data

def truncate_long_string(s, max_length=250):
    if isinstance(s, str) and len(s) > 254:
        return s[:max_length] + "..."
    return s

def create_excel(data, output_file):
    # Truncate long strings in the data
    for item in data:
        for key, value in item.items():
            item[key] = truncate_long_string(value)

    data = sorted(data, key=lambda x: x['Rules'])

    df = pd.DataFrame(data)
    # Reorder columns
    base_columns = ['Rules', 'Output mode', 'Output destination', 'Output smg', 'Output tags']
    attr_columns = [col for col in df.columns if col.startswith('Attr ')]
    attr_columns.sort(key=lambda x: int(x.split()[1]))  # Sort attr columns numerically
    df = df[base_columns + attr_columns]
    df.to_excel(output_file, index=False)


# Use the functions
input_file = "xyz.txt"  # Your input file path
output_file = "policydata.xlsx"  # Your output file path

data = parse_rule_text(input_file)
create_excel(data, output_file)

print("Policy data printed in policydata workbook!")
