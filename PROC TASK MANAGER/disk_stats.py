import time


disk_stats_file = '/proc/diskstats'
main_device = 'sda'

class disk_stats_info():

	def __init__(self):
		collect_initial_data = self.get_stats()
		self.prev_reads_completed = collect_initial_data[0]
		self.prev_writes_completed = collect_initial_data[2]
		self.prev_sectors_read = collect_initial_data[1]
		self.prev_sectors_written = collect_initial_data[3]

	def get_stats(self):

		fp = open(disk_stats_file)

		sda_line = None
		for line in fp:
			if line.split()[2] == main_device:
				sda_line = line.split()
				break
		#print sda_line
		stats = []

		#reads completed 
		stats.append(int(sda_line[3]))
		#sectores read
		stats.append(int(sda_line[5]))
		#writes completed
		stats.append(int(sda_line[7]))
		#sectors written
		stats.append(int(sda_line[9]))
		
		#print stats
		return stats

	def get_disk_info(self):

		current_data = self.get_stats()

		stats_interval = self.calculate_stats(current_data)

		self.prev_reads_completed = current_data[0]
		self.prev_sectors_read = current_data[1]
		self.prev_writes_completed = current_data[2]
		self.prev_sectors_written = current_data[3]

		return stats_interval

	def calculate_stats(self, current_data):

		stats = {}
		stats['disk_reads_interval'] = current_data[0] - self.prev_reads_completed
		stats['disk_sectors_read_interval'] = current_data[1] - self.prev_sectors_read
		stats['disk_writes_interval'] = current_data[2] - self.prev_writes_completed
		stats['disk_sectors_written_interval'] = current_data[3] - self.prev_sectors_written

		return stats
 


if __name__ == "__main__":
	a = disk_stats_info()
	for i in range(5):
		time.sleep(10)
		print (a.get_disk_info())











