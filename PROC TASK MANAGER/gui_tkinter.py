
import tkinter as tk
from tkinter import *

from matplotlib import style

style.use("ggplot")
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
LARGE_FONT= ("Verdana", 12)
style.use("ggplot")


#importing the cpu_all_cores_stats.py
from cpu_all_cores_stats import cpu_cores_stats

#import the memory info module
from memory_info import Meminfo

#importing the disk stats class
from disk_stats import disk_stats_info

#importing the proc stats class
from proc_stats import get_process_info

#importing the network stats class
from network_stats import TcpUdp

#importing the snmp
from network_snmp_file_stats import SnmpInfo

#import the net dev file
from network_net_dev import NetworkBytes

class linux_task_manager_app(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand = True)
		tk.Tk.wm_title(self, "Task manager")

		

		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		self.frames = {}

		for F in (StartPage, CpuStats, DiskStats, Process_info, NetworkStatstics):

			frame = F(container, self)

			self.frames[F] = frame

			frame.grid(row=0, column=0, sticky="nsew")

		self.geometry("800x500")
		self.show_frame(StartPage)

	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
		if cont == CpuStats or cont == DiskStats or cont == Process_info or cont == NetworkStatstics:
			print("calling the function")
			frame.update_stats()

#this is the first page as app opens

