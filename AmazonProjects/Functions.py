#Functions for policy and predicate data merging
from itertools import product

def get_predicate_list(predicatesheet):
    sheet = predicatesheet
    # Find the last row in column C
    last_row = sheet.Cells(sheet.Rows.Count, "A").End(-4162).Row

    predicates_list = []
    # Process each row to remove gaps
    for row in range(1, last_row + 1):
        print(f"Processing row number {row} of predicate sheet")
        predicates_line = []

        # Check if first column had header as predicate
        if sheet.Range(f"A{row}").Value == "predicate":
            predicate_row = row
            #predicate string
            value = sheet.Range(f"A{row}").Value
            predicates_line.append(value)

            #attr string
            value = ""
            for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                attr = sheet.Range(f"{col}{row}").Value

                if attr is None:
                    pass #skip empty cells
                elif attr == "Output":
                    #Output String
                    predicates_line.append(attr)
                    value = value[:-2]
                elif attr != "":
                    value = value + attr + "; "
            predicates_line.append(value)
        else:
            # predicate string
            value = sheet.Range(f"A{row}").Value
            predicates_line.append(value)

            # attr string
            value = ""
            for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                attr = sheet.Range(f"{col}{row}").Value
                header_attr = sheet.Range(f"{col}{predicate_row}").Value

                if attr is None:
                    pass  # skip empty cells
                elif header_attr == "Output":
                        # Output String
                        predicates_line.append(attr)
                        value = value[:-2]
                elif attr != "":
                        value = value + sheet.Range(f"{col}{predicate_row}").Value + ": " + attr + "; "
            predicates_line.append(value)
        predicates_list.append(predicates_line)

    # Write to Excel starting from O1
    for i, row_data in enumerate(predicates_list, start=1):
        for j, value in enumerate(row_data):
            # Convert column number to letter (O=15, P=16, Q=17)
            col = chr(ord('N') + j + 1)  # N + 1 = O, and so on
            cell = f"{col}{i}"
            sheet.Range(cell).Value = str(value)[:254]
    return predicates_list

def get_policy_list(policysheet):
    # Select the sheet with "policies" data
    sheet = policysheet

    # Find the last row in column A
    last_row = sheet.Cells(sheet.Rows.Count, "A").End(-4162).Row

    policy_list = []
    end_to_end_line_item_list = []
    # Process each row to build the policy_list line item
    for row in range(1, last_row + 1):
        print(f"Processing {row}")
        policy_line = []
        end_to_end_line = []
        # Check if first column had header as policy
        if sheet.Range(f"A{row}").Value == "policy":
            policy_row = row
            #policy string
            value = sheet.Range(f"A{row}").Value
            policy_line.append(value)

            #attr string
            value = ""
            for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                attr = sheet.Range(f"{col}{row}").Value

                if attr is None:
                    pass #skip empty cells
                elif attr == "Output":
                    #Output String
                    policy_line.append(attr)
                    value = value[:-2]
                elif attr != "":
                    value = value + attr + "; "
            policy_line.append(value)
        else:
            # policy string
            value = sheet.Range(f"A{row}").Value
            policy_line.append(value)

            # attr string
            value = ""
            for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                attr = sheet.Range(f"{col}{row}").Value
                header_attr = sheet.Range(f"{col}{policy_row}").Value

                if attr is None:
                    pass  # skip empty cells
                elif header_attr == "Output":
                    # Output String
                    policy_line.append(attr)
                    value = value[:-2]
                elif attr != "":
                    value = value + sheet.Range(f"{col}{policy_row}").Value + ": " + attr + "; "

            policy_line.append(value)
        policy_list.append(policy_line)

    # Write to Excel starting from O1
    for i, row_data in enumerate(policy_list, start=1):
        for j, value in enumerate(row_data):
            # Convert column number to letter (O=15, P=16, Q=17)
            col = chr(ord('N') + j + 1)  # N + 1 = O, and so on
            cell = f"{col}{i}"
            sheet.Range(cell).Value = str(value)[:254]
    #Write E2E line items in column S
    for row, line_item in enumerate(end_to_end_line_item_list, start=1):
        sheet.Range(f"S{row}").Value = line_item

    return policy_list

def parse_count_string(input_string):
    # If multiple COUNT patterns (contains 'or')
    if ' or COUNT  ' in input_string:
        # Split by 'or COUNT  ' to separate multiple counts
        parts = input_string.split(' or COUNT  ')
        result = []

        # Handle first part (has 'COUNT  ' at start)
        first_part = parts[0].replace('COUNT  ', '')
        pred_parts = first_part.split(' matching ')
        result.append([pred_parts[0].strip(), pred_parts[1].strip()])

        # Handle remaining parts
        for part in parts[1:]:
            # Remove everything after ':'
            clean_part = part.split(':')[0]
            pred_parts = clean_part.split(' matching ')
            result.append([pred_parts[0].strip(), pred_parts[1].strip()])

        return result

    # If single COUNT pattern
    else:
        # Remove 'COUNT  ' and everything after ':'
        clean_string = input_string.replace('COUNT  ', '').split(':')[0]
        # Split on 'matching'
        pred_parts = clean_string.split(' matching ')
        return [pred_parts[0].strip(), pred_parts[1].strip()]

def get_matching_predicates(predicate_list, search_items):
    result = []

    # If search_items is not a list of lists, convert it to one
    if not isinstance(search_items[0], list):
        search_items = [search_items]

    for search_item in search_items:
        for pred in predicate_list:
            # For the first item (predicate name), exact match is required
            if pred[0] == search_item[0]:
                # For the second item, split by comma and check if any part matches
                search_values = [x.strip() for x in search_item[1].split(',')]
                if any(val == pred[1] for val in search_values):
                    result.append(pred[2])
                    # print(f"Matched: {search_item[0]}, {pred[1]}")

    return result


def flatten_nested_list(nested_list):
    base = nested_list[:2]  # First two elements are always base elements
    # print("base: ")
    # print(base)
    # print("nestedlist2: ")
    # print(nested_list[2])
    # Check if third item is a list or not
    if not isinstance(nested_list[2], list):
        # If not a list, return single item with the third element as is
        return [nested_list]

    predicates = nested_list[2]  # List of predicates
    # print("predicates: ")
    # print(predicates)

    def process_list(input_list):
        # Convert non-list items to lists and unnest nested lists
        processed_lists = []
        for item in input_list:
            # print("item of input list: ")
            # print(item)
            if not isinstance(item, list):
                # If item is not a list, convert to single-item list
                processed_lists.append([item])
                # print("processed item: ")
                # print([item])
            elif any(isinstance(subitem, list) for subitem in item):
                # If item contains nested lists, extend with those nested lists
                processed_lists.extend(item)
                # print("processed item: ")
                # print(extend(item))
            else:
                # If item is a simple list, add it as is
                processed_lists.append(item)
                # print("processed item: ")
                # print(item)

        # Do product and convert result to list of lists
        result = [list(x) for x in product(*processed_lists)]
        expanded_list = []
        for item in result:
            part = ""

            for attr in item:
                part = part + "; " + attr
            expandeditem = part[2:]
            # print("expandeditem: ")
            # print(expandeditem)
            expanded_list.append(expandeditem)

        # print("expanded list: ")
        # print(expanded_list)
        return expanded_list

    expanded_list = process_list(predicates)
    nested_list = []
    for pred in expanded_list:
        # print("pred: ")
        # print(pred)
        nested_list.append([*base, f"{pred}"])
        # print("appended_line")
        # print([*base, f"{pred}"])
    return nested_list


