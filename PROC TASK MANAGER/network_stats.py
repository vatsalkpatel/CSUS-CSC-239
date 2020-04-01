import struct
import os
import socket

#gloabla variables filenames
tcp_file_path = "/proc/net/tcp"
udp_file_path = "/proc/net/udp"
proc_path = "/proc"
passwd_file = '/etc/passwd'


class TcpUdp():

	def __init__(self):
		self.tcp_connections = None
		self.udp_connections = None
		self.process_paths = None
		self.matching_nodes = None



	#   [['udp', '0.0.0.0', '0.0.0.0', 'avahi', '22088'], ['avahi-daemon']]
	#    protocol  local_address destnitation_address username inode  program name 
	def get_active_tcp_conncetions(self):

		self.tcp_connections = self.get_tcp_connections_data()
		self.udp_connections = self.get_udp_connections_data()

		self.process_paths = get_process_paths()
		#print self.process_paths
		self.matching_nodes = self.match_inode()


		#additional code for reverseip_lookup
		for node in self.matching_nodes:
			try:
				node[0][1] = socket.gethostbyaddr(  str(node[0][1]) ) [0]
				node[0][2] = socket.gethostbyaddr(  str(node[0][2]) ) [0]
			except:
				pass


		#print self.matching_nodes
		return self.matching_nodes

	def match_inode(self):

		matches = []
		for process in self.process_paths:
			inode_list = self.get_process_info(process)
			if inode_list == None:
				continue

			#time.sleep(1)
			for connection in self.tcp_connections:
				for inode in inode_list[1]:
					if inode == int(connection[4]):
						matches.append([connection, inode_list[0]])


			for connection in self.udp_connections:
				for inode in inode_list[1]:
					if inode == int(connection[4]):
						matches.append([connection, inode_list[0]])


		matches_final = []
		for connection in matches:
			user_name = self.get_user_name(connection[0][3])
			connection[0][3] = user_name

		return matches

	
	def get_user_name(self, user_id):
		all_users = self.read_passwd_file()
		userid = str(user_id)
		#print all_users
		user_name = None
		for user in all_users:
			#print userid, "     ",  user[2], "    ", user[0] 
			if userid == user[2]:
				user_name =  user[0]
				break

		return user_name
		

	def read_passwd_file(self):
		fp = open(passwd_file)
		all_users = []
		for line in fp:
			count = 0
			data = ''
			for char in line:
				if char == ':':
					count += 1
				if count == 3:
					break
				else:
					data += char

			data = data.split(':')
			all_users.append(data)

		return all_users



	def get_process_info(self, process):

		program_name = self.get_program_name(process)
		fd_paths = get_inode_numbers_of_process(process)

		each_process_fd = [program_name, fd_paths]

		return each_process_fd

		
	def get_program_name(self, process):

		file_name = process + "/stat"


		fd = None
		lines = []
		try:
			fd = open(file_name)

			lines = []
			for line in fd:
				lines.append(line.split()[1][1:-1])
			
		except Exception as e:
			pass

		return lines


	def get_tcp_connections_data(self):
		fp = open(tcp_file_path)

		
		lines = []
		for line in fp:
			lines.append(line.split())

		tcp_data = []
		for info in lines[1:]:
			local_addr = info[1][:8]
			rem_addr = info[2][:8]
			user_id = info[7]
			inode = info[9]
			local_port = int(info[1][9:], 16)
			rem_port = int(info[2][9:], 16)

			temp = []

			# convert the addresses to hex to ip
			local_address =  socket.inet_ntoa(struct.pack("<L", int(local_addr, 16)))
			rem_address =  socket.inet_ntoa(struct.pack("<L", int(rem_addr, 16)))

			temp.append('tcp')
			temp.append(local_address)
			temp.append(rem_address)
			temp.append(user_id)
			temp.append(inode)
			temp.append(local_port)
			temp.append(rem_port)
			

			tcp_data.append(temp)


		return tcp_data



	def get_udp_connections_data(self):
		fp = open(udp_file_path)

		
		lines = []
		for line in fp:
			lines.append(line.split())

		udp_data = []
		for info in lines[1:]:
			local_addr = info[1][:8]
			rem_addr = info[2][:8]
			user_id = info[7]
			inode = info[9]
			local_port = int(info[1][9:], 16)
			rem_port = int(info[2][9:], 16)

			temp = []

			#convert addr hex to ip
			local_address =  socket.inet_ntoa(struct.pack("<L", int(local_addr, 16)))
			rem_address =  socket.inet_ntoa(struct.pack("<L", int(rem_addr, 16)))

			temp.append('udp')
			temp.append(local_address)
			temp.append(rem_address)
			temp.append(user_id)
			temp.append(inode)
			temp.append(local_port)
			temp.append(rem_port)

			udp_data.append(temp)


		return udp_data



def get_processes(folder):

	dir_list = None
	try:
		dir_list= os.listdir(folder)
		process_dir = []
		for  dir_name in dir_list:
			try:
				dn = int(dir_name)
				process_dir.append(dir_name)
			except Exception as e:
				pass

		return process_dir
	except Exception as e:
		pass
	return None

def get_inode_numbers_of_process(folder):
	folder__ = folder + "/fd/"

	process_list = get_processes(folder__)

	if process_list == None:
		return None
	inode_numbers = []
	for dir_name in process_list:
		fp = folder__ + dir_name
		inode = get_inode_number(fp)
		if inode not in inode_numbers:
			inode_numbers.append(inode)

	return inode_numbers


def get_inode_number(fp):
	#print fp
	try:
		return os.stat(fp).st_ino
	except Exception as e:
		return None
	


#given folder name and process list return the path to 
# the process_folder within the process_list
def get_process_paths():

	process_list = get_processes(proc_path)
	folder_names = []
	for dir_name in process_list:
		fp = '/proc/'+ dir_name  
		folder_names.append(fp)

	return folder_names


if __name__ == "__main__":
	a = TcpUdp()
	print(a.get_active_tcp_conncetions())
