import sys
import random
import  numpy as np

random.seed(1337)

class IP_durations:
    """Class to store IP durations indexed by AS"""

    def __init__ (self):
        self.byAS = {}

    def add_duration(self, duration):
        """Add a duration object"""
        if duration.AS not in self.byAS:
            self.byAS[duration.AS] = []
        self.byAS[duration.AS].append(duration)

    def get_AS_durations(self, AS, start=0, end=sys.maxsize):
        """Get all durations stored for the specified AS
        
        returns list of durations in millis

        Keyword arguments:
        start -- include only durations active after provided time in millis
        end   -- include only durations active before provided time in millis
        """
        durations = []
        for dur in self.byAS[AS]:
            if dur.active_between(start, end):
                durations.append(dur.length())
        return durations

class Duration:
    """Duration object 
    
    A duration is defined by its start and end in millis
    AS specifies the autonomous system    
    """
    def __init__(self, first_seen, last_seen, AS):
        """Specify a new duration by its first time seen, last time seen and AS
        
        first_seen -- int specifying time in millis
        last_seen -- int specifying time in millis
        """
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.AS = AS
    
    def length(self):
        """Return length of the duration in millis"""
        return self.last_seen-self.first_seen

    def active_between(self, start, end):
        """Check if a duration was active between a given start and end point"""
        if self.first_seen <= end and self.last_seen > start:
            return True
        else:
            return False

def CARDCount(IP_durations, AS, IPs, window_start, window_end):
    """Compute CARDCount 
    
    IP_durations -- IP_duration object containing the "grund truth" distributions
    AS -- Autononmous system for which the IPs were recorded
    IPs -- int specifying the number of unique IP addresses
    window_start -- time in millis specifying the start of the measurement period
    window_end -- time in millis specifying the end of the measurement period

    returns:
    num_hosts -- estimated number of hosts
    lower_bound -- lower bound based on 95th percentile
    upper_bound -- upper bound based on 95th percentile
    """
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

    return num_hosts, lower_bound, upper_bound

def load_duration_distributions(filepath):
    """Loads IP duration information from a csv file
    
    File format should be 
    AS, int, int

    return:
    IP_duration object
    """
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


# Example usage based on RIPE Atlas durations of 2018 and AS3320 Deutsche Telekom AG
IP_durations = load_duration_distributions("./atlas_durations_2018.csv")
print(CARDCount(IP_durations, 3320, 7, 1514761200, 1514761200+7*24*60*60)[0])
