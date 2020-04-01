import time

#stat file
cpu_stat_file = '/proc/stat'

#constants for get_cores() function
cpu_signature = 'cpu'
interupt_signature = 'intr'
context_signature = 'ctxt'
cpu_position = 0

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

class cpu_cores_stats():
	
	def __init__(self):

		#getting the intial value of stat at startup
		fp = open(cpu_stat_file)
		self.cpu_prev_state_stats = self.get_stats(fp)

		self.prev_interupts = self.get_interupts(fp)
		self.prev_contexts = self.get_contexts(fp)
		fp.close()
		#self.prev_contexts = self.get_contexts(fp)
		#self.cpu_current_state_stats = {}
		#print self.cpu_prev_state_stats

	def get_contexts(self, fp):
		fp.seek(0)

		

		for line in fp:
			if line[0:4] == context_signature:
				line = line.split()
				return int(line[1])
		# 		contexts[line[0]] = line[1]

		# return int(contexts)

	def get_interupts(self, fp):
		fp.seek(0)

		for line in fp:
			l = line.split()
			if l[0] == interupt_signature:
				return int(l[1])
		# 		interupts[interupt_signature] = l[1]


		# return int(interupts)

	#returns {cpu: [user_utilization, system_utilization, overall_utilization]}
	def cpu_interval_data(self):

		fp = open(cpu_stat_file)
		cpu_current_state_stats = self.get_stats(fp)

		cpu_interval_stats = self.cpu_utilization_stats(cpu_current_state_stats)

		interupt_interval_stat = {}
		context_interval_stat = {}
		interupt_interval_stat[interupt_signature] = self.get_interupt_interval(fp)
		context_interval_stat[context_signature] = self.get_context_interval(fp)
#		
		fp.close()
		cpu_interval_stats.update(interupt_interval_stat)
		cpu_interval_stats.update(context_interval_stat)

		return cpu_interval_stats

	def get_interupt_interval(self, fp):
		
		current_interupts = self.get_interupts(fp)
		interval_interupts = current_interupts - self.prev_interupts

		self.prev_interupts = current_interupts
		return interval_interupts

	def get_context_interval(self, fp):

		current_contexts = self.get_contexts(fp)
		interval_contexts = current_contexts - self.prev_contexts
		self.prev_contexts = current_contexts

		return interval_contexts


	#returns {cpu: [user_utilization, system_utilization, overall_utilization]}
	def cpu_utilization_stats(self, cpu_current_state_stats):

		interval_data = {}

		for core in cpu_current_state_stats:
			prev_core_data = self.cpu_prev_state_stats.get(core)
			if prev_core_data != None:
				interval_data[core] = []

				#calculating intervals
				user_interval = int(cpu_current_state_stats[core][0]) - int(self.cpu_prev_state_stats[core][0])
				system_interval = int(cpu_current_state_stats[core][1]) - int(self.cpu_prev_state_stats[core][1])
				idle_interval = int(cpu_current_state_stats[core][2]) - int(self.cpu_prev_state_stats[core][2])

				#adding interval to the core
				interval_data[core].append(user_interval)
				interval_data[core].append(system_interval)
				interval_data[core].append(idle_interval)	

		cpu_utilization_data = {}

		for core in interval_data:
			cpu_utilization_data[core] = []

			#calculating stats for utilization
			total_time = interval_data[core][0] + interval_data[core][1] + interval_data[core][2]

			user_utilization = interval_data[core][0] / float(total_time)
			system_utilization = interval_data[core][1] / float(total_time)
			overall_utilization = (interval_data[core][0] + interval_data[core][1]) / float(total_time)

			cpu_utilization_data[core].append(user_utilization)
			cpu_utilization_data[core].append(system_utilization)
			cpu_utilization_data[core].append(overall_utilization)

		#update the prev state to current state
		self.cpu_prev_state_stats = cpu_current_state_stats

		return cpu_utilization_data
		#print interval_data
		

	# return format {'cpu': [user, system, idle]}
	def get_stats(self, fp):

		stats = {}
		for line in fp:
			if line[0] == "c":
				line = line.split()
				#print line
				stats[line[0]] = [line[user], line[system], line[idle]]
			else:
				return stats
		
		return stats


if __name__ == "__main__":
	a = cpu_cores_stats()
	for i in range(3):
		time.sleep(2)
		print (a.cpu_interval_data()) 