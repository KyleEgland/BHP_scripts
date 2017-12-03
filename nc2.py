#! python3
# This is a revision to the netcat program created in the Black Hat Python book
import argparse
import socket
import threading
import subprocess


def client_sender(buffer, target, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to our target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)
        while True:
            # Now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # Wait for more input
            buffer = input("")
            buffer += "\n"

            # Send it off
            client.send(buffer)
    except Exception as e:
        print('[-] ERR:  {}'.format(e))
        print("[*] Exception! Exiting.")

        # Tear down the connection
        client.close()


def server_loop(port, target='0.0.0.0'):
    # If no target is defined, we listen on all interfaces

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()


def run_command(command):
    # Trim the newline
    command = command.rstrip()

    # Run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                         shell=True)
    except Exception as e:
        print('[-] ERR:  {}'.format(e))
        output = "Failed to execute command.\r\n"

    # Send the output back to the client
    return output


def client_handler(client_socket, upload_dest, execute, command):
    # Check for upload
    if len(upload_dest):

        # Read in all of the bytes and write to our destination
        file_buffer = ""

        # Keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # Now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_dest, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Acknowledge that we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n" %
                               upload_dest)
        except Exception as e:
            print('[-] ERR:  {}'.format(e))
            client_socket.send("Failed to save file to %s\r\n" %
                               upload_dest)

        # Check for command execution
        if len(execute):
            # Run the command
            output = run_command(execute)

            client_socket.send(output)

    # Now we go into another loop if a command shell was requested
    if command:
        while True:
            # Show a simple prompt
            client_socket.send("<NCR:#> ")

            # Now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Send back the command output
            response = run_command(cmd_buffer)

            # Send back the response
            client_socket.send(response)


def main():
    desc = 'Netcat-like program made using Python 3.'
    use = '\n\
nc2.py -t 192.168.0.1 -p 5555 -l -c\n\
nc2.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe\n\
nc2.py -t 192.168.0.1 -p 5555 -l -e "cat /etc/passwd"'
    parser = argparse.ArgumentParser(description=desc, usage=use)
    parser.add_argument('-t', '--target', type=str,
                        help='Input the IPv4 address of target machine.')
    parser.add_argument('-p', '--port', type=int,
                        help='Input number of target port')
    parser.add_argument('-e', '--execute', type=str,
                        help='Execute the given file upon receiving a \
connection')
    parser.add_argument('-c', '--command', type=str,
                        help='Initialize a command shell')
    parser.add_argument('-u', '--upload', type=str,
                        help='Upon receiving connection, upload a file and \
write to [destination].  Usage "--upload=destination"')

    args = parser.parse_args()


if __name__ == '__main__':
    main()
