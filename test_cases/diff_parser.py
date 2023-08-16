import re


def code_diff_map(diff_file):
    file_map = {}

    with open(diff_file) as f:
        for line in f.readlines():
            if line.startswith('+++'):
                file_path = line.split(' b/')[-1]
                if file_path:
                    current_file = file_path.strip()
                    file_map[current_file] = []

            if line.startswith('@@'):
                pattern = re.compile('\\+(.+) @@')
                res = pattern.findall(line)[0]
                pattern2 = re.compile(',')
                match = pattern2.search(res)
                if match:
                    start = int(res.split(',')[0])
                    end = int(res.split(',')[1])
                else:
                    start = int(res)
                    end = 1
                arr = [num for num in range(start, start+end)]
                file_map[current_file].extend(arr)
        return file_map
