#from functions import the pre-defined functions

import Python20Apps.functions #Local module - written by developer
import time #Standard module - written by Python code developers
#complete list of Python modules are present in the link

now = time.strftime("%b %d, %Y %H:%M:%S")
print("It is",now)

prompt1 = "Type Add followed by action or Show or Edit followed by number of action to be edited or Complete followed by number of action completed or Exit: "
prompt2 = "Enter a new_todo: "
prompt4 = "Enter the number of the action to be edited: "
prompt5 = "Enter the number of action that is completed: "

while True:
    user_action = input(prompt1).capitalize()
    user_action = user_action.strip()

    if user_action.startswith("Add"):

        todos = Python20Apps.functions.get_todos()

        todo = user_action[4:] + "\n"
        todo = todo.capitalize()
        todos.append(todo)

        Python20Apps.functions.write_todos(todos)

    elif user_action.startswith("Show"):

        todos = Python20Apps.functions.get_todos()

        for index, item in enumerate(todos):
            item = item.strip('\n')
            item = f"{index+1}-{item}"
            print(item)

    elif user_action.startswith("Edit"):
        try:

            todos = Python20Apps.functions.get_todos()

            number = int(user_action[5:]) - 1
            print(todos[number])
            new_todo = input(prompt2)
            todos[number] = new_todo.capitalize() + '\n'
            Python20Apps.functions.write_todos(todos)
        except ValueError:
            print("Your command is not valid!")
            continue

    elif user_action.startswith("Complete"):
        try:

            todos = Python20Apps.functions.get_todos()

            number = int(user_action[9:]) - 1
            print(todos[number])
            completed_todo = todos[number].strip('\n')
            todos.pop(number)
            Python20Apps.functions.write_todos(todos)
            message = f"Todo {completed_todo} was removed from the list"
            print(message)
        except IndexError:
            print("The action number is out of range!")
            continue

    elif user_action.startswith("Exit"):
        break

    else:
        print("Command is not valid!")

print("Bye!")