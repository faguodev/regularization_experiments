import random
import itertools
from faker.providers.person.en import Provider

def create_people(n):
    first_names = list(set(Provider.first_names))
    random.shuffle(first_names)

    names = first_names[0:n]
    return list(names)

def assign_smokers(people, proportion):
    smokers_count = int(len(people) * proportion)
    smokers = set(random.sample(people, smokers_count))
    return smokers

def assign_cancer(people, smokers, cancer_prop_smokers, cancer_prop_nonsmokers):
    cancer_smokers_count = int(len(smokers) * cancer_prop_smokers)
    cancer_nonsmokers_count = int((len(people) - len(smokers)) * cancer_prop_nonsmokers)
    
    cancer_smokers = set(random.sample(list(smokers), cancer_smokers_count))
    nonsmokers = set(people) - smokers
    cancer_nonsmokers = set(random.sample(list(nonsmokers), cancer_nonsmokers_count))
    
    return cancer_smokers.union(cancer_nonsmokers)

def create_exact_friendships(people, smokers, friendship_prop_same, friendship_prop_diff):
    friendships = set()
    nonsmokers = set(people) - smokers
    
    # Calculate exact numbers
    num_same = int(friendship_prop_same * (len(smokers) * (len(smokers) - 1) / 2 + len(nonsmokers) * (len(nonsmokers) - 1) / 2))
    num_diff = int(friendship_prop_diff * (len(smokers) * len(nonsmokers)))
    
    # Generate smoker-smoker and nonsmoker-nonsmoker friendships
    same_friendships = list(itertools.combinations(smokers, 2)) + list(itertools.combinations(nonsmokers, 2))
    random.shuffle(same_friendships)
    for friendship in same_friendships[:num_same]:
        friendships.add(friendship)

    # Generate smoker-nonsmoker friendships
    diff_friendships = list(itertools.product(smokers, nonsmokers))
    random.shuffle(diff_friendships)
    for friendship in diff_friendships[:num_diff]:
        friendships.add(friendship)
    
    return friendships

def generate_dataset(n, smoker_prop, cancer_prop_smokers, cancer_prop_nonsmokers, friendship_prop_same, friendship_prop_diff, file_path):
    print("creating people")
    people = create_people(n)
    print("creating smokers")
    smokers = assign_smokers(people, smoker_prop)
    print("assigning cancer")
    cancer_people = assign_cancer(people, smokers, cancer_prop_smokers, cancer_prop_nonsmokers)
    print("creating friendships")
    friendships = create_exact_friendships(people, smokers, friendship_prop_same, friendship_prop_diff)
    
    with open(file_path, 'w') as db_file:
        for friendship in friendships:
            db_file.write(f"Friends({friendship[0]}, {friendship[1]})\n")
            db_file.write(f"Friends({friendship[1]}, {friendship[0]})\n")
        
        for smoker in smokers:
            db_file.write(f"Smokes({smoker})\n")
        
        for person_with_cancer in cancer_people:
            db_file.write(f"Cancer({person_with_cancer})\n")

if __name__ == "__main__":
    n = 500  # Total number of people
    smoker_prop = 0.4  # Proportion of smokers
    cancer_prop_smokers = 0.3  # Proportion of smokers who have cancer
    cancer_prop_nonsmokers = 0.1  # Proportion of non-smokers who have cancer
    friendship_prop_same = 0.8  # Proportion of friendships where both are smokers or non-smokers
    friendship_prop_diff = 0.1  # Proportion of friendships between a smoker and a non-smoker
    file_path = "./smoking/smoking.all.db"  # Path to the output file

    # Generate the dataset and write to file
    generate_dataset(n, smoker_prop, cancer_prop_smokers, cancer_prop_nonsmokers, friendship_prop_same, friendship_prop_diff, file_path)