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
    output = []
    curr = ""

    for char in args:
        if char == "'":
            is_in_quotes = not is_in_quotes
            continue

        if char == " " and not is_in_quotes:
            if curr:
                output.append(curr)
                curr = ""
            continue

        curr += char

    output.append(curr)
    return output

def process_quoted_command(arg):
    is_in_single_quotes = False
    output = ""
    for char in arg:
        if char == "'":
            output += char
            is_in_single_quotes = not is_in_single_quotes
            continue
        
        if char == ' ' and not is_in_single_quotes:
            if output[-1] == ' ':
                continue

        output += char

    return output

def prepare_quoted_arguments(arguments):
    params_output = []
    current_param = ""
    is_in_single_quotes = False
    for char in arguments:
        if char == ' ':
            if is_in_single_quotes:
                current_param += char
                continue
            else:
                if len(current_param) > 0:
                    params_output.append(current_param)
                    current_param = ""
                    continue

        if char == "'":
            if is_in_single_quotes:
                is_in_single_quotes = False
                if len(current_param) > 0:
                    params_output.append(f"'{current_param}'")
                    current_param = ""
                continue
                
            else:
                is_in_single_quotes = True
                if len(current_param) > 0:
                    params_output.append(current_param)
                    current_param = ""
                continue

        
        current_param += char
    
    if len(current_param) > 0:
        params_output.append(current_param)
    
    return params_output

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
                
                args = parse_args(args)
                command_path = iterate_paths(command)
                if command_path:
                    subprocess.run([command] + args)
                else:
                    print(f"{user_input}: command not found")

    pass


if __name__ == "__main__":
    main()
