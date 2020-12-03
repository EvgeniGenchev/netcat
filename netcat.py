import sys 
import socket
import getopt
import threading
import subprocess

listen 				= False
command 			= False
upload 				= False
execute 			= ''
target 				= ''
upload_destination 	= ''
port 				= 0

def client_handler(client_socket):
	global upload
	global execute
	global command

	if upload_destination:
		file_buffer = ''

		while True:
			data = client_socket.recv(1024)

			if data:
				file_buffer += data
			else:
				break

		try:
			file_descriptor = open(upload_destination, 'wb')
			file_descriptor.write(file_buffer)
			file_descriptor.close()

			client_socket.send(f"[*] Successfully saved file to {upload_destination}".encode('utf-8'))

		except:
			client_socket.send(f"[*] Failed to saved file to {upload_destination}".encode('utf-8'))	

	if execute:

		output = run_command(execute)

		client_socket.send(output)

	if command:

		while True:
			client_socket.send("<Ge:#> ")

			cmd_buffer = ''

			while "\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024)

			response = run_command(cmd_buffer)

			client_socket.send(response)	

def server_loop():
	global target

	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target, port))

	server.listen(5)

	while True:

		client_socket, addr = server.accept()

		client_thread = threading.Thread(target=client, args=(client_socket,))
		cliet_thread.start()

def run_command(command):
	command = command.rstrip()

	try:
		output = subprocess.check_output(command, suderr=subprocess.STDOUT, shell=True)
	except:
		output = "Command execution failed!"

	return output

def client_sender(buff):

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		client.connect((target, port))

		if len(buff):
			client.send(buff)

		while True:

			recv_len = 1
			response = ""

			while recv_len:
				data      = client.recv(4096)
				recv_len  = len(data)
				response += data

				if recv_len < 4096:
					break

				print(response.decode())

				buff  = input()
				buff += '\n'

				client.send(buff)
	except:
		print("[*] Exception! Exiting.")
		client.close()

def check_int(num):
	try:
		return int(num)
	except ValueError:
		print("Port has to be a positive integer")


def check_ip(ip):
	try:
		if len(ip_list := ip.split('.')) == 4:
			for i in ip_list: 
				assert	0 <= int(i) <= 255
		else: 
			raise ValueError
	except (ValueError , AssertionError):
		assert False, "Invalid IP address"
	return ip


def usage():

	help_msg = """
Usage: genet.py -t target_host -p port

-l --listen                  - listen on [host]:[port] for incoming connection
-e --execute=file_to_run     - execute the given file upon receiving a connection
-c --command 	             - initialize a command shell
-u --upload=destination      - upon receiving a connection upload a file and write to [destination]

Examples:
genet.py -t 192.168.0.1 -p 5555 -l -c
genet.py -t 192.168.0.1 -p 5555 -l -u=path/to/target
genet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"
echo 'Kenobi' | ./genet.py -t 192.168.11.12 -p 135 -
"""

	print(help_msg)
	sys.exit(0)

def main():
	global listen 
	global comand
	global upload
	global execute
	global target
	global upload_destination
	global port

	args_list = sys.argv[1:]

	if not len(args_list):
		usage()

	try:

		shortopts = "hle:t:p:cu"
		longopts = ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload']
		opts, args = getopt.getopt(args_list, shortopts, longopts)

	except getopt.GetoptError as err:
		print(str(err))
		usage() 

	for op, ac in opts:
		print(op, ac)
		if op in ('-h', '--help'): usage()
		elif op in ('-l', '--listen'): listen = True
		elif op in ('-e', '--execute'): execute = ac
		elif op in ('-c', '--commandshell'): commandshell = True
		elif op in ('-u', '--upload'): upload_destination = ac
		elif op in ('-t', '--target'): target = check_ip(ac)
		elif op in ('-p', '--port'): port = check_int(ac)	
		else: assert False, "Unknown command"

	if not listen and len(target) and port > 0:
		
		buff = sys.stdin.read()
		client_sender(buff)

	if listen:
		server_loop()

main()




