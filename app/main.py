import sys


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input()
        
        if user_input == 'exit':
            break
        print(f"{user_input}: command not found")

    pass


if __name__ == "__main__":
    main()
