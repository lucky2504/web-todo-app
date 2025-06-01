#using a third party module/library - created by other people which we can use in Python. Can be found on pypi.org
#Download the 3rd party module from settings or enter the installation line in TERMINAL (not Python Console)

import functions
import FreeSimpleGUI as sg
import time

sg.theme("Black")

#Child objects to build parts of window
clock = sg.Text('', key = "clock")
label = sg.Text("Type in a ToDo")
input_box = sg.InputText(tooltip = "Enter todo", key="todo")
add_button = sg.Button("Add", size=10)
list_box = sg.Listbox(values=functions.get_todos(), key='todos',
                      enable_events=True, size=[45,10])
edit_button = sg.Button("Edit")
complete_button = sg.Button("Complete")
exit_button = sg.Button("Exit")

window = sg.Window('My To-Do App',
                   layout=[[clock],
                           [label],
                           [input_box, add_button],
                           [list_box, edit_button, complete_button],
                           [exit_button]],
                   font=('Helvetica',20)) #Parent object containing all the above objects

while True:
    event, values = window.read(timeout=6000) #Displays the window
    window["clock"].update(value = time.strftime("%b %d, %Y %H:%M"))
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
            try:
                todo_to_edit = values['todos'][0] #As todos output is a string
                new_todo = values['todo'] + "\n"
                todos = functions.get_todos()
                index = todos.index(todo_to_edit)
                todos[index] = new_todo
                functions.write_todos(todos)
                window['todos'].update(values=todos)
            except IndexError:
                sg.popup("Please select an item first.", font=("Helvetica",20)) #Error handling
        case "Complete":
            try:
                todo_to_complete = values['todos'][0]
                todos = functions.get_todos()
                todos.remove(todo_to_complete)
                functions.write_todos(todos)
                window['todos'].update(values=todos)
                window['todo'].update(value='')
            except IndexError:
                sg.popup("Please select an item first.", font=("Helvetica", 20))
        case "Exit":
            break
        case 'todos':
            window['todo'].update(value=values['todos'][0])

        case sg.WIN_CLOSED:
            break

window.close()



