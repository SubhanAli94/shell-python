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
    o_file_name = ""
    for idx, char in enumerate(args):

        if char == '1' and idx+2 < len(args) and args[idx+1] ==">" and args[idx+2] ==">":
            idx = idx + 3
            if not is_escaped and not is_in_quotes and not is_in_double_quotes: 
                o_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                if curr: output.append(curr)
                return output, o_file_name, None, 'a'
        
        if char == '>' and idx+1 < len(args) and args[idx+1] ==">":
            idx = idx + 2
            if not is_escaped and not is_in_quotes and not is_in_double_quotes: 
                o_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                if curr: output.append(curr)
                return output, o_file_name, None, 'a'

        if char == '2' and idx+1 < len(args) and args[idx +1] == ">":
            idx = idx + 2
            if not is_escaped and not is_in_quotes and not is_in_double_quotes: 
                err_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                write_output_to_file(err_file_name, "")
                return output, None, err_file_name, 'w'

        if char == '1' and idx + 1 < len(args) and args[idx + 1] == ">":
            idx = idx + 2
            if not is_escaped and not is_in_quotes and not is_in_double_quotes:
                o_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                if curr: output.append(curr)
                return output, o_file_name, None, 'w'
        elif char == ">":
            idx = idx + 1
            if not is_escaped and not is_in_quotes and not is_in_double_quotes:
                o_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                if curr: output.append(curr)
                return output, o_file_name, None, 'w'

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

    return output, o_file_name, None, 'w'

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

def write_output_to_file(file_name, output, file_mode = 'w'):
    with open(file_name, file_mode) as file:
        output += '\n' if file_mode == 'a' else ''
        file.write(output)


def main():
    
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        parsed_input, op_file_name, err_file_name, file_mode = parse_args(user_input.strip())
        command = parsed_input[0]
        argl = parsed_input[1:]
        args = " ".join(parsed_input[1:])

        match command:
            case 'exit':
                break
            case 'type':
                if (output := process_type_command(args)) is not None:
                    file_name = op_file_name or err_file_name
                    write_output_to_file(file_name, output, file_mode) if file_name else print(output)
                    
            case 'echo':
                write_output_to_file(op_file_name, args, file_mode) if op_file_name else print(args)
                    
            case 'pwd':
                output = os.getcwd()
                file_name = op_file_name or err_file_name
                write_output_to_file(file_name, output, file_mode) if file_name else print(output)
            case 'cd':
                process_cd_command(args)  
            case _:
                command_path = iterate_paths(command)
                if not command_path:
                    print(f"{user_input}: command not found")
                else:  
                    p = subprocess.run([command] + argl, capture_output=True, text=True)
                    
                    for file_name, output in [(op_file_name, p.stdout), (err_file_name, p.stderr)]:
                        if output and (stripped := output.strip()):
                            write_output_to_file(file_name, stripped, file_mode) if file_name else print(stripped)
                    
    pass

if __name__ == "__main__":
    main()
