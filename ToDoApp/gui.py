#using a third party module/library - created by other people which we can use in Python. Can be found on pypi.org
#Download the 3rd party module from settings or enter the installation line in TERMINAL (not Python Console)

import functions
import FreeSimpleGUI as sg

#Child objects to build parts of window
label = sg.Text("Type in a ToDo")
input_box = sg.InputText(tooltip = "Enter todo", key="todo")
add_button = sg.Button("Add")
list_box = sg.Listbox(values=functions.get_todos(), key='todos',
                      enable_events=True, size=[45,10])

edit_button = sg.Button("Edit")
window = sg.Window('My To-Do App',
                   layout=[[label], [input_box, add_button], [list_box, edit_button]],
                   font=('Helvetica',20)) #Parent object containing all the above objects

while True:
    event, values = window.read() #Displays the window
    print(1, event)
    print(2, values)
    print(3, values['todos'])
    match event:
        case "Add":
            todos = functions.get_todos()
            new_todo = values['todo'] + "\n" #todo key output of input_box
            todos.append(new_todo)
            functions.write_todos(todos)
            window['todos'].update(values=todos)
        case "Edit":
            todo_to_edit = values['todos'][0] #As todos output is a string
            new_todo = values['todo'] + "\n"
            todos = functions.get_todos()
            index = todos.index(todo_to_edit)
            todos[index] = new_todo
            functions.write_todos(todos)
            window['todos'].update(values=todos)
        case 'todos':
            window['todo'].update(value=values['todos'][0])

        case sg.WIN_CLOSED:
            break

window.close()



