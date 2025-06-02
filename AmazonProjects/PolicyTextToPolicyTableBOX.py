import pandas as pd

def create_policy_end_to_end_line(file_path):
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
        line_count = len(lines) - 5

        rule_name = lines[0].rsplit('_', 1)[0] # Get rule name

        # Initialize other fields
        boxClass = ''
        minHeight = ''
        minLength = ''
        minWidth = ''

        attributes = []  # Store attributes in a list

        for line in lines[1:]:
            line = line.strip()
            if 'boxClass |' in line:
                boxClass = line.split('|')[0].strip()[:-8] + ": " + line.split('|')[1].strip()
            elif 'minHeight |' in line:
                minHeight = line.split('|')[0].strip()[:-9] + ": " + line.split('|')[1].strip()
            elif 'minLength |' in line:
                minLength = line.split('|')[0].strip()[:-9] + ": " + line.split('|')[1].strip()
            elif 'minWidth |' in line:
                minWidth = line.split('|')[0].strip()[:-8] + ": " + line.split('|')[1].strip()
            elif line and not line.startswith('Rule:') and '|' not in line:
                line = line.strip()
                if line:
                    attributes.append(line)

        policy_text = '; '.join(attributes)

        # Update max_attrs if this rule has more attributes
        max_attrs = max(max_attrs, len(attributes))

        # Create rule dictionary
        rule_dict = {
            'Rules': rule_name,
            'boxClass': boxClass,
            'minHeight': minHeight,
            'minLength': minLength,
            'minWidth': minWidth,
            'Line Count': line_count,
            'Policy Text': policy_text,
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

def get_unique_attrs(data):
    df = pd.DataFrame(data)
    unique_attrs = [] # Create a set to store unique attributes
    for cell in df['Attr 0']: # Process each cell in the 'Attr 0' column
        attrs = [attribute.strip() for attribute in cell.split(',')] # Split the attributes by comma and strip whitespace
        for attr in attrs:
            unique_attrs.append(attr) # Add each attribute to the set
    unique_attrs = list(set(unique_attrs))
    return unique_attrs

def create_policy_attribute_df(policy_data, attributes):
    if isinstance(policy_data, list): # Converting policy_data to DataFrame if it's not already
        df_policy = pd.DataFrame(policy_data) # Assuming policy_data is a list of dictionaries
    else:
        df_policy = policy_data

    base_columns = ['Rules', 'boxClass', 'minHeight', 'minLength', 'minWidth', 'Line Count', 'Policy Text', 'Attr 0'] # Initialize new dataframe with base columns
    policy_attribute = pd.DataFrame(columns=base_columns + attributes)

    policy_attribute[base_columns] = df_policy[base_columns] # Copy base columns from policy_data

    for idx, row in df_policy.iterrows(): # For each row in policy_data
        attr_conditions = {attr: [] for attr in attributes} # Dictionary to collect all conditions for each attribute

        for col in df_policy.columns: # For each attribute column in original data (Attr 1, Attr 2, etc.)
            if col.startswith('Attr ') and col != 'Attr 0':
                value = row[col]
                if pd.isna(value) or str(value).strip() == '':
                    continue

                value = str(value)

                for attr in attributes: # Check for each attribute in this cell
                    if attr in value:
                        condition = value.split(attr)[1].strip() # Split by attribute and take what comes after
                        if condition:  # Only add if there's something after the split
                            attr_conditions[attr].append(condition)

        for attr, conditions in attr_conditions.items(): # Combine all conditions for each attribute and set in the dataframe
            if conditions:  # Only set if we found conditions
                policy_attribute.at[idx, attr] = '; '.join(conditions)

    return policy_attribute

input_file = "text_dump.txt"
policy_text_data = create_policy_end_to_end_line(input_file)
policy_text_data = sorted(policy_text_data, key=lambda x: x['Rules'])
attributes = get_unique_attrs(policy_text_data) # Get unique attributes and create policy attribute DataFrame
policy_attribute = create_policy_attribute_df(policy_text_data, attributes)

# Generate JSON for policydata.xlsx
df_policy = pd.DataFrame(policy_attribute)
df_policy.to_json('policyattribute.json', orient='records', indent=4)