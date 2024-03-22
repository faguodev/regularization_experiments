import sys

def read_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def count_domain_sizes(lines):
    tasks = set()
    courses = set()
    people = set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        if line.startswith("courseTA") or line.startswith("courseProf"):
            courses.add(parts[0].strip())
            people.add(parts[1].strip())
        elif line.startswith("student") or line.startswith("faculty"):
            people.add(parts[0].strip())
        elif line.startswith("project"):
            tasks.add(parts[0].strip())
            people.add(parts[1].strip())

    return len(tasks), len(courses), len(people)

def adjust_weights_in_mln(input_file, output_file, task_count, course_count, people_count):
    rescaling_factors = [course_count*course_count, task_count*course_count, course_count, task_count*task_count, task_count, course_count, course_count]

    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    numeric_lines_indexes = []
    
    for index, line in enumerate(lines):
        if line.strip() and (line[0].isdigit() or line[0] == '-'):
            numeric_lines_indexes.append(index)
    
    if len(numeric_lines_indexes) >= 4:
        last_seven_indexes = numeric_lines_indexes[-7:]
    else:
        last_seven_indexes = []

    
    for i, index in enumerate(last_seven_indexes):
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
    task_count, course_count, people_count = count_domain_sizes(lines)
    adjust_weights_in_mln(input_file, output_file, task_count, course_count, people_count)

