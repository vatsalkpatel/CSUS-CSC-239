import time

net_dev_filepath = "/proc/net/dev"

class NetworkBytes():

	def __init__(self, ):

		self.prev_stats = self.get_curr_stats()


	def get_interval_stats(self):

		curr_stats = self.get_curr_stats()

		interval_stats = self.cal_interval_data(curr_stats)

		self.prev_stats = curr_stats

		return interval_stats

	def cal_interval_data(self, curr_stats):

		interval_data = []
		total_bytes_recieved = curr_stats[0] - self.prev_stats[0]
		total_bytes_transmitted = curr_stats[1] - self.prev_stats[1]

		interval_data.append(total_bytes_recieved)
		interval_data.append(total_bytes_transmitted)

		return interval_data



	def get_curr_stats(self):

		f = open(net_dev_filepath)

		lines = []
		for line in f:
			lines.append(line.split())

		stats = []
		total_bytes_recieved = int(lines[2][1]) + int(lines[3][1])
		total_bytes_transmitted = int(lines[2][9]) + int(lines[3][9])
		stats.append(total_bytes_recieved)
		stats.append(total_bytes_transmitted)

		return stats



if __name__ == '__main__':
	a = NetworkBytes()
	for i in range(5):
		time.sleep(3)
		print (a.get_interval_stats())


