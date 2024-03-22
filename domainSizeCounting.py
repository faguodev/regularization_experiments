def read_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def count_domain_sizes_and_check_overlap_smoking(lines):
    persons = set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        if line.startswith("Friends"):
            persons.add(parts[0].strip())
            persons.add(parts[1].strip())
        elif line.startswith("Smokes"):
            persons.add(parts[0].strip())
        elif line.startswith("Cancer"):
            persons.add(parts[0].strip())

    # Checking for overlap

    return len(persons)

def get_domains_smoking(lines):
    persons = set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        if line.startswith("Friends"):
            persons.add(parts[0].strip())
            persons.add(parts[1].strip())
        elif line.startswith("Smokes"):
            persons.add(parts[0].strip())
        elif line.startswith("Cancer"):
            persons.add(parts[0].strip())

    return persons

def smoking_counting(dataset_file_path):
    lines = read_dataset(dataset_file_path)
    person_count = count_domain_sizes_and_check_overlap_smoking(lines)

    print(f"Domain sizes:\nPerson: {person_count}")

    # Additional print to indicate if any overlap exists
    if person_count:
        print("There is overlap among the domains.")
    else:
        print("No overlap among the domains.")

def count_domain_sizes_and_check_overlap_imdb(lines):
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

    # Checking for overlaps
    person_film_overlap = persons.intersection(films)
    person_type_overlap = persons.intersection(types)
    film_type_overlap = films.intersection(types)

    return len(persons), len(films), len(types), person_film_overlap, person_type_overlap, film_type_overlap

def get_domains_imdb(lines):
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

    return persons, films, types

def imdb_counting(dataset_file_path):
    lines = read_dataset(dataset_file_path)
    person_count, film_count, type_count, person_film_overlap, person_type_overlap, film_type_overlap = count_domain_sizes_and_check_overlap_imdb(lines)

    print(f"Domain sizes:\nPerson: {person_count}\nFilm: {film_count}\nType: {type_count}")
    print(f"Overlaps:\nPerson-Film: {person_film_overlap}\nPerson-Type: {person_type_overlap}\nFilm-Type: {film_type_overlap}")

    # Additional print to indicate if any overlap exists
    if person_film_overlap or person_type_overlap or film_type_overlap:
        print("There is overlap among the domains.")
    else:
        print("No overlap among the domains.")

def count_domain_sizes_and_check_overlap_webkb(lines):
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

    # Checking for overlaps
    task_course_overlap = tasks.intersection(courses)
    task_person_overlap = tasks.intersection(people)
    course_person_overlap = courses.intersection(people)

    return len(tasks), len(courses), len(people), task_course_overlap, task_person_overlap, course_person_overlap

def get_domains_webkb(lines):
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

    return tasks, courses, people

def webkb_counting(dataset_file_path):
    lines = read_dataset(dataset_file_path)
    task_count, course_count, person_count, task_course_overlap, task_person_overlap, course_person_overlap = count_domain_sizes_and_check_overlap_webkb(lines)

    print(f"Domain sizes:\nTask: {task_count}\nCourse: {course_count}\nPerson: {person_count}")
    print(f"Overlaps:\nTask-Course: {task_course_overlap}\nTask-Person: {task_person_overlap}\nCourse-Person: {course_person_overlap}")

    # Additional print to indicate if any overlap exists
    if task_course_overlap or task_person_overlap or course_person_overlap:
        print("There is overlap among the domains.")
    else:
        print("No overlap among the domains.")

def count_domain_sizes_and_check_overlap_nations(lines):
    nations= set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        for part in parts:
            nations.add(part.strip())

    # Checking for overlap

    return len(nations)

def get_domains_nations(lines):
    nations= set()

    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        for part in parts:
            nations.add(part.strip())

    return nations

def nations_counting(dataset_file_path):
    lines = read_dataset(dataset_file_path)
    nation_count = count_domain_sizes_and_check_overlap_nations(lines)

    print(f"Domain sizes:\nNation: {nation_count}")

    # Additional print to indicate if any overlap exists
    if nation_count:
        print("There is overlap among the domains.")
    else:
        print("No overlap among the domains.")

if __name__ == "__main__":
    # Smoking
    dataset_file_path = './smoking/smoking.all.db'
    smoking_counting(dataset_file_path)

    # IMDB
    dataset_file_path = './imdb/imdb.all.db'
    imdb_counting(dataset_file_path)

    # WebKB
    dataset_file_path = './webkb/webkb.all.db'
    webkb_counting(dataset_file_path)

    # Nations
    dataset_file_path = './nations/nations.all.db'
    nations_counting(dataset_file_path)