import subprocess
import os
from datasetSubsampling import smoking_sampling, imdb_sampling, webkb_sampling, nations_sampling
from calculateStatistics import plot_results, calculate_results
from scripts.smokerDatasetCreation import generate_dataset

#region Helper Commands

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def learn_weights(jar, subsample, location, lambda_val=None):
    # Learn the weights
    if lambda_val:
        run_command(f"java -jar ../jars/{jar} --wl --lambda {lambda_val} --train {subsample} formulas.mln")
    else:
        run_command(f"java -jar ../jars/{jar} --wl --train {subsample} formulas.mln")

    # Move the learned MLN to its proper location
    run_command(f"mv formulas_learned.mln {location}")

#endregion
    
dataset_folders = [
    'smoking', 
    'imdb',
    'webkb',
    'nations'
]

directories_to_create = ['folds', 'learned_mlns', 'results']

for directory in dataset_folders:
    for subdirectory in directories_to_create:
        os.makedirs(f"{directory}/{subdirectory}", exist_ok=True)

#region Regularization Definitions
regularizations_with_lambda = [
    ('l1_lbfgs', 'l1_lbfgs.jar'),
    ('l2_lbfgs', 'l2_lbfgs.jar'),
]

regularizations_without_lambda = [
    ('no_reg_lbfgs', 'no_reg_lbfgs.jar'),
]

lambda_values = [0.01, 0.1, 1.0, 10.0, 100.0] # 
#endregion

#region Training Dataset Sampling
sample_size = 20
num_train_folds = 20

dataset_file_path = './smoking/smoking.all.db'
smoking_sampling(dataset_file_path, sample_size, num_train_folds)

sample_size = 50
dataset_file_path = './imdb/imdb.all.db'
imdb_sampling(dataset_file_path, sample_size, num_train_folds)

dataset_file_path = './webkb/webkb.all.db'
webkb_sampling(dataset_file_path, sample_size, num_train_folds)

sample_size = 5
dataset_file_path = './nations/nations.all.db'
nations_sampling(dataset_file_path, sample_size, num_train_folds)
#endregion

#region Target Dataset Sampling
num_target_folds = 5

dataset_file_path = './smoking/smoking.all.db'
smoking_targets = [100, 200, 300, 400] #, 500, 600, 700, 800, 900
for target_size in smoking_targets:
    smoking_sampling(dataset_file_path, target_size, num_target_folds, target=True)
    """ for i in range(1, num_target_folds + 1):
        target_path = f"./smoking/folds/smoking_target_{target_size}_{i}.db"
        generate_dataset(target_size, target_path) """

dataset_file_path = './imdb/imdb.all.db'
imdb_targets = [100, 150, 200, 250]
for target_size in imdb_targets:
    imdb_sampling(dataset_file_path, target_size, num_target_folds, target=True)

dataset_file_path = './webkb/webkb.all.db'
webkb_targets = [100, 200, 300, 400, 500, 600, 700]
for target_size in webkb_targets:
    webkb_sampling(dataset_file_path, target_size, num_target_folds, target=True)

dataset_file_path = './nations/nations.all.db'
nations_targets = [8,10,12]
for target_size in nations_targets:
    nations_sampling(dataset_file_path, target_size, num_target_folds, target=True)
#endregion

#region Experiments
experiments = [
    ('smoking', 'damlnSmoking.py', smoking_targets), 
    ('imdb', 'damlnImdb.py', imdb_targets),
    ('webkb', 'damlnWebkb.py', webkb_targets),
    ('nations', 'damlnNations.py', nations_targets),
]

for directory, damln_script, targets in experiments:
        
    os.chdir(directory)
    print("\n\n##############################################")
    print(f"Running Dataset {directory}")
    print("##############################################\n\n")

    # For every Fold
    for i in range(1, num_train_folds + 1):

        print("\n\n##############################################")
        print(f"Learning Fold {i}")
        print("##############################################\n\n")

        # Define the database we're learning from
        subsample = f"./folds/filtered_{directory}_{i}.db"

        # For every regularization that requires lambda
        for reg, jar in regularizations_with_lambda:

            print("\n\n##############################################")
            print(f"Learning with Regularization {reg}")
            print("##############################################\n\n")

            # For every lambda value
            for lambda_val in lambda_values:

                print("\n\n##############################################")
                print(f"Lambda: {lambda_val}")
                print("##############################################\n\n")

                # Define the location of the learned MLN
                mln_location = f"./learned_mlns/{directory}_{reg}_{i}_{lambda_val}.mln"

                # Learn the weights
                learn_weights(jar, subsample, mln_location, lambda_val)

        # For every regularization that does not require lambda
        for reg, jar in regularizations_without_lambda:

            print("\n\n##############################################")
            print(f"Learning with Regularization {reg}")
            print("##############################################\n\n")

            # Define the location of the learned MLN
            mln_location = f"./learned_mlns/{directory}_{reg}_{i}.mln"

            # Learn the weights
            learn_weights(jar, subsample, mln_location)

        # For every target
        target_list = [(str(target_size), target_fold) for target_size in targets for target_fold in range(1, num_target_folds + 1)]
        target_list.append(('all', 0))
        for target in target_list:
                
            print("\n\n##############################################")
            print(f"Inferencing Target {target}")
            print("##############################################\n\n")

            if target[0] == 'all':
                target_location = f"./{directory}.all.db"
            else:
                target_location = f"./folds/{directory}_target_{target[0]}_{target[1]}.db"

            # For every regularization that requires lambda
            for reg, jar in regularizations_with_lambda:

                print("\n\n##############################################")
                print(f"Running Inference with Weights learned from Regularization {reg}")
                print("##############################################\n\n")

                # For every lambda value
                for lambda_val in lambda_values:

                    print("\n\n##############################################")
                    print(f"Lambda: {lambda_val}")
                    print("##############################################\n\n")

                    # Define the location of the learned MLN
                    mln_location = f"./learned_mlns/{directory}_{reg}_{i}_{lambda_val}.mln"

                    # Define the location of the results
                    results_location = f"./results/{reg}_{i}_{lambda_val}_{target[0]}_{target[1]}.txt"

                    # Run inference
                    run_command(f"java -jar ../jars/{jar} --ll --test {target_location} {mln_location} > {results_location}")

            # For every regularization that does not require lambda
            for reg, jar in regularizations_without_lambda:

                print("\n\n##############################################")
                print(f"Running Inference with Weights learned from Regularization {reg}")
                print("##############################################\n\n")

                # Define the location of the learned MLN
                mln_location = f"./learned_mlns/{directory}_{reg}_{i}.mln"

                # Define the location of the results
                results_location = f"./results/{reg}_{i}_{target[0]}_{target[1]}.txt"

                # Run inference
                run_command(f"java -jar ../jars/{jar} --ll --test {target_location} {mln_location} > {results_location}")

                print("\n\n##############################################")
                print(f"Learning & Inferencing DAMLN")
                print("##############################################\n\n")
                    
                # Define the location of the damln MLN
                damln_location = f"./learned_mlns/{directory}_damln_{reg}_{i}_{target[0]}_{target[1]}.mln"

                # Define the location of the results
                results_location = f"./results/damln_{reg}_{i}_{target[0]}_{target[1]}.txt"

                # Adjust the weights
                run_command(f"python ../{damln_script} {mln_location} {damln_location} {target_location}")

                # Run inference
                run_command(f"java -jar ../jars/{jar} --ll --test {target_location} {damln_location} > {results_location}")

    os.chdir('..')  # Change back to the parent directory

#endregion