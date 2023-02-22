import sys
import random
import  numpy as np

random.seed(1337)
class IP_durations:
    def __init__ (self):
        self.byAS = {}

    def add_duration(self, duration):
        if duration.AS not in self.byAS:
            self.byAS[duration.AS] = []
        self.byAS[duration.AS].append(duration)

    def get_AS_durations(self, AS, start=0, end=sys.maxsize):
        durations = []
        for dur in self.byAS[AS]:
            if dur.active_between(start, end):
                durations.append(dur.length())
        return durations

class Duration:
    def __init__(self, first_seen, last_seen, AS):
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.AS = AS
    
    def length(self):
        return self.last_seen-self.first_seen

    def active_between(self, start, end):
        if self.first_seen <= end and self.last_seen > start:
            return True
        else:
            return False

def CARDCount(IP_durations, AS, IPs, window_start, window_end):
    durations = IP_durations.get_AS_durations(AS, window_start, window_end)
    window_size = window_end-window_start
    observed_durations = []
    for dur in durations:
        dur = (dur*window_size)/(dur+window_size)
        observed_durations.append(dur)
    observed_durations = sorted(observed_durations)

    means = []
    for i in range(1000):
        sum = 0
        for j in range(IPs):
            rnd = random.randint(0, len(observed_durations)-1)  
            sum += observed_durations[rnd]
        means.append(sum/(IPs))
    means = sorted(means)

    mean = np.mean(means)
    lower=means[25]
    upper= means[975]

    total_duration = mean*IPs
    num_hosts = total_duration/window_size

    total_duration = lower*IPs
    lower_bound = total_duration/window_size

    total_duration = upper*IPs
    upper_bound = total_duration/window_size

    return num_hosts, lower_bound, upper_bound, observed_durations

def load_duration_distributions(filepath):
    durations = IP_durations()

    with open(filepath) as file: 
        for line in file:
            vals = line.strip("\n").split(",")
            AS = int(vals[0])
            first_seen = int(vals[1])
            last_seen = int(vals[2])

            dur = Duration(first_seen, last_seen, AS)
            durations.add_duration(dur)
    return durations


IP_durations = load_duration_distributions("./atlas_durations_2018.csv")

print(CARDCount(IP_durations, 3320, 7, 1514761200, 1514761200+7*24*60*60)[0])