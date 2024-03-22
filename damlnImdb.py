import sys

def read_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def count_domain_sizes(lines):
    persons = set()
    films = set()
    types = set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        if line.startswith("workedUnder"):
            persons.add(parts[0].strip())
            persons.add(parts[1].strip())
        elif line.startswith("movie"):
            films.add(parts[0].strip())
            persons.add(parts[1].strip())
        elif line.startswith("director") or line.startswith("male") or line.startswith("actor"):
            persons.add(parts[0].strip())
        elif line.startswith("genre"):
            persons.add(parts[0].strip())
            types.add(parts[1].strip())

    return len(persons), len(films), len(types)    

def adjust_weights_in_mln(input_file, output_file, person_count, film_count, type_count):
    rescaling_factors = [film_count, person_count, film_count, type_count*person_count]

    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    numeric_lines_indexes = []
    
    for index, line in enumerate(lines):
        if line.strip() and (line[0].isdigit() or line[0] == '-'):
            numeric_lines_indexes.append(index)
    
    if len(numeric_lines_indexes) >= 4:
        last_four_indexes = numeric_lines_indexes[-4:]
    else:
        last_four_indexes = []

    for i, index in enumerate(last_four_indexes):
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
    person_count, film_count, type_count = count_domain_sizes(lines)
    adjust_weights_in_mln(input_file, output_file, person_count, film_count, type_count)
