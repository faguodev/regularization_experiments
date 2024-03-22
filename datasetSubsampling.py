import random
from domainSizeCounting import get_domains_imdb, get_domains_smoking, get_domains_webkb, get_domains_nations

def read_dataset(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def extract_predicates(lines):
    predicates = set()
    for line in lines:
        predicate = line.strip().split('(')[0]
        # Remove negation
        if predicate.startswith('!'):
            predicate = predicate[1:]
        predicates.add(predicate)
    return predicates

def check_predicates(filtered_lines, required_predicates):
    predicates_in_filtered = extract_predicates(filtered_lines)
    is_valid = required_predicates.issubset(predicates_in_filtered)
    return is_valid

def write_filtered_dataset(filtered_lines, output_file_path):
    with open(output_file_path, 'w') as file:
        file.writelines(filtered_lines)

def sample_subset(names, subset_size):
    return set(random.sample(list(names), min(subset_size, len(names))))

#################################
# Smoking Dataset Sampling

def extract_people_smoking(lines):
    names = set()
    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        for name in parts:
            names.add(name.strip())
    return names

def collect_related_entries_smoking(lines, subset_names):
    filtered_lines = []
    for line in lines:
        # Extract names and strip spaces for accurate comparison
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        names_in_line = {name.strip() for name in parts}

        # Check if all names in the line are in the subset_names
        if names_in_line.issubset(subset_names):
            filtered_lines.append(line)
    return filtered_lines

def check_predicates_smoking(filtered_lines):
    predicates_in_filtered = extract_predicates(filtered_lines)
    persons = get_domains_smoking(filtered_lines)
    persons = list(persons)

    extra_lines = []

    if "Friends" not in predicates_in_filtered:
        extra_lines.append(f"!Friends({persons[0]}, {persons[1]})\n")
    if "Smokes" not in predicates_in_filtered:
        extra_lines.append(f"!Smokes({persons[0]})\n")
    if "Cancer" not in predicates_in_filtered:
        extra_lines.append(f"!Cancer({persons[0]})\n")

    return filtered_lines + extra_lines


def smoking_sampling(dataset_file_path, subset_size, folds, target=False):
    required_predicates = {"Friends", "Smokes", "Cancer"}

    lines = read_dataset(dataset_file_path)
    names = extract_people_smoking(lines)

    rejections = 0

    for i in range(1, folds + 1):
        if target:
            output_file_path = f'./smoking/folds/smoking_target_{subset_size}_{i}.db'
        else:
            output_file_path = f'./smoking/folds/filtered_smoking_{i}.db'
        is_valid = False
        while not is_valid:
            subset_names = sample_subset(names, subset_size)
            related_lines = collect_related_entries_smoking(lines, subset_names)
            final_lines = check_predicates_smoking(related_lines)
            is_valid = check_predicates(final_lines, required_predicates)
            if not is_valid:
                rejections += 1
            else:
                write_filtered_dataset(final_lines, output_file_path)

#################################
# IMDB Dataset Sampling

def extract_people_imdb(lines):
    people = set()
    for line in lines:
        if line.startswith("workedUnder") or line.startswith("movie") or line.startswith("director") or line.startswith("male") or line.startswith("actor") or line.startswith("genre"):
            parts = line.strip().split('(')[1].split(')')[0].split(',')
            for part in parts:
                part = part.strip()
                # Assuming the first part is always a person for movie and genre
                if line.startswith("movie"):
                    people.add(parts[1].strip())
                    break
                elif line.startswith("genre"):
                    people.add(parts[0].strip())
                    break
                else:
                    people.add(part)
    return people

def collect_related_entries_imdb(lines, subset_names):
    related_lines = []
    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        parts = [part.strip() for part in parts]
        if "movie" in line and parts[1] in subset_names:
            related_lines.append(line)
        elif "genre" in line and parts[0] in subset_names:
            related_lines.append(line)
        elif set(parts).issubset(subset_names):
            related_lines.append(line)
    return related_lines

def check_predicates_imdb(filtered_lines):
    predicates_in_filtered = extract_predicates(filtered_lines)
    persons, films, types = get_domains_imdb(filtered_lines)
    persons, films, types = list(persons), list(films), list(types)

    extra_lines = []

    if "workedUnder" not in predicates_in_filtered:
        extra_lines.append(f"!workedUnder({persons[0]}, {persons[1]})\n")
    if "movie" not in predicates_in_filtered:
        extra_lines.append(f"!movie({films[0]}, {persons[0]})\n")
    if "director" not in predicates_in_filtered:
        extra_lines.append(f"!director({persons[0]})\n")
    if "male" not in predicates_in_filtered:
        extra_lines.append(f"!male({persons[0]})\n")
    if "actor" not in predicates_in_filtered:
        extra_lines.append(f"!actor({persons[0]})\n")
    if "genre" not in predicates_in_filtered:
        extra_lines.append(f"!genre({persons[0]}, {types[0]})\n")

    return filtered_lines + extra_lines


def imdb_sampling(dataset_file_path, subset_size, folds, target=False):
    required_predicates = {"workedUnder", "movie", "director", "genre", "actor", "male"}
    
    lines = read_dataset(dataset_file_path)
    names = extract_people_imdb(lines)

    rejections = 0
    
    for i in range(1, folds + 1):
        if target:
            output_file_path = f'./imdb/folds/imdb_target_{subset_size}_{i}.db'
        else:
            output_file_path = f'./imdb/folds/filtered_imdb_{i}.db'
        is_valid = False
        while not is_valid:
            subset_names = sample_subset(names, subset_size)
            related_lines = collect_related_entries_imdb(lines, subset_names)
            final_lines = check_predicates_imdb(related_lines)
            is_valid = check_predicates(final_lines, required_predicates)
            if not is_valid:
                rejections += 1
            else:
                write_filtered_dataset(final_lines, output_file_path)

#################################
# WebKB Dataset Sampling

def extract_people_webkb(lines):
    """Extract unique person names from the dataset."""
    people = set()
    for line in lines:
        if line.startswith("project") or line.startswith("courseTA") or line.startswith("courseProf"):
            parts = line.strip().split('(')[1].split(')')[0].split(',')
            # Add the person to the set
            people.add(parts[1].strip())
        elif line.startswith("student") or line.startswith("faculty"):
            parts = line.strip().split('(')[1].split(')')[0].split(',')
            # Add the person to the set
            people.add(parts[0].strip())
    return people

def collect_related_entries_webkb(lines, subset_names):
    """Collect entries related to the sampled subset of names."""
    related_lines = []
    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        parts = [part.strip() for part in parts]
        # Check if the line includes a name from the subset_names
        if "project" in line and parts[1] in subset_names:
            related_lines.append(line)
        elif "courseTA" in line and parts[1] in subset_names:
            related_lines.append(line)
        elif "courseProf" in line and parts[1] in subset_names:
            related_lines.append(line)
        elif set(parts).issubset(subset_names):
            related_lines.append(line)
    return related_lines

def check_predicates_webkb(filtered_lines):
    """Check if the filtered dataset contains the required predicates."""
    predicates_in_filtered = extract_predicates(filtered_lines)
    tasks, courses, persons = get_domains_webkb(filtered_lines)
    tasks, courses, persons = list(tasks), list(courses), list(persons)

    extra_lines = []

    if "project" not in predicates_in_filtered:
        extra_lines.append(f"!project({tasks[0]}, {persons[0]})\n")
    if "courseTA" not in predicates_in_filtered:
        extra_lines.append(f"!courseTA({courses[0]}, {persons[0]})\n")
    if "student" not in predicates_in_filtered:
        extra_lines.append(f"!student({persons[0]})\n")
    if "courseProf" not in predicates_in_filtered:
        extra_lines.append(f"!courseProf({courses[0]}, {persons[0]})\n")
    if "faculty" not in predicates_in_filtered:
        extra_lines.append(f"!faculty({persons[0]})\n")

    return filtered_lines + extra_lines

def webkb_sampling(dataset_file_path, subset_size, folds, target=False):
    required_predicates = {"project", "courseTA", "student", "courseProf", "faculty"}

    lines = read_dataset(dataset_file_path)
    names = extract_people_webkb(lines)
    
    rejections = 0
    
    for i in range(1, folds + 1):
        if target:
            output_file_path = f'./webkb/folds/webkb_target_{subset_size}_{i}.db'
        else:
            output_file_path = f'./webkb/folds/filtered_webkb_{i}.db'
        is_valid = False
        while not is_valid:
            subset_names = sample_subset(names, subset_size)
            related_lines = collect_related_entries_webkb(lines, subset_names)
            final_lines = check_predicates_webkb(related_lines)
            is_valid = check_predicates(final_lines, required_predicates)
            if not is_valid:
                rejections += 1
            else:
                write_filtered_dataset(final_lines, output_file_path)

#################################
# Nations Dataset Sampling
    
def extract_nations(lines):
    nations = set()
    for line in lines:
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        for name in parts:
            nations.add(name.strip())
    return nations

def collect_related_entries_nations(lines, subset_nations):
    filtered_lines = []
    for line in lines:
        # Extract names and strip spaces for accurate comparison
        parts = line.strip().split('(')[1].split(')')[0].split(',')
        names_in_line = {name.strip() for name in parts}

        # Check if all names in the line are in the subset_nations
        if names_in_line.issubset(subset_nations):
            filtered_lines.append(line)
    return filtered_lines

def check_predicates_nations(filtered_lines):
    predicates_in_filtered = extract_predicates(filtered_lines)
    nations = get_domains_nations(filtered_lines)
    nations = list(nations)

    extra_lines = []

    unary_predicates = [
        "Agriculturalpop",
        "Illiterates",
        "Englishtitles",  
        "Usaidreceived",  
        "Purges", 
        "Demonstrations", 
        "Catholics",  
        "Medicinengo",
        "Area",   
        "Rainfall",   
        "Largestrelgn",   
        "Neutralblock",   
        "Age",
        "Lawngos",
        "Export", 
        "Largestlang",
        "Ethnicgrps", 
        "Economicaidtaken",   
        "Techassistancetaken",
        "Foreignmail",
        "Caloriesconsumed",   
        "Artsculturengo", 
        "Assassinations", 
        "Majgovcrisis",   
        "Unpaymentdelinq",
        "Balancepayments",
        "Systemstyle0",   
        "Noncommunist",   
        "Geographyx", 
        "Blocmembership2",
        "Freedomofopposition2",   
        "Govchangelegal1",
        "Legitgov1",  
        "Constitutional2",
        "Electoralsystem2",   
        "Politicalleadership1",   
        "Horizontalpower2",   
        "Military2",  
        "Bureaucracy1",   
        "Censorship2",
        "Freedomofopposition0",   
        "IFCandIBRD", 
        "Airdistance",
        "Religions",  
        "Religioustitles",
        "Goveducationspend",  
        "Femaleworkers",  
        "Exports",
        "Russiantitles",  
        "Primaryschool",  
        "Electoralsystem0",   
        "Politicalleadership0",   
        "Horizontalpower0",   
        "Bureaucracy0",   
        "Censorship0",
        "Geographyy", 
        "Blocmembership1",
        "Systemstyle2",   
        "Constitutional1",
        "Popxenergabs",   
        "Popabs", 
        "Blocmembership0",
        "Threats",
        "Accusations",
        "Militaryaction", 
        "Protests",   
        "Languages",  
        "Communistparty", 
        "Largestethnic",  
        "Constitutional0",
        "Geographyz", 
        "Govchangelegal2",
        "Military1",  
        "Divorces",   
        "Railroadlength", 
        "Militarypersonnel",  
        "Govspending",
        "Govchangelegal0",
        "Military0",  
        "Killedforeignviolence",  
        "Riots",  
        "Diplomatexpelled",   
        "Foreigncollegestud", 
        "Seabornegoods",  
        "Imports",
        "Investments",
        "Electoralsystem1",   
        "Popnland",   
        "Arable", 
        "Politicalparties",   
        "Legitgov0",  
        "Politicalleadership2",   
        "Killeddomesticviolence", 
        "Freedomofopposition1",   
        "Systemstyle1",   
        "Telephone",  
        "Energyconsume",  
        "GNP",
        "Immigrantsmigrants", 
        "Runningwater",   
        "Protein",
        "Bureaucracy2",   
        "Monarchy",   
        "Censorship1",
        "Roadlength", 
        "Emigrants",  
        "Incomeabs",  
        "Unassessment",   
        "Defenseexpabs",  
        "Balanceinvestments", 
        "Unemployed"
    ]

    binary_predicates = [
        "Economicaid",
        "Releconomicaid",
        "Treaties",
        "Reltreaties",
        "Officialvisits",
        "Conferences",
        "Exportbooks",
        "Relexportbooks",
        "Booktranslations",
        "Relbooktranslations",
        "Warning",
        "Violentactions",
        "Militaryactions",
        "Duration",
        "Negativebehavior",
        "Severdiplomatic",
        "Expeldiplomats",
        "Boycottembargo",
        "Aidenemy",
        "Negativecomm",
        "Accusation",
        "PProtests",
        "Unoffialacts",
        "Attackembassy",
        "Nonviolentbehavior",
        "Weightedunvote",
        "Unweightedunvote",
        "Tourism",
        "Reltourism",
        "Tourism3",
        "EEmigrants",
        "Relemigrants",
        "Emigrants3",
        "Students",
        "Relstudents",
        "Relexports",
        "Exports3",
        "Intergovorgs",
        "Relintergovorgs",
        "Ngo",
        "Relngo",
        "Intergovorgs3",
        "Ngoorgs3",
        "Embassy",
        "Reldiplomacy",
        "Timesincewar",
        "Timesinceally",
        "Lostterritory",
        "Dependent",
        "Independence",
        "Commonbloc0",
        "Blockpositionindex",
        "Militaryalliance",
        "Commonbloc1",
        "Commonbloc2"
    ]

    for predicate in unary_predicates:
        if predicate not in predicates_in_filtered:
            extra_lines.append(f"!{predicate}({nations[0]})\n")
    for predicate in binary_predicates:
        if predicate not in predicates_in_filtered:
            extra_lines.append(f"!{predicate}({nations[0]}, {nations[1]})\n")

    return filtered_lines + extra_lines

def nations_sampling(dataset_file_path, subset_size, folds, target=False):
    unary_predicates = [
        "Agriculturalpop",
        "Illiterates",
        "Englishtitles",  
        "Usaidreceived",  
        "Purges", 
        "Demonstrations", 
        "Catholics",  
        "Medicinengo",
        "Area",   
        "Rainfall",   
        "Largestrelgn",   
        "Neutralblock",   
        "Age",
        "Lawngos",
        "Export", 
        "Largestlang",
        "Ethnicgrps", 
        "Economicaidtaken",   
        "Techassistancetaken",
        "Foreignmail",
        "Caloriesconsumed",   
        "Artsculturengo", 
        "Assassinations", 
        "Majgovcrisis",   
        "Unpaymentdelinq",
        "Balancepayments",
        "Systemstyle0",   
        "Noncommunist",   
        "Geographyx", 
        "Blocmembership2",
        "Freedomofopposition2",   
        "Govchangelegal1",
        "Legitgov1",  
        "Constitutional2",
        "Electoralsystem2",   
        "Politicalleadership1",   
        "Horizontalpower2",   
        "Military2",  
        "Bureaucracy1",   
        "Censorship2",
        "Freedomofopposition0",   
        "IFCandIBRD", 
        "Airdistance",
        "Religions",  
        "Religioustitles",
        "Goveducationspend",  
        "Femaleworkers",  
        "Exports",
        "Russiantitles",  
        "Primaryschool",  
        "Electoralsystem0",   
        "Politicalleadership0",   
        "Horizontalpower0",   
        "Bureaucracy0",   
        "Censorship0",
        "Geographyy", 
        "Blocmembership1",
        "Systemstyle2",   
        "Constitutional1",
        "Popxenergabs",   
        "Popabs", 
        "Blocmembership0",
        "Threats",
        "Accusations",
        "Militaryaction", 
        "Protests",   
        "Languages",  
        "Communistparty", 
        "Largestethnic",  
        "Constitutional0",
        "Geographyz", 
        "Govchangelegal2",
        "Military1",  
        "Divorces",   
        "Railroadlength", 
        "Militarypersonnel",  
        "Govspending",
        "Govchangelegal0",
        "Military0",  
        "Killedforeignviolence",  
        "Riots",  
        "Diplomatexpelled",   
        "Foreigncollegestud", 
        "Seabornegoods",  
        "Imports",
        "Investments",
        "Electoralsystem1",   
        "Popnland",   
        "Arable", 
        "Politicalparties",   
        "Legitgov0",  
        "Politicalleadership2",   
        "Killeddomesticviolence", 
        "Freedomofopposition1",   
        "Systemstyle1",   
        "Telephone",  
        "Energyconsume",  
        "GNP",
        "Immigrantsmigrants", 
        "Runningwater",   
        "Protein",
        "Bureaucracy2",   
        "Monarchy",   
        "Censorship1",
        "Roadlength", 
        "Emigrants",  
        "Incomeabs",  
        "Unassessment",   
        "Defenseexpabs",  
        "Balanceinvestments", 
        "Unemployed"
    ]

    binary_predicates = [
        "Economicaid",
        "Releconomicaid",
        "Treaties",
        "Reltreaties",
        "Officialvisits",
        "Conferences",
        "Exportbooks",
        "Relexportbooks",
        "Booktranslations",
        "Relbooktranslations",
        "Warning",
        "Violentactions",
        "Militaryactions",
        "Duration",
        "Negativebehavior",
        "Severdiplomatic",
        "Expeldiplomats",
        "Boycottembargo",
        "Aidenemy",
        "Negativecomm",
        "Accusation",
        "PProtests",
        "Unoffialacts",
        "Attackembassy",
        "Nonviolentbehavior",
        "Weightedunvote",
        "Unweightedunvote",
        "Tourism",
        "Reltourism",
        "Tourism3",
        "EEmigrants",
        "Relemigrants",
        "Emigrants3",
        "Students",
        "Relstudents",
        "Relexports",
        "Exports3",
        "Intergovorgs",
        "Relintergovorgs",
        "Ngo",
        "Relngo",
        "Intergovorgs3",
        "Ngoorgs3",
        "Embassy",
        "Reldiplomacy",
        "Timesincewar",
        "Timesinceally",
        "Lostterritory",
        "Dependent",
        "Independence",
        "Commonbloc0",
        "Blockpositionindex",
        "Militaryalliance",
        "Commonbloc1",
        "Commonbloc2"
    ]

    required_predicates = set(unary_predicates + binary_predicates)

    lines = read_dataset(dataset_file_path)
    nations = extract_nations(lines)

    rejections = 0

    for i in range(1, folds + 1):
        if target:
            output_file_path = f'./nations/folds/nations_target_{subset_size}_{i}.db'
        else:
            output_file_path = f'./nations/folds/filtered_nations_{i}.db'
        is_valid = False
        while not is_valid:
            subset_nations = sample_subset(nations, subset_size)
            related_lines = collect_related_entries_nations(lines, subset_nations)
            final_lines = check_predicates_nations(related_lines)
            is_valid = check_predicates(final_lines, required_predicates)
            if not is_valid:
                rejections += 1
            else:
                write_filtered_dataset(final_lines, output_file_path)

def smoking_sampling(dataset_file_path, subset_size, folds, target=False):
    required_predicates = {"Friends", "Smokes", "Cancer"}

    lines = read_dataset(dataset_file_path)
    names = extract_people_smoking(lines)

    rejections = 0

    for i in range(1, folds + 1):
        if target:
            output_file_path = f'./smoking/folds/smoking_target_{subset_size}_{i}.db'
        else:
            output_file_path = f'./smoking/folds/filtered_smoking_{i}.db'
        is_valid = False
        while not is_valid:
            subset_names = sample_subset(names, subset_size)
            related_lines = collect_related_entries_smoking(lines, subset_names)
            final_lines = check_predicates_smoking(related_lines)
            is_valid = check_predicates(final_lines, required_predicates)
            if not is_valid:
                rejections += 1
            else:
                write_filtered_dataset(final_lines, output_file_path)


if __name__ == "__main__":
    # Smoking
    dataset_file_path = './smoking/smoking.all.db'
    subset_size = 5
    folds = 50
    smoking_sampling(dataset_file_path, subset_size, folds)

    # IMDB
    dataset_file_path = './imdb/imdb.all.db'
    subset_size = 5
    folds = 50
    imdb_sampling(dataset_file_path, subset_size, folds)

    # WebKB
    dataset_file_path = './webkb/webkb.all.db'
    subset_size = 5
    folds = 50
    webkb_sampling(dataset_file_path, subset_size, folds)

    # Nations
    dataset_file_path = './nations/nations.all.db'
    subset_size = 5
    folds = 50
    nations_sampling(dataset_file_path, subset_size, folds)