import time

#read proc file extract relevant information regarding cpu

# file for stat cpu collection
cpu_usage_file = "/proc/stat"
main_cpu = 0
interrupt = 0



#indexes for cpu vals
user       = 1
nice       = 2
system     = 3
idle       = 4
iowait     = 5
irq        = 6
softirq    = 7
steal      = 8
guest      = 9
guest_nice = 10


class cpu_utilization_stats():


	def __init__(self):
		self.prev_val_user = 0
		self.prev_val_system = 0
		self.prev_val_idle = 0
		self.prev_interupts = 0
		self.prev_context_switches = 0
	
	def cpu_utilization(self):
		fp = open(cpu_usage_file)
		lines = []
		for line in fp:
			#print line
			lines.append(line.split())

		stats = self.cpu_utilization_info_extract(lines)
		fp.close()
		return stats


	#array positions of cpu in columns


	def cpu_utilization_info_extract(self ,lines):
		main_cpu_no = main_cpu
		stats = {}

		#calculate no of cpu's
		
	
		stats["user"] = int(lines[main_cpu_no][user]) 
		stats["system"] = int(lines[main_cpu_no][system]) 
		stats["idle"] = int(lines[main_cpu_no][idle]) 

		return stats

	def get_cpu_data_by_interval(self ,interval):


		#cpu stat stuff	
		stats = self.cpu_utilization()
		self.prev_val_user = stats["user"]
		self.prev_val_system = stats["system"]
		self.prev_val_idle = stats["idle"]
		per_interval_user_time = 0
		per_interval_system_time = 0
		per_interval_idle_time = 0
		#print self.prev_val_user, "  ", self.prev_val_idle, " ", self.prev_val_system

		#interval
		time.sleep(interval)
		
		#after interval data
		current_stats = self.cpu_utilization()
		#print current_stats
		per_interval_idle_time = current_stats["idle"] - self.prev_val_idle
		per_interval_system_time = current_stats["system"] - self.prev_val_system
		per_interval_user_time = current_stats["user"] - self.prev_val_user
			

		prev_val_user = current_stats["user"]
		prev_val_system = current_stats["system"]
		prev_val_idle = current_stats["idle"]

		#total time for cpu
		total_time = per_interval_user_time + per_interval_system_time + per_interval_idle_time
			
		interval_based_stats = {}
		interval_based_stats["cpu_utilization_user_mode"] = per_interval_user_time / float(total_time)
		interval_based_stats["cpu_utilization_system_mode"] = per_interval_system_time / float(total_time)
		interval_based_stats["cpu_utilization_idle_mode"] =  (per_interval_system_time + per_interval_user_time) / float(total_time)

		return interval_based_stats


stats = cpu_utilization_stats()

for i in range(5):
	print (stats.get_cpu_data_by_interval(2))

