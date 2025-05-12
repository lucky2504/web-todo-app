FILEPATH = "../Files/todos.txt"

def get_todos(filepath=FILEPATH):
    """ Opens and reads the file "todos.txt"
        Returns the list in todos.txt
    """
    with open(filepath, 'r') as file_local:
        todos_local = file_local.readlines()
    return todos_local

def write_todos(todos_arg,filepath=FILEPATH):
    """ Opens the "todos.txt" file and writes into it. """
    with open(filepath, 'w') as file:
        file.writelines(todos_arg)

print(__name__)

if __name__ == "__main__":
    print("hello from functions")
    print(get_todos())