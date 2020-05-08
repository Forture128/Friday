

import socket
import sys


# [START declare variable like example]
ADDR = ''
PORT = 10000
BUFF_SIZE = 4096
device_id = None
server_address = (ADDR, PORT)
# [END declare variable like example]

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(sock, message):
    sock.sendto(message.encode(), server_address)

    # Receive response
    print('Waiting for response.....')
    response = sock.recv(BUFF_SIZE)

    return response

def make_message(device_id, action, data=''):
    if data:
        return '{{ "device" : "{}", "action":"{}", "data" : "{}" }}'.format(device_id, action, data)
    else:
        return '{{ "device" : "{}", "action":"{}" }}'.format(device_id, action)

def run_action(device, action, data=''):
    message = make_message(device_id, action, data)
    if not message:
        return
    print('Send message: {}'.format(message))

    event_response = send_command(client_sock, message).decode('utf-8')
    print('Received response : {}'.format(event_response))


def main():
    device_id = sys.argv[1]
    if not device_id:
        sys.exit('The device Id must be specified')

    print('Bringing up device {}'.format(device_id))
    try:
        run_action(device_id, 'detach')
        run_action(device_id, 'attach')
        run_action(device_id, 'ent', 'LED is online')
        run_action(device_id, 'subscribe')

        while True:
            response = client_sock.recv(BUFF_SIZE)
            message = response.decode('utf-8')
            if message.find("ON") != -1:
                sys.stdout.write(
                    '\r>> ' +" LED is ON " + ' <<')
                sys.stdout.flush()
            elif message.find("OFF") != -1:
                sys.stdout.write(
                    '\r >>' + " LED is OFF " + ' <<')
                sys.stdout.flush()

    finally:
        print('Closing socket')
        client_sock.close()


if __name__ == '__main__':
    main()





