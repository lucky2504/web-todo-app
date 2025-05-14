#using a third party module/library - created by other people which we can use in Python. Can be found on pypi.org
#Download the 3rd party module from settings or enter the installation line in TERMINAL (not Python Console)

import functions
import FreeSimpleGUI as sg

#Child objects to build parts of window
label = sg.Text("Type in a ToDo")
input_box = sg.InputText(tooltip = "Enter todo")
add_button = sg.Button("Add")

window = sg.Window('My To-Do App',
                   layout=[[label], [input_box, add_button]],
                   font=('Helvetica',20)) #Parent object containing all the above objects
window.read() #Displays the window
window.close()



