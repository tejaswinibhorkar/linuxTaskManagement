from time import sleep
from collections import OrderedDict
import re


class CpuInfo(object):

    def __init__(self):

        self.STAT_FILE = '/proc/stat'
        self.MEM_INFO_FILE = '/proc/meminfo'
        self.INTERVAL = 1
        self.cpu_count = 0

    def readfile(self, path):
        try:
            with open(path, 'r') as disk_file:
                data = disk_file.readlines()
                return data
        except IOError as e:
            print('Error Reading File: {}'.format(e))

    def get_cpu_info(self):
        stat_content = self.readfile(self.STAT_FILE)
        values = OrderedDict()
        for line in stat_content:
            fields = line.split()
            is_cpu = re.findall('^cpu', fields[0])
            is_intr = re.findall('^intr', fields[0])
            is_ctxt = re.findall('^ctxt', fields[0])
            if is_cpu:
                self.cpu_count += 1
                field_values = [fields[1], fields[3], fields[4]]
                values[fields[0]] = field_values
            if is_intr:
                values[fields[0]] = fields[1]
            if is_ctxt:
                values[fields[0]] = fields[1]
        # print(values)
        return values

    def get_mem_info(self):
        mem_content = self.readfile(self.MEM_INFO_FILE)
        values = OrderedDict()
        for line in mem_content:
            fields = line.split()
            is_totalMem = re.findall('^MemTotal', fields[0])
            is_freeMem = re.findall('^MemFree', fields[0])
            if is_totalMem:
                values[fields[0]] = fields[1]
            if is_freeMem:
                values[fields[0]] = fields[1]
        return values

    def calculate_cpu_metrics(self, prev_cpu_values, curr_cpu_values):
        for field in curr_cpu_values:
            if 'cpu' in field:
                # USER TIME
                prev_cpu_user_time = int(prev_cpu_values[field][0])
                cur_cpu_user_time = int(curr_cpu_values[field][0])
                delta_cpu_user_time = (cur_cpu_user_time - prev_cpu_user_time) * 0.01

                # SYSTEM TIME
                prev_cpu_system_time = int(prev_cpu_values[field][1])
                cur_cpu_system_time = int(curr_cpu_values[field][1])
                delta_cpu_system_time = (cur_cpu_system_time - prev_cpu_system_time) * 0.01

                # IDLE TIME
                prev_cpu_idle_time = int(prev_cpu_values[field][2])
                cur_cpu_idle_time = int(curr_cpu_values[field][2])
                delta_cpu_idle_time = (cur_cpu_idle_time - prev_cpu_idle_time) * 0.01

                # CPU UTILIZATION
                total_cpu_used = delta_cpu_user_time + delta_cpu_system_time
                total_cpu_time = total_cpu_used + delta_cpu_idle_time
                overall_cpu_utilization = (total_cpu_used/total_cpu_time) * 100
                user_mode_utilization = (delta_cpu_user_time/total_cpu_time) * 100
                system_mode_utilization = (delta_cpu_system_time/total_cpu_time) * 100
                print("""{} utilization: user_mode = {}%, system_mode = {}%, overall = {}%"""
                      .format(field, user_mode_utilization, system_mode_utilization, overall_cpu_utilization))

            if 'intr' in field:
                prev_intr_count = int(prev_cpu_values[field])
                cur_intr_count = int(curr_cpu_values[field])
                rate_intr_count = (cur_intr_count - prev_intr_count)/self.INTERVAL
                print("Rate for {} = {}".format(field, rate_intr_count))

            if 'ctxt' in field:
                prev_ctxt_count = int(prev_cpu_values[field])
                cur_ctxt_count = int(curr_cpu_values[field])
                rate_ctxt_count = (cur_ctxt_count - prev_ctxt_count)/self.INTERVAL
                print("Rate for {} = {}".format(field, rate_ctxt_count))

    def swap_current_cache(self, curr_cpu_values):
        prev_cpu_values_swap = curr_cpu_values
        return prev_cpu_values_swap

    def calculate_mem_metrics(self, prev_mem, curr_mem):
        avg_mem = {}
        print("prev mem= {}".format(prev_mem))
        print("curr mem = {}".format(curr_mem))
        for field in curr_mem:
            prev_mem_value = int(prev_mem[field])
            print("Prev: {}, {}".format(prev_mem_value,field))
            cur_mem_value = int(curr_mem[field])
            print("curr: {}, {}".format(cur_mem_value,field))
            avg_mem_value = ((prev_mem_value + cur_mem_value)/2) * 0.001
            avg_mem[field] = avg_mem_value

        for memory in avg_mem:
            if 'MemFree' in memory:
                avg_free_mem = avg_mem[memory]
                print("Avg: {}, {}".format(avg_free_mem, memory))

            if 'MemTotal' in memory:
                avg_total_mem = avg_mem[memory]
                print("Avg: {}, {}".format(avg_total_mem, memory))

        total_mem_utilization = ((avg_total_mem - avg_free_mem) / avg_total_mem) * 100
        print("Total memory Utilization = {}%".format(total_mem_utilization))


if __name__ == '__main__':
    cpuObj = CpuInfo()
    prev_cpu_values_ = cpuObj.get_cpu_info()
    prev_mem_values = cpuObj.get_mem_info()

    while True:
        sleep(cpuObj.INTERVAL)
        curr_cpu_values_ = cpuObj.get_cpu_info()
        curr_mem_values = cpuObj.get_mem_info()

        cpuObj.calculate_cpu_metrics(prev_cpu_values_, curr_cpu_values_)
        cpuObj.calculate_mem_metrics(prev_mem_values, curr_mem_values)

        prev_cpu_values_ = cpuObj.swap_current_cache(curr_cpu_values_)
        prev_mem_values = cpuObj.swap_current_cache(curr_mem_values)
