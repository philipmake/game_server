import socket

port = 6000
ip = '127.0.0.1'

# Create a socket and connect to the server
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    ss.connect((ip, port))
    print("Connected to game server.")

    # ✅ Wait for the first message (welcome prompt)
    data = ss.recv(1024).decode().strip()
    print(data)  # Show welcome message

    # ✅ Now, ask the user for input (yes or no)
    message = input(">> ").strip().lower()
    ss.sendall(message.encode("ascii"))

    # If the user said "no", exit immediately
    if message != "yes":
        print("Exiting game...")
        ss.close()
        exit()

    while True:
        # Receive the next message from server
        data = ss.recv(1024).decode().strip()
        if not data:
            print("Server closed the connection.")
            break

        print(f"{data}")

        # Exit if game is over or aborted
        if "Time up!" in data or "Game aborted" in data:
            break

        # Only ask for input if it's a question
        if "Question" in data:
            answer = input("Your answer: ").strip()

            # Allow user to exit manually
            if answer.lower() == "exit":
                print("Exiting game...")
                ss.sendall("exit".encode("ascii"))
                break

            # Send answer to server
            ss.sendall(answer.encode("ascii"))

except ConnectionError:
    print("Lost connection to the server.")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Closing connection...")
    ss.close()
