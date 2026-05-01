import os
import sys
import subprocess


def is_builtin(command):
    builtins = ['echo', 'exit', 'type', 'pwd']
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
                is_in_single_quotes = False
                output = ""
                for char in user_input[5:]:
                    if char == "'":
                        is_in_single_quotes = not is_in_single_quotes
                        continue
                    
                    if char == ' ' and not is_in_single_quotes:
                        if output[-1] == ' ':
                            continue

                    output += char

                print(output)
            elif user_input == 'pwd':
                print(os.getcwd())
            elif user_input.startswith("cd "):
                try:
                    if user_input[3:] == "~":
                        os.chdir(os.environ['HOME'])
                    else:
                        os.chdir(user_input[3:])
                except FileNotFoundError:
                    print(f"cd: {user_input[3:]}: No such file or directory")
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
