import sys


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        if user_input == 'exit':
            break
        
        if user_input.startswith("echo "):
            print(user_input[5:])
        else:
            print(f"{user_input}: command not found")

    pass


if __name__ == "__main__":
    main()
