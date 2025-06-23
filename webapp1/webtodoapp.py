#How streamlit actually works?
# pip freeze > requirements.txt to get all required apps
#streamlit run webtodo.py
#How streamlit actually works?
#To run the app, in Terminal type "streamlit run webtodo.py"
#For web app, in terminal type "pip freeze > requirements.txt"
#That should create a requirements .txt file in the project which will have all the required packages to be in installed in the server

import streamlit as st
import functions

todos = functions.get_todos()

def add_todo():
    todo = st.session_state["new_todo"] + "\n"
    todos.append(todo)
    functions.write_todos(todos)

st.title("Lucky's Todos")
st.write('To increase productivity!')

for index, todo in enumerate(todos):
    checkbox = st.checkbox(todo, key=todo)
    if checkbox:
        todos.pop(index)
        functions.write_todos(todos)
        del st.session_state[todo]
        st.rerun()

st.text_input(label="Enter a todo: ", placeholder = "Add a new todo...",
              on_change=add_todo, key='new_todo')
