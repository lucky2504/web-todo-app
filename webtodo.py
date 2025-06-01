#streamlit run webtodo.py
#How streamlit actually works?

import streamlit as st
import functions

todos = functions.get_todos()

st.title("My Todo App")
st.subheader("This is my todoapp!")
st.write('To increase productivity!')

for todo in todos:
    st.checkbox(todo)


st.text_input(label="Enter a todo: ", placeholder = "Add a new todo...")