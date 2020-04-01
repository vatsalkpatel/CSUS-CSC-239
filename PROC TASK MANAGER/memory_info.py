import time

mem_stat_file = '/proc/meminfo'


class Meminfo():

    def __init__(self):
        collect_initial_data = self.get_stats()
        self.prev_mem_total = collect_initial_data[0]
        self.prev_mem_free = collect_initial_data[1]
        self.prev_mem_avail = collect_initial_data[2]

    def get_stats(self):

        gp = open(mem_stat_file)

        gp.seek(0)
        for line in gp:
            li = line.split()
            if li[0] == "MemTotal:":
                total_memory = int(li[1]) / 1024
            if li[0] == "MemFree:":
                mem_free_prev = int(li[1]) / 1024
            if li[0] == "MemAvailable:":
                mem_avail_prev = int(li[1]) / 1024
        gp.close()
        # print sda_line
        Mem_stats = []

        # total memory
        Mem_stats.append(total_memory)
        # memory free
        Mem_stats.append(mem_free_prev)
        # memory free
        Mem_stats.append(mem_avail_prev)

        # print stats
        return Mem_stats

    def get_mem_info(self):

        current_data = self.get_stats()

        mem_stats_interval = self.calculate_stats(current_data)

        self.prev_mem_free = current_data[1]
        self.prev_mem_avail = current_data[2]

        return mem_stats_interval

    def calculate_stats(self, current_data):

        mem_stats = {}
        mem_stats['avg_mem_total'] = current_data[0]
        mem_stats['avg_mem_available'] = (current_data[2] + self.prev_mem_avail)/2
        # mem_stats['avg_mem_free'] = current_data[1] + self.prev_sectors_read
        mem_stats['mem_utilization'] = (current_data[0] - mem_stats['avg_mem_available']) / current_data[0] * 100
        # average_mem_free = float((mem_free_curr + mem_free_prev) / 2)
        # average_mem_used = float((mem_used_curr + mem_used_prev) / 2)
        # mem_utilization = float((average_mem_used / total_memory) * 100)

        return mem_stats


if __name__ == "__main__":
    a = Meminfo()
    for i in range(5):
        time.sleep(10)
        print(a.get_mem_info())
