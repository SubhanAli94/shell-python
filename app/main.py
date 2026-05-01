import sys


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        if user_input.startswith('type '):
            if user_input[5:] == 'echo' or user_input[5:] == 'exit' or user_input[5:] == 'type':
                print(f"{user_input[5:]} is a shell builtin")
            else:
                print(f"{user_input[5:]}: not found")
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
