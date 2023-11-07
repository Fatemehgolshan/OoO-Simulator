'''
Pipeline component with a specified latency and input buffer
'''


class PComponent:
    def __init__(self, name, latency, input_buffer_size):
        self.name = name
        self.latency = latency
        self.input_buffer_size = input_buffer_size
        self.available_cycles = [0] * input_buffer_size
        self.total_input_reqs = 0
        self.total_wait_cycles = 0


    def get_name(self):
        return self.name


    def get_latency(self):
        return self.latency


    def get_size(self):
        return self.input_buffer_size


    def allocate(self, curr_cycle):
        '''
        This function allocates an entry in the reservation station, and
        returns the cycle at which the operation is DONE
        '''

        self.total_input_reqs += 1
        min_available_cycle = min(self.available_cycles)
        min_available_idx = self.available_cycles.index(min_available_cycle)

        if curr_cycle >= min_available_cycle:
            # it's available, use it after waiting for its latency!
            self.available_cycles[min_available_idx] = curr_cycle + self.latency # set the availability for next users
            return curr_cycle + self.latency

        # it's not available, wait until it gets ready, then wait for the lantecy
        wait_time = min_available_cycle - curr_cycle
        self.total_wait_cycles += wait_time
        self.available_cycles[min_available_idx] += self.latency
        return min_available_cycle + self.latency


    def get_wait_cycles(self, curr_cycle):
        min_available_cycle = min(self.available_cycles)
        return max(min_available_cycle - curr_cycle, 0)


    def allocate_timed(self, curr_cycle, lat):
        # return the wait time
        min_available_cycle = min(self.available_cycles)
        min_available_idx = self.available_cycles.index(min_available_cycle)
        self.available_cycles[min_available_idx] = max(min_available_cycle, curr_cycle) + lat



    def __repr__(self):
        return f'name:{self.name}, latency:{self.latency}, input_buffer_size:{self.input_buffer_size}, available_cycles:{self.available_cycles}, total_input_reqs:{self.total_input_reqs}, total_wait_cycles:{self.total_wait_cycles}'