class StartPage(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		#title of the first window
		#self.geometry("500x500")
		print ("StartPage {self}")

		label = tk.Label(self, text = "Start Page")
		label.pack(pady = 10, padx = 10)

		button = tk.Button(self, text = "Cpu stats", command = lambda: controller.show_frame(CpuStats))
		button.pack()

		button2 = tk.Button(self, text="Disk stats", command=lambda: controller.show_frame(DiskStats))
		button2.pack()

		button2 = tk.Button(self, text="Network stats", command=lambda: controller.show_frame(NetworkStatstics))
		button2.pack()

		button2 = tk.Button(self, text="Process_info", command=lambda: controller.show_frame(Process_info))
		button2.pack()

		# button3 = tk.Button(self, text = "visit page 3")
		# button3.pack()


class CpuStats(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		print ("CpuStats {self}")
		label = tk.Label(self, text="CPU STATS overall utilization graph")
		label.pack(pady=10,padx=10)

		button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
		#button1.grid(row = 0, column = 1)
		button1.pack()


		#attempt to add graph
		self.f = Figure(figsize=(1,1), dpi=100)
		self.a = self.f.add_subplot(111)
		self.f.subplots_adjust(left=0.15,bottom=0.18,right=0.87,top=0.86)
		self.a.set_xlabel('Timeline',fontsize = 12)
		self.a.set_ylabel('Cpu Utilization percentage',fontsize = 12)
		canvas = FigureCanvasTkAgg(self.f, self)
		canvas.draw()
		canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

		toolbar = NavigationToolbar2Tk(canvas, self)
		toolbar.update()

		self.y_axis = [10,10,10,10,10,10,10,10,10,10]
		self.x_axis = [1,2,3,4,5,6,7,8,9,10]
		#self.a.plot(self.x_axis, self.y_axis)


		canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


		self.listbox = tk.Listbox(self,height=3)
		self.listbox.insert(0, "CPU     user    system   overall      intr     cntxt    memutil   totalmem    avalmem")
		self.listbox.itemconfig(0, {'bg':'yellow'})
		self.listbox.insert(1, "vatsal")
		self.listbox.pack(side = BOTTOM, fill = BOTH)

		self.line1, = self.a.plot(self.x_axis, self.y_axis, 'b-')

		self.time = 0
		self.count = 0
		self.timer = 10

		#initializing the class all_core_stats
		self.cpu_stats = cpu_cores_stats()

		#innitoializing the meminfo class
		self.mem_stats = Meminfo()


	def clear_listbox(self):
		self.listbox.delete(1, END)

	def fill_listbox(self, cpu_stats):
		count = 1
		for data in cpu_stats:
			self.listbox.insert(count, data)
			count += 1


	def update_stats(self):
		cpu_stats = self.get_cpu_label_box_output_val()
		self.clear_listbox()
		self.fill_listbox(cpu_stats)
		self.timer = self.timer + 1
		self.listbox.after(self.time + 1000, self.update_stats)


	def get_cpu_label_box_output_val(self):
		cpu_data = self.get_cpu_mem_stats()


		#plotting and updating data
		new_data = cpu_data[0][2]*100
		self.y_axis.pop(0)
		self.y_axis.append(new_data)
		self.line1.set_ydata(self.y_axis)
		self.x_axis.pop(0)
		self.x_axis.append(self.timer)
		self.line1.set_ydata(self.x_axis)
		self.f.canvas.draw()
		self.a.clear()
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		self.a.set_ylim([0,110])
		self.a.set_xlabel('Timeline',fontsize = 12)
		self.a.set_ylabel('Cpu Utilization percentage',fontsize = 12)
		self.a.plot(self.x_axis, self.y_axis)


		cpu =  "cpu " + "    "  +"%.2f" % (cpu_data[0][0]*100) + "    "  \
				+ "%.2f" % (cpu_data[0][1]*100) +  "    " + "%.2f" % (cpu_data[0][2]*100) +  "          " \
				+ "%d" % cpu_data[0][3] + "    " +  "%d" % cpu_data[0][4] + "    "\
				+ "%.2f" % cpu_data[1] + "     " +"%.2f" % cpu_data[2] + "      " +"%.2f" % cpu_data[3]

		return [cpu]

		

	def get_cpu_mem_stats(self):
		cpu_data = self.cpu_stats.cpu_interval_data() 
		mem_data = self.mem_stats.get_mem_info()
		#print cpu_data
		cpu = cpu_data['cpu']
		
		cpu.append(cpu_data['intr'])
		cpu.append(cpu_data['ctxt'])

		#print mem_data
		avg_mem_available = mem_data['avg_mem_available']
		avg_mem_total = mem_data['avg_mem_total']
		mem_utilization = mem_data['mem_utilization']


		return [cpu, mem_utilization, avg_mem_total, avg_mem_available]


class DiskStats(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Disk stats")
		label.pack(pady=10,padx=10)
		print ("DiskStats {self}")
		button1 = tk.Button(self, text="Back to Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()

		#attempt to add graph
		self.f = Figure(figsize=(4,4), dpi=100)
		self.ax1=self.f.add_subplot(221)
		self.ax2 = self.f.add_subplot(222)
		self.ax3 = self.f.add_subplot(223)
		self.ax4 = self.f.add_subplot(224)
		canvas = FigureCanvasTkAgg(self.f, self)
		canvas.draw()
		canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		toolbar = NavigationToolbar2Tk(canvas, self)
		toolbar.update()
		self.y_axis1 = [0, 0, 0, 0]
		self.x_axis1 = [1, 2, 3, 4]
		self.y_axis2 = [0, 0, 0, 0]
		self.x_axis2 = [1, 2, 3, 4]
		self.y_axis3 = [0, 0, 0, 0]
		self.x_axis3 = [1, 2, 3, 4]
		self.y_axis4 = [0, 0, 0, 0]
		self.x_axis4 = [1, 2, 3, 4]
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


		self.listbox = tk.Listbox(self,height=3)
		self.listbox.insert(0, "disk_r     disksecread    disk_w     disksecwritten")
		self.listbox.itemconfig(0, {'bg':'yellow'})
		self.listbox.pack(side = BOTTOM, fill = BOTH)


		#initialize the diskinfo class
		self.disk_stats = disk_stats_info()

		self.line1, = self.ax1.plot(self.x_axis1, self.y_axis1, 'b-')
		self.line2, = self.ax2.plot(self.x_axis2, self.y_axis2, 'b-')
		self.line3, = self.ax3.plot(self.x_axis3, self.y_axis3, 'b-')
		self.line4, = self.ax4.plot(self.x_axis4, self.y_axis4, 'b-')
		self.f.legend([self.line1,self.line2,self.line3,self.line4],["disk reads","disk sector read","disk write","disk sector write"])

		#self time 
		self.time = 0

		#just a test val
		self.count = 0

		#set timer for x axis
		self.timer = 4

	def clear_listbox(self):
		self.listbox.delete(1, END)


	def fill_listbox(self, disk_stats):
		self.listbox.insert(1, disk_stats)
			

	def update_stats(self):
		disk_stats = self.get_disk_labelbox_input()
		self.clear_listbox()
		self.fill_listbox(disk_stats)
		self.timer = self.timer+4
		self.listbox.after(self.time + 4000, self.update_stats)


	def get_disk_labelbox_input(self):
		disk_stats = self.get_disk_stats()
		disk_reads = str(disk_stats['disk_reads_interval'])
		disk_sectors_read = str(disk_stats['disk_sectors_read_interval'])
		disk_writes = str(disk_stats['disk_writes_interval'])
		disk_sectors_written = str(disk_stats['disk_sectors_written_interval'])

		# plotting and updating data
		self.y_axis1.pop(0)
		self.y_axis1.append(int(disk_reads))
		self.line1.set_ydata(self.y_axis1)
		self.x_axis1.pop(0)
		self.x_axis1.append(self.timer)
		self.line1.set_ydata(self.x_axis1)
		self.f.canvas.draw()
		#self.ax1.clear()
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		self.ax1.plot(self.x_axis2, self.y_axis2)

		self.y_axis2.pop(0)
		self.y_axis2.append(int(disk_sectors_read))
		self.line2.set_ydata(self.y_axis2)
		self.x_axis2.pop(0)
		self.x_axis2.append(self.timer)
		self.line2.set_ydata(self.x_axis2)
		self.f.canvas.draw()
		#self.ax2.clear()
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		self.ax2.plot(self.x_axis2, self.y_axis2)

		self.y_axis3.pop(0)
		self.y_axis3.append(int(disk_writes))
		self.line3.set_ydata(self.y_axis3)
		self.x_axis3.pop(0)
		self.x_axis3.append(self.timer)
		self.line3.set_ydata(self.x_axis3)
		self.f.canvas.draw()
		#self.ax2.clear()
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		self.ax3.plot(self.x_axis3, self.y_axis3)

		self.y_axis4.pop(0)
		self.y_axis4.append(int(disk_sectors_written))
		self.line4.set_ydata(self.y_axis4)
		self.x_axis4.pop(0)
		self.x_axis4.append(self.timer)
		self.line4.set_ydata(self.x_axis4)
		self.f.canvas.draw()
		#self.ax4.clear()
		self.f.subplots_adjust(left=0.15, bottom=0.18, right=0.87, top=0.86)
		self.ax4.plot(self.x_axis4, self.y_axis4)
		self.f.legend([self.line1,self.line2,self.line3,self.line4],["disk reads","disk sector read","disk write","disk sector write"])



		label_output = disk_reads + "            "	+ disk_sectors_read + "            " + disk_writes + "            "	 + disk_sectors_written
		return label_output	

	def get_disk_stats(self):
		disk_stats = self.disk_stats.get_disk_info()
		#print disk_stats
		return disk_stats

class NetworkStatstics(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Network stats")
		label.pack(pady=10,padx=10)
		print ("NetworkStats {self}")
		button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
		
		button1.pack()

		w = Label(self , text="Filter connections")
		w.pack()

		self.entry_box = Entry(self , width=10)
		self.entry_box.pack()

		self.listbox_ip = tk.Listbox(self, height=2)
		self.listbox_ip.insert(0, " Forwarding   Inrecieves  Outrequests")
		self.listbox_ip.itemconfig(0, {'bg':'yellow'})

		self.listbox_tcp = tk.Listbox(self, height=2)
		self.listbox_tcp.insert(0, "Active_open    Current_establishment    Inseg     Outseg")
		self.listbox_tcp.itemconfig(0, {'bg':'yellow'})

		self.listbox_udp = tk.Listbox(self, height=2)
		self.listbox_udp.insert(0, "Indatagram   Outdatagram")
		self.listbox_udp.itemconfig(0, {'bg':'yellow'})

		self.listbox_bytes = tk.Listbox(self, height=2)
		self.listbox_bytes.insert(0, "recieved_bytes    transmitted_bytes")
		self.listbox_bytes.itemconfig(0, {'bg':'yellow'})

		self.listbox = tk.Listbox(self, height=15)
		self.listbox.insert(0, "program_name       source_address    local_port    destination_address   remote_port     username       protocol       inode")
		self.listbox.itemconfig(0, {'bg':'yellow'})



		self.listbox.pack(side = BOTTOM, fill = BOTH)
		self.listbox_ip.pack(side = TOP, fill = 	BOTH)
		self.listbox_tcp.pack(side = TOP, fill = 	BOTH)
		self.listbox_udp.pack(side = TOP, fill = 	BOTH)
		self.listbox_bytes.pack(side = TOP, fill = 	BOTH)
		#intializing the network stats
		self.net_stats = TcpUdp()

		#snmp file data ip tcp udp
		self.snmp_data = SnmpInfo()


		#transmitted bytes
		self.trasn_rec = NetworkBytes()

		self.time = 0
		
		#print "network class initiated"


	def set_filter_box_val(self, network_stats):
		filter_val = self.entry_box.get()
		

		filter_stats = []
		if filter_val != '':
			for conn in network_stats:
				if filter_val in conn:
					filter_stats.append(conn)
		else:
			return network_stats

		return filter_stats


	def clear_listbox(self):
		self.listbox.delete(1, END)
		self.listbox_ip.delete(1, END)
		self.listbox_tcp.delete(1, END)
		self.listbox_udp.delete(1, END)
		self.listbox_bytes.delete(1, END)


	def fill_listbox(self, network_stat, ip_data, tcp_data, udp_data, net_utilization_data):
		count = 1
		for data in network_stat:
			self.listbox.insert(count, data)
			count += 1

		self.listbox_ip.insert(1, ip_data)
		self.listbox_tcp.insert(1, tcp_data)
		self.listbox_udp.insert(1, udp_data)

		self.listbox_bytes.insert(1, net_utilization_data)
			
	def update_stats(self):

		#network stats
		network_stat = self.get_network_labelbox_input()
		filter_stats = self.set_filter_box_val(network_stat)
		
		# ip tcp udp data
		ip_tcp_udp_stats = self.get_ip_tcp_udp_stats()
		ip_data = ip_tcp_udp_stats[0]
		tcp_data = ip_tcp_udp_stats[1]
		udp_data = ip_tcp_udp_stats[2]

		net_utilization_data = self.get_rec_transmit_bytes()

		self.clear_listbox()
		self.fill_listbox(filter_stats, ip_data, tcp_data, udp_data, net_utilization_data)
		self.listbox.after(self.time + 1000, self.update_stats)

	def get_rec_transmit_bytes(self):

		data = self.trasn_rec.get_interval_stats()

		net_uti_data = str(data[0]) + "                     " + str(data[1])

		return net_uti_data

	def get_ip_tcp_udp_stats(self):

		data = self.snmp_data.get_interval_stats()

		
		ip_tcp_udp_stats = []

		ip_data = str(data[0][0]) + "                     " + str(data[0][1]) + "                      " + str(data[0][2])

		tcp_data = str(data[1][0]) + "                           " + str(data[1][1]) + "                             " + str(data[1][2]) + "                   " + str(data[1][3])

		udp_data = str(data[2][0]) + "                        " + str(data[1][1]) 

		ip_tcp_udp_stats.append(ip_data)
		ip_tcp_udp_stats.append(tcp_data)
		ip_tcp_udp_stats.append(udp_data)

		return ip_tcp_udp_stats


	def get_network_labelbox_input(self):
		tcp_udp_con = self.net_stats.get_active_tcp_conncetions()

		label_box_output = []
		for conn in tcp_udp_con:
			label_box_output.append(self.process_input(conn))

		#print label_box_output
		return label_box_output

	def process_input(self, conn):
		program_name = conn[1][0]

		protocol = conn[0][0]

		source_address = conn[0][1]
		destination_address = conn[0][2]
		username = conn[0][3]
		inode = conn[0][4]
		local_port = conn[0][5]
		remote_port = conn[0][6]
 
		label_input = str(program_name)  + "           " + str(source_address) + "         "+ str(local_port)  +"          " + str(destination_address) + "            "+  str(remote_port) +"              " + str(username)  + "            " + str(protocol) + "           "+  str(inode)

		return label_input 


class Process_info(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text="Process_info")
		label.pack(pady=10,padx=10)

		button1 = tk.Button(self, text="Back to Home",
							command=lambda: controller.show_frame(StartPage))
		button1.pack()

		w = Label(self , text="Filter process")
		w.pack()

		self.entry_box = Entry(self , width=10)
		self.entry_box.pack()


		self.listbox = tk.Listbox(self , height=25)
		self.listbox.insert(0, "procid          procname       username       virtual_mem_total         res_mem_total        usr_utilization      sys_utilization      overall_utilization")
		self.listbox.itemconfig(0, {'bg':'yellow'})
		self.listbox.pack(side = BOTTOM, fill = BOTH)


		self.time = 0

		#initialize the process class 
		self.process_info = get_process_info()



	def set_filter_box_val(self, process_stats):
		filter_val = self.entry_box.get()
		

		filter_stats = []
		if filter_val != '':
			for process in process_stats:
				if filter_val in process:
					filter_stats.append(process)
		else:
			return process_stats

		return filter_stats


	def clear_listbox(self):
		self.listbox.delete(1, END)


	def fill_listbox(self, proc_info):
		count = 1
		for data in proc_info:
			self.listbox.insert(count, data)
			count += 1


	def update_stats(self):
		process_stats = self.get_process_label_box_input()
		filter_stats = self.set_filter_box_val(process_stats)
		#print(filter_stats)
		self.clear_listbox()
		self.fill_listbox(filter_stats)
		self.listbox.after(self.time + 1000, self.update_stats)


	def get_process_label_box_input(self):
		process_stats = self.process_info.get_processes_stats_interval()

		label_box_output = []
		for process in process_stats:
			stat_row = str(process[0]) + "        " +  str(process[1])  + "          " + str(process[2])  + "        " + str(process[3])  + "        " +  str(process[4])  + "          " +  "%.2f"%process[5] + "         " + "%.2f"%process[6] + "        " + "%.2f"%process[7] 
			label_box_output.append(stat_row)

		return label_box_output  



app = linux_task_manager_app()

app.mainloop()






