#Functions for policy and predicate data merging
import win32com.client
import os
from itertools import product


def get_pol_pred_list(policysheet, pol_pred_column_list, pol_pred):
    # Select the sheet with "policies" data
    sheet = policysheet
    col_list = pol_pred_column_list
    po_pr = pol_pred

    # Find the last row in column A
    last_row = sheet.Cells(sheet.Rows.Count, "A").End(-4162).Row

    policy_list = []
    end_to_end_line_item_list = []
    # Process each row to build the policy_list line item
    for row in range(1, last_row + 1):
        #print(f"Processing {row}")
        policy_line = []
        end_to_end_line = []
        # Check if first column had header as policy
        if sheet.Range(f"A{row}").Value == po_pr:
            policy_row = row
            #policy string
            value = sheet.Range(f"A{row}").Value
            policy_line.append(value)

            #attr string
            value = ""
            for col in col_list:
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
            for col in col_list:
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
    base = nested_list[:3]  # First two elements are always base elements
    # print("base: ")
    # print(base)
    # print("nestedlist2: ")
    # print(nested_list[2])
    # Check if third item is a list or not
    if not isinstance(nested_list[3], list):
        # If not a list, return single item with the third element as is
        return [nested_list]

    predicates = nested_list[3]  # List of predicates
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

def list_to_string(lst):
    return ', '.join(map(str, lst))

# Code to get all attributes used in each line item of policy when end to end line is in column 3
def get_all_attr_used(expanded_list):
    index_of_item = 0
    pol_attr_list = []
    for item in expanded_list:

        if item[1] == 'Output':
            item.append("Attributes used: ")  # Add empty column for consistency
            if pol_attr_list == []:
                pol_index = index_of_item
                pass
            else:
                pol_attr_list = list(set(pol_attr_list))
                pol_attr = (", ".join(pol_attr_list))
                expanded_list[pol_index][5] = pol_attr
                pol_attr_list = []
            continue

        attr_list = []

        try:
            # Split the attribute line into individual predicates
            pred_list = item[3].split("; ")

            # Extract attribute names
            for pred_item in pred_list:
                pred_string = pred_item.split(": ")[0]
                attr_list.append(pred_string)
                pol_attr_list.append(pred_string)

            # Remove duplicates and sort
            attr_list = list(set(attr_list))
            attr_list.sort()

            # Create the attributes string
            if attr_list:
                item.append(", ".join(attr_list))
            else:
                item.append("")

        except Exception as e:
            print(f"Error processing row: {item}")
            print(f"Error: {str(e)}")
            item.append("")  # Add empty column in case of error

    pol_attr_list = list(set(pol_attr_list))
    pol_attr = (", ".join(pol_attr_list))
    expanded_list[pol_index + 1][5] = pol_attr

    return expanded_list

#Change headers of predicate and policy columns
def change_headers(pol_pred_list):
    for index_of_item in range(len(pol_pred_list) - 1):  # Stop one item before the end
        current_item = pol_pred_list[index_of_item]
        next_item = pol_pred_list[index_of_item + 1]

        if current_item[0] in ['policy', 'predicate']:
            if next_item[0] in ['policy', 'predicate']:
                current_item[0] = "Name of policy/predicate"
                current_item[2] = "E2E_Line"
            else:
                current_item[0] = next_item[0]

    return pol_pred_list

def expand_list(first_list,second_list):
    Policy_list = first_list
    predicate_list = second_list
    E2EList = []
    for policy_line in Policy_list:

        try:
            if policy_line[0] == "Name of policy/predicate" or policy_line[1] == "Output":
                E2Epolicyline = policy_line
                E2Epolicyline.append("E2E_Attribute_Line")
                E2Epolicyline.append("Predicates used?")
                # print("policy line")
            elif "COUNT  " not in policy_line[2]:
                E2Epolicyline = policy_line
                E2Epolicyline.append(policy_line[2])
                E2Epolicyline.append("No")
                # print("policy line")
            else:
                # print("not policy line")
                E2Epolicyline = policy_line
                attr_header_attr = policy_line[2].split("; ")
                attr_line = []
                for attr in attr_header_attr:
                    if "COUNT  " not in attr:
                        attr_line.append(attr)
                    else:
                        complete_line = []
                        search_items = parse_count_string(attr)
                        # print(search_items)
                        complete_line = get_matching_predicates(predicate_list, search_items)
                        # print(complete_line)
                        if complete_line == []:
                            complete_line = [f"Predicate values did not match for {attr}"]
                        else:
                            pass
                        attr_line.append(complete_line)
                E2Epolicyline.append(attr_line)
                E2Epolicyline.append("Yes")

            E2EList.append(E2Epolicyline)
            # print("for policy line: ")
            # print(policy_line)
            # print("E2E policy line: ")
            # print(E2Epolicyline)

        except Exception as e:
            print(f"Error processing line: {policy_line}")
            print(f"Error message: {str(e)}")

    print("E2E List: ")
    print(E2EList)


    expanded_list = []
    row = 1
    for policy_item in E2EList:
        flattened_items = flatten_nested_list(policy_item)
        for item in flattened_items:
            expanded_list.append(item)
            print("Flattened item: ")
            print(item)

            row += 1
    return expanded_list
