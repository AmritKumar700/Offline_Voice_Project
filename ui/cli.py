# We need to import the dispatcher to send commands to it
from agent.dispatcher import dispatch_command

def main():
    """Main function to run the CLI loop."""
    print("AI Agent CLI is ready. Type 'exit' to quit.")
    while True:
        # Get input from the user
        user_input = input(">>> ")

        # Check for exit condition
        if user_input.lower() == "exit":
            print("Exiting agent. Goodbye!")
            break

        # Dispatch the command and get the result
        result = dispatch_command(user_input)

        # Print the result
        print(result)

if __name__ == "__main__":
    main()