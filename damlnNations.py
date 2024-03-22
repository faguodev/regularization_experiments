import sys

def read_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def count_domain_sizes(lines):
    nations = set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        for part in parts:
            nations.add(part.strip())
            
    return len(nations)

def adjust_weights_in_mln(input_file, output_file, nations_count):
    rescaling_factors = [nations_count, nations_count, nations_count, nations_count * nations_count, nations_count, nations_count, nations_count, nations_count, nations_count, nations_count]

    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    numeric_lines_indexes = []
    
    for index, line in enumerate(lines):
        if line.strip() and (line[0].isdigit() or line[0] == '-'):
            numeric_lines_indexes.append(index)
    
    if len(numeric_lines_indexes) >= 10:
        last_ten_indexes = numeric_lines_indexes[-10:]
    else:
        last_ten_indexes = []

    for i, index in enumerate(last_ten_indexes):
        parts = lines[index].split()
        if parts:
            try:
                parts[0] = str(float(parts[0]) / rescaling_factors[i])
                lines[index] = ' '.join(parts) + '\n'
            except ValueError:
                pass
    
    with open(output_file, 'w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    target_file = sys.argv[3]
    lines = read_dataset(target_file)
    nations_count = count_domain_sizes(lines)
    adjust_weights_in_mln(input_file, output_file, nations_count)
