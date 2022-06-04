import csv
import sys
from collections import defaultdict

def parse_to_dict(fname):
    
    d = defaultdict(lambda: 0)
    with open(fname) as f:
        
        csv_reader = csv.reader(f, delimiter=",")
        csv_reader.__next__()
        for row in csv_reader:
            # print(row)
            d[row[1]] += int(row[2])
    
    return d


if __name__ == "__main__":

    unoptimized_data = parse_to_dict(sys.argv[1])
    optimized_data = parse_to_dict(sys.argv[2])
    
    print(f"Unoptimized:\n \
            ------------\n \
            Total Cycles: {sum(unoptimized_data.values())}")
    for k in unoptimized_data.keys():
        print(f"{k}: {unoptimized_data[k]}\n")

    print(f"Optimized:\n \
        ------------\n \
        Total Cycles: {sum(optimized_data.values())}")
    for k in optimized_data.keys():
        print(f"{k}: {optimized_data[k]}\n")

    print(f"Gain:\n \
        ------------\n \
            Total Gain: {sum(unoptimized_data.values()) / sum(optimized_data.values())}")
    for k in optimized_data.keys():
        print(f"{k}: {unoptimized_data[k] - optimized_data[k]}\n")

    # for filename in sys.argv[1:]:
    #     with open(filename) as f:
            
    #         csv_reader = csv.reader(f, delimiter=",")
    #         csv_reader.__next__()
    #         for row in csv_reader:
    #             unoptimized_data[row[1]] += row[[2]]
    