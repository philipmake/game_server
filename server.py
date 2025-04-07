import socket
import threading
import pandas as pd
import time
from datetime import datetime, timedelta

ip = '127.0.0.1'
port = 6000


def start_server(ip, port):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.bind((ip, port))
    ss.listen(4)
    print("Game server starting....")

    while True:
        conn, addr = ss.accept()
        print(f"Connected to client on address: {addr}")

        # new thread for each client
        client_thread = threading.Thread(target=session, args=(conn,))
        client_thread.start()


def session(conn):
    try:
        conn.sendall('Welcome to your 60 seconds of fame </>  (enter yes or no to start)'.encode('ascii'))
        res = conn.recv(1024).decode().strip().lower()

        if res != 'yes':
            print("Game session aborted.")
            conn.sendall("Game aborted by player.".encode('utf-8'))
            return

        rnd = 0
        duration = timedelta(seconds=60)
        start_time = datetime.now()
        grade = 0

        while datetime.now() - start_time < duration:
            q_and_a = load_question_and_answer(rnd)

            if q_and_a is None:
                msg = "No more questions available. Ending game."
                conn.sendall(msg.encode('utf-8'))
                break

            que, correct_answer = q_and_a
            conn.sendall(f"\nQuestion {rnd + 1}: {que}".encode('utf-8'))

            try:
                user_answer = conn.recv(1024).decode()
                if not user_answer:  # Handle empty response (client disconnected)
                    print("Client disconnected.")
                    break
            except Exception as e:
                print(f"Error receiving answer: {e}")
                break

            if check_answer(correct_answer, user_answer):
                grade += 1
                msg2 = f"\tCorrect! Grade: {grade}"
            else:
                msg2 = f"\tWrong! Grade: {grade}"

            conn.sendall(msg2.encode('ascii'))
            time.sleep(0.5)
            rnd += 1

        final_msg = f"\nTime up! Your final grade is {grade}"
        print(final_msg)
        conn.sendall(final_msg.encode('ascii'))

    except Exception as e:
        print(f"Error during session: {e}")


def load_question_and_answer(i):
    try:
        f = pd.read_csv("math_questions.csv")
        if i >= len(f):
            return None
        row = f.iloc[i].values
        return row
    except FileNotFoundError:
        print("Error: math_questions.csv not found!")
        return None
    except Exception as e:
        print(f"Error loading questions: {e}")
        return None


def check_answer(answer, user_input):
    return str(answer).strip().lower() == str(user_input).strip().lower()


if __name__ == "__main__":
    start_server(ip, port)
