import os
import sys
import subprocess


def is_builtin(command):
    builtins = ['echo', 'exit', 'type']
    return command in builtins

def iterate_paths(command):
    path_list = os.environ['PATH'].split(os.pathsep)
    for path in path_list:
        file_path = os.path.join(path, command)
        if is_executable(file_path):
            return file_path
    return None

def is_executable(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        if user_input.startswith('type '):
            command = user_input[5:]
            if is_builtin(command):
                print(f"{command} is a shell builtin")
            else:
                file_path = iterate_paths(command)
                if file_path:
                    print(f"{command} is {file_path}")
                else:
                    print(f"{command}: not found")
        
        else:
            if user_input == 'exit':
                break
            if user_input.startswith("echo "):
                print(user_input[5:])
            if user_input == 'pwd':
                print(os.getcwd())
            else:
                input_list = user_input.split()
                command = iterate_paths(input_list[0])

                if command:
                    arguments = input_list[1:]
                    subprocess.run([input_list[0]] + arguments)
                else:
                    print(f"{user_input}: command not found")

    pass


if __name__ == "__main__":
    main()
