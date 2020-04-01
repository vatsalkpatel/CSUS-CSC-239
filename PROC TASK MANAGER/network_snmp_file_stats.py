import time
snmp_file_path = "/proc/net/snmp"

class SnmpInfo():

	def __init__(self):

		self.prev_stats = self.get_curr_snmp_stats()



	def get_interval_stats(self):

		curr_stats = self.get_curr_snmp_stats()

		interval_stats  = self.cal_intreval_data(curr_stats)

		self.prev_stats = curr_stats

		return interval_stats

	def cal_intreval_data(self, curr_stats):

		ip_interval_data = []
		#ipinfo
		ip_forwarding  = curr_stats[0][0] - self.prev_stats[0][0]
		ip_inrecieves = curr_stats[0][1] - self.prev_stats[0][1]
		ip_outrequests = curr_stats[0][2] - self.prev_stats[0][2]

		ip_interval_data.append(ip_forwarding)
		ip_interval_data.append(ip_inrecieves)
		ip_interval_data.append(ip_outrequests)

		tcp_interval_data = []
		#tcp_info
		tcp_acticve_open = curr_stats[1][0] - self.prev_stats[1][0]
		tcp_current_estab = curr_stats[1][1] 
		tcp_inseg = curr_stats[1][2] - self.prev_stats[1][2]
		tcp_outseg = curr_stats[1][3] - self.prev_stats[1][3]

		tcp_interval_data.append(tcp_acticve_open)
		tcp_interval_data.append(tcp_current_estab)
		tcp_interval_data.append(tcp_inseg)
		tcp_interval_data.append(tcp_outseg)

		udp_interval_data = []
		#udp info
		udp_indatagram  = curr_stats[2][0] - self.prev_stats[2][0]
		udp_outdatagram = curr_stats[2][1] - self.prev_stats[2][1]

		udp_interval_data.append(udp_indatagram)
		udp_interval_data.append(udp_outdatagram)


		all_stats_interval = []
		all_stats_interval.append(ip_interval_data)
		all_stats_interval.append(tcp_interval_data)
		all_stats_interval.append(udp_interval_data)

		return all_stats_interval

	
	def get_curr_snmp_stats(self):

		f = open(snmp_file_path)

		lines = []
		for line in f:
			lines.append(line.split())

		#print lines

		ipinfo = []
		#ipinfo 
		ip_forwarding = int(lines[1][1])
		ip_inrecieves = int(lines[1][3])
		ip_outrequests = int(lines[1][10])

		ipinfo.append(ip_forwarding)
		ipinfo.append(ip_inrecieves)
		ipinfo.append(ip_outrequests)

		tcpinfo = []
		#tcpinfo
		tcp_acticve_open = int(lines[7][5])
		tcp_current_estab = int(lines[7][9])
		tcp_inseg  = int(lines[7][10])
		tcp_outseg = int(lines[7][11])

		tcpinfo.append(tcp_acticve_open)
		tcpinfo.append(tcp_current_estab)
		tcpinfo.append(tcp_inseg)
		tcpinfo.append(tcp_outseg)

		udpinfo = []
		#udpinfo
		udp_indatagram = int(lines[9][1])
		udp_outdatagram = int(lines[9][4])

		udpinfo.append(udp_indatagram)
		udpinfo.append(udp_outdatagram)

		all_stats = []

		all_stats.append(ipinfo)
		all_stats.append(tcpinfo)
		all_stats.append(udpinfo)
		

		return all_stats


if __name__ == '__main__':
	a = SnmpInfo()
	for i in range(10):
		time.sleep(5)
		print (a.get_interval_stats())


