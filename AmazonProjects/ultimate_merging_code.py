#Simplified merging code for predicate data

import win32com.client
import os
import Functions as fu

excel = None
wb = None

try:
    #Opening the workbook
    filepath = input("Please provide the filepath to the workbook: ")
    file_path = os.path.abspath(filepath) # Get absolute path of the Excel file
    excel = win32com.client.Dispatch("Excel.Application") # Create Excel application object
    excel.Visible = True # Make Excel visible
    wb = excel.Workbooks.Open(file_path) # Open the workbook

    #Build predicate list
    predicate_sheet = wb.Worksheets(input("Please provide the name of the predicate sheet: ")) #ask for predicate sheet name and open it
    predicate_list = fu.get_predicate_list(predicate_sheet)
    print(predicate_list)

    #Build policy list
    policy_sheet = wb.Worksheets(input("Please provide the name of the policy sheet: "))  # ask for policy sheet name and open it
    Policy_list = fu.get_policy_list(policy_sheet)
    # Print both lists
    print("Policy List:")
    print(Policy_list)

    for item in Policy_list:
        print(item)

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