import csv
import sys
import os
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

def parse_dir(dirname, model_prefix):
    
    valid_files = {
        "_default.csv": "Unoptimized",
        "_simd.csv": "SIMD Add/Mul",
        "_simple_mac.csv": "Scalar MAC",
        "_mac_simd_hardcoded.csv": "SIMD MAC"
    }
    
    files = os.listdir(os.path.abspath(dirname))
    print(files)
    opt_dict = {}
    for f in files:
        ending = None
        for el in valid_files.keys():
            if f.endswith(el):
                ending = el
        if f.startswith(model_prefix) and ending != None:
            opt_dict[valid_files[ending]] = parse_to_dict(os.path.abspath(dirname) + '/' + f)

    return opt_dict

if __name__ == "__main__":
    
    data = parse_dir(sys.argv[1], sys.argv[2])
    outfile = sys.argv[3]
    print(f"keys: {data['Unoptimized'].keys()} values: {data['Unoptimized'].values()}")
    
    with open(outfile, 'w') as f:
        
        f.write("Optimization,Operation,Duration\n")
        for opt in data.keys():
            
            for k in data[opt].keys():
                f.write(f"{opt},{k},{data[opt][k]}\n")

