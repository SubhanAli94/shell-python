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
    file_name = ""
    for idx, char in enumerate(args):
        if (char == '>' or (char == '1' and args[idx + 1] == ">")) and not is_escaped and not is_in_quotes and not is_in_double_quotes:
            file_name = args[idx+1:].strip()
            if curr: output.append(curr)
            return output, file_name

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

    return output, file_name

def process_type_command(args):
    args = args.split()
    for arg in args:
        if is_builtin(arg):
            return f"{arg} is a shell builtin"
        else:
            file_path = iterate_paths(arg)
            if file_path:
                return f"{arg} is {file_path}"
            else:
                print(f"{arg}: not found")
                return None

def process_cd_command(arg):
    try:
        if arg == "~":
            os.chdir(os.environ['HOME'])
        else:
            os.chdir(arg)
    except FileNotFoundError:
        print(f"cd: {arg}: No such file or directory")

def write_output_to_file(file_name, output):
    with open(file_name, 'w') as file:
        file.write(output)

def main():
    
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        parsed_input, file_name = parse_args(user_input)
        command = parsed_input[0]
        argl = parsed_input[1:]
        args = " ".join(parsed_input[1:])

        match command:
            case 'exit':
                break
            case 'type':
                output = process_type_command(args) 
                if output != None and file_name:
                    write_output_to_file(file_name, output)
                elif output != None:
                    print(output)
            case 'echo':
                if file_name:
                    write_output_to_file(file_name, args)
                else:
                    print(args)
            case 'pwd':
                output = os.getcwd()
                if file_name:
                    write_output_to_file(file_name, output)
                else:
                    print(output)
            case 'cd':
                process_cd_command(args)  
            case _:
                command_path = iterate_paths(command)
                if command_path:
                    p = subprocess.run([command] + argl, capture_output=True, text=True)
                    
                    if p.stderr:
                        print(p.stderr)
                    elif file_name:
                        write_output_to_file(file_name, p.stdout)
                    else:

                        print(p.stdout.strip())

                else:
                    print(f"{user_input}: command not found")
        
        file_name = ""
                    
    pass

if __name__ == "__main__":
    main()
