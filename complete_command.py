def process_complete_command(args, argl):
    if(len(argl) == 2 and argl[0] == '-p'):
        print(f"complete: {argl[-1]}: no completion specification")