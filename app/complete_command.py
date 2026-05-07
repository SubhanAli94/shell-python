from typing import Dict

completions : Dict[str, str] = {}

def process_complete_command(args, argl):
    global completions

    if(len(argl) == 2 and argl[0] == '-p'):
        if not completions:
            print(f"complete: {argl[-1]}: no completion specification")
        else: 
            completion = completions.get(argl[1])
            print(f"complete -C '{completion}' {argl[1]}")
    
    if(len(argl) == 3 and argl[0] == "-C"):
        if not completions.get(argl[2]):
            completions[argl[2]] = argl[1] # e.g. (git, <PATH>)
