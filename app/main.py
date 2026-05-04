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

def parse_args(args):
    is_in_quotes = False
    is_in_double_quotes = False
    output = []
    curr = ""
    is_escaped = False
    for char in args:
        if char == '\\' and not is_escaped and not is_in_quotes:
            is_escaped = not is_escaped
            continue
        
        if not is_escaped:
            if char == '"' and not is_in_quotes:
                is_in_double_quotes = not is_in_double_quotes
                continue

            if char == "'" and not is_in_double_quotes:
                is_in_quotes = not is_in_quotes
                continue

            if char == " " and not is_in_quotes and not is_in_double_quotes:
                if curr:
                    output.append(curr)
                    curr = ""
                continue
        else:
            is_escaped = not is_escaped

        curr += char

    output.append(curr)

    return output

def process_type_command(args):
    args = args.split()
    for arg in args:
        if is_builtin(arg):
            print(f"{arg} is a shell builtin")
        else:
            file_path = iterate_paths(arg)
            if file_path:
                print(f"{arg} is {file_path}")
            else:
                print(f"{arg}: not found")

def process_echo_command(arg):
    output = parse_args(arg)
    print(*output)

def process_cd_command(arg):
    try:
        if arg == "~":
            os.chdir(os.environ['HOME'])
        else:
            os.chdir(arg)
    except FileNotFoundError:
        print(f"cd: {arg}: No such file or directory")

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
            
        command, *args = user_input.split(" ", 1)
        args = "".join(args)
        match command:
            case 'exit':
                break
            case 'type':
                process_type_command(args) 
            case 'echo':
                process_echo_command(args)
            case 'pwd':
                print(os.getcwd())
            case 'cd':
                process_cd_command(args)  
            case _:
                
                parsed_input = parse_args(user_input)
                command = parsed_input[0]
                args = parsed_input[1:]
                command_path = iterate_paths(command)
                
                if command_path:
                    subprocess.run([command] + args)
                else:
                    print(f"{user_input}: command not found")

    pass

if __name__ == "__main__":
    main()
