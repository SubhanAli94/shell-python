import os
import sys


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        if user_input.startswith('type '):
            command = user_input[5:]
            if command == 'echo' or command == 'exit' or command == 'type':
                print(f"{command} is a shell builtin")
            else:
                executable_to_find = command
                path_list = os.environ['PATH'].split(os.pathsep)
                for path in path_list:
                    file_path = os.path.join(path, executable_to_find)
                    if(os.path.isfile(file_path)):
                        if(os.access(file_path, os.X_OK)):
                            print(f"{executable_to_find} is {file_path}")
                            break
                        else:
                            print(f"{command}: not found")
                        
                else:
                    print(f"{command}: not found")
        else:
            if user_input == 'exit':
                break
            
            if user_input.startswith("echo "):
                print(user_input[5:])
            else:
                print(f"{user_input}: command not found")

    pass


if __name__ == "__main__":
    main()
