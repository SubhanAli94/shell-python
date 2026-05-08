import os
import subprocess
import readline
import sys
from typing import List, Dict

BUILT_INS = ['echo', 'exit', 'type', 'pwd', 'complete']
matches = []
lcp = ""
completions : Dict[str, str] = {}

def is_registred_completer(command):
    global completions
    return completions.get(command) != None

def process_complete_command(args, argl):
    global completions

    if(len(argl) == 2 and argl[0] == '-p'):
        if not completions:
            print(f"complete: {argl[-1]}: no completion specification")
        else: 
            if is_registred_completer(argl[1]):
                completion = completions.get(argl[1])
                print(f"complete -C '{completion}' {argl[1]}")
            else:
                print(f"complete: {argl[-1]}: no completion specification")
    
    if(len(argl) == 3 and argl[0] == "-C"):
        if not completions.get(argl[2]):
            completions[argl[2]] = argl[1] # e.g. (git, <PATH>)

def run_complete_process(args, env):
    try:
        op = subprocess.run(args, capture_output=True, text=True, env=env)
        stripped_op = op.stdout.strip()
        if stripped_op:
            op_list = op.stdout.strip().split('\n')
            op_list = [f"{op} " for op in op_list] 
            return op_list
    except Exception as e:
        print(f"error: {type(e).__name__}: {e}")
        return []

    return []

#Not used anywhere
def find_longest_common_prefix(arr: List[str]):
    if not arr : return ""
    if len(arr) == 1: return arr[0]

    first_word = arr[0]

    for idx, char in enumerate(first_word):
        for item in arr:
            if idx >= len(item) or item[idx] != char:
                return first_word[:idx]
    
    
    return first_word

def get_file_or_dir_matches(text = '', dir_path = '.'):
    global lcp

    res = [fn for fn in os.listdir(dir_path) if fn.startswith(text)]
    
    dirs = [dir for dir in res if os.path.isdir(os.path.join(dir_path, dir))]
    files = [file for file in res if os.path.isfile(os.path.join(dir_path, file))]

    if len(dirs) == 1 and not files:
        return [f"{dirs[0]}{os.sep}"]
    
    if len(files) == 1 and not dirs:
        return [f"{files[0]} "]
    
    # if not lcp:
    #     print(f"here:  {lcp}")
    #     lcp = find_longest_common_prefix(res)
    #     if lcp: return [lcp]

    dirs = [f"{dir}{os.sep}" for dir in dirs]
    files = [f"{file} " for file in files]    
    return dirs + files

def get_env_for_completion(input_line):
    byte_len = len(input_line.encode('utf-8'))
    env = os.environ.copy()
    env["COMP_LINE"] = input_line
    env["COMP_POINT"] = f"{byte_len}"

    return env

def auto_complete(text, state):
    global matches
    global lcp

    if state == 0:
        line = readline.get_line_buffer() 
        ll = line.split()
        if len(ll) == 1:
            if completions.get(ll[0]):
                cmd = completions.get(ll[0])
                env = get_env_for_completion(line)
                matches = run_complete_process([cmd], env)
            else:
                if text:
                    matches = [f"{bi} " for bi in BUILT_INS if bi.startswith(text)] or \
                        [f"{os.path.basename(ex)} " for ex in find_executable_paths(text)]
                else:
                    matches = get_file_or_dir_matches()
        elif len(ll) > 1:
            if is_registred_completer(ll[0]):
                env = get_env_for_completion(line)
                args = []
                args.append(completions.get(ll[0]))
                args.append(ll[0])
                args.append(ll[-1])
                args.append(ll[-2])
                matches = run_complete_process(args, env)
            else:
                p = os.path.dirname(line.split()[-1]) if "/" in line.split()[-1] else '.'
                matches = get_file_or_dir_matches(text, p)

        if not matches: 
            print('\x07', end='')
            return None

    try:
        return matches[state]
    except IndexError:
        matches = []
        return None
  
def find_executable_paths(arg, tab_completion = True):
    path_list = os.environ['PATH'].split(os.pathsep)
    all_paths = []

    for path in path_list:
        try:
            all_files = os.listdir(path)
        except:
            continue

        #if exact file names are requires
        if not tab_completion:
            all_files = [os.path.join(path, af) for af in all_files if af == arg and is_executable_v2(os.path.join(path, af))]

        #if paths for tab completion is required
        elif tab_completion:
            all_files = [os.path.join(path, af) for af in all_files if af.startswith(arg) and is_executable_v2(os.path.join(path, af))]

        all_paths.extend(all_files)
    return all_paths

def is_executable_v2(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def process_executable_request(command):
    file_paths = find_executable_paths(command, tab_completion=False)
    try:
        return file_paths[0]
    except:
        None

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
        
        elif char == '>' and idx+1 < len(args) and args[idx+1] ==">":
            idx = idx + 2
            if not is_escaped and not is_in_quotes and not is_in_double_quotes: 
                o_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                if curr: output.append(curr)
                return output, o_file_name, None, 'a'


        if char == '2' and idx+2 < len(args) and args[idx+1] == ">" and args[idx+2] == ">":
            idx = idx + 3
            if not is_escaped and not is_in_quotes and not is_in_double_quotes: 
                err_file_name = "".join([arg for arg in args[idx:].strip() if arg != '"'])
                write_output_to_file(err_file_name, "", 'a')
                return output, None, err_file_name, 'a'

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
        if arg in BUILT_INS:
            return f"{arg} is a shell builtin"
        else:
            file_path = process_executable_request(arg)
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
        output += '\n' if output else ''
        file.write(output)
        
def main():
    
    readline.set_completer(auto_complete)
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind('bind ^I rl_complete')
    else:
        readline.parse_and_bind('tab: complete')
    
    while True:
        user_input = input("$ ")
        
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
            case 'complete':
                process_complete_command(args, argl)

            case 'echo':
                write_output_to_file(op_file_name, args, file_mode) if op_file_name else print(args)
                    
            case 'pwd':
                output = os.getcwd()
                file_name = op_file_name or err_file_name
                write_output_to_file(file_name, output, file_mode) if file_name else print(output)
            case 'cd':
                process_cd_command(args)  
            case _:
                command_path = process_executable_request(command)
                if not command_path:
                    print(f"{user_input}: command not found")
                else:  
                    p = subprocess.run([command] + argl, capture_output=True, text=True)
                    
                    stripped_err = p.stderr.strip()
                    stripped_op = p.stdout.strip()
                    if stripped_err:
                        if err_file_name:
                            write_output_to_file(err_file_name, stripped_err, file_mode)
                        
                        elif op_file_name:
                            write_output_to_file(op_file_name, '', file_mode)
                            print(stripped_err)
                        else:
                            print(stripped_err)
                        

                    if stripped_op:
                        if op_file_name:
                            write_output_to_file(op_file_name, stripped_op, file_mode)
                        else:
                            print(stripped_op)
                    
    pass

if __name__ == "__main__":
    main()
