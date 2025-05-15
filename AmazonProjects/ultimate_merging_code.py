#Simplified merging code for predicate data

import win32com.client
import os
import Functions as fu
from numpy.matlib import empty

excel = None
wb = None

try:
    # Get the workbook name
    filepath = input("Please provide the filepath to the workbook: ")

    # Opening the workbook
    file_path = os.path.abspath(filepath) # Get absolute path of the Excel file
    excel = win32com.client.Dispatch("Excel.Application") # Create Excel application object
    excel.Visible = True # Make Excel visible
    wb = excel.Workbooks.Open(file_path) # Open the workbook

    # Build predicate list
    predicate_sheet = wb.Worksheets(input("Please provide the name of the predicate sheet: "))  # ask for predicate sheet name and open it
    predicate_start_col = ord(input("Please provide the start column of predicate data (excluding predicate column): ").upper())
    predicate_end_col = ord(input("Please provide the end column of predicate data: ").upper())
    pred_column_list = [chr(i) for i in range(predicate_start_col, predicate_end_col + 1)] # Create list using list comprehension
    print("Attribute columns of predicate data: ")
    print(pred_column_list)

    pol_pred = "predicate"
    predicate_list = fu.get_pol_pred_list(predicate_sheet,pred_column_list,pol_pred)
    print(predicate_list)

    #printing predicate data in new sheet
    # Add new worksheet
    ws = wb.Sheets.Add()
    ws.Name = pol_pred
    # Write to Excel starting from A1
    for i, row_data in enumerate(predicate_list, start=1):
        for j, value in enumerate(row_data):
            col = chr(ord('A') + j )  # from col A
            cell = f"{col}{i}"
            ws.Range(cell).Value = str(value)[:254]

    # Build policy list
    policy_sheet = wb.Worksheets(input("Please provide the name of the policy sheet: "))  # ask for policy sheet name and open it
    pol_start_col = ord(input("Please provide the start column of policy data (excluding policy name column): ").upper())
    pol_end_col = ord(input("Please provide the end column of policy data: ").upper())
    pol_column_list = [chr(i) for i in range(pol_start_col, pol_end_col + 1)] # Create list using list comprehension
    print("Attribute columns of policy data: ")
    print(pol_column_list)

    pol_pred = "policy"
    Policy_list = fu.get_pol_pred_list(policy_sheet,pol_column_list,pol_pred)
    # Print both lists
    for item in Policy_list:
        print(item)

    #printing policy data in new sheet
    # Add new worksheet
    ws = wb.Sheets.Add()
    ws.Name = pol_pred
    # Write to Excel starting from A1
    for i, row_data in enumerate(Policy_list, start=1):
        for j, value in enumerate(row_data):
            # Convert column number to letter (O=15, P=16, Q=17)
            col = chr(ord('A') + j )  # from col A
            cell = f"{col}{i}"
            ws.Range(cell).Value = str(value)[:254]

    ask_user = input("Do you want to merge policy and predicate data? Y/N: ")
    if ask_user == 'Y':
        pass
    else:
        quit()

    E2EList = []
    for policy_line in Policy_list:
        print(f"Policy line lower is {policy_line[0].lower()}")
        try:
            if policy_line[0].lower() == "policy":
                E2Epolicyline = policy_line
                # print("policy line")
            elif "COUNT  " not in policy_line[2]:
                E2Epolicyline = policy_line
                # print("policy line")
            else:
                # print("not policy line")
                E2Epolicyline = []
                E2Epolicyline = [policy_line[0], policy_line[1]]

                attr_header_attr = policy_line[2].split("; ")
                attr_line = []
                for attr in attr_header_attr:
                    if "COUNT  " not in attr:
                        attr_line.append(attr)
                    else:
                        complete_line = []
                        search_items = fu.parse_count_string(attr)
                        # print(search_items)
                        complete_line = fu.get_matching_predicates(predicate_list, search_items)
                        # print(complete_line)
                        attr_line.append(complete_line)
                E2Epolicyline.append(attr_line)

            E2EList.append(E2Epolicyline)
            # print("for policy line: ")
            # print(policy_line)
            # print("E2E policy line: ")
            # print(E2Epolicyline)

        except Exception as e:
            print(f"Error processing line: {policy_line}")
            print(f"Error message: {str(e)}")

    #print(E2EList)
    # Add new worksheet
    ws = wb.Sheets.Add()
    ws.Name = "expanded_data"

    expanded_list = []
    row = 1
    for policy_item in E2EList:
        flattened_items = fu.flatten_nested_list(policy_item)
        for item in flattened_items:
            expanded_list.append(item)
            print(item)

            for col, value in enumerate(item, start=1):
                ws.Cells(row, col).Value = value[:254]
                if col == 3:
                    attributes = value.split("; ")
                    for colu, value in enumerate(attributes, start=4):
                        ws.Cells(row, colu).Value = value[:254]
            row += 1

    #print(expanded_list)
    print("\nSuccessfully processed all rows")
    print(f"Data written to sheet expanded_data")

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    try:
        wb.Save()
    except Exception as e:
        print(f"Error saving workbook: {str(e)}")