import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import unicodedata

def parse_loglikelihood(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('loglikelihood'):
                _, value = line.strip().split('=')
                return float(value)
    return None

def aggregate_statistics(results_folder, regularization, n, m, lambda_val=None, method=None, target=None, n_min=1):
    loglikelihoods = []
    for i in range(n_min, n + 1):
        if target == 'all':
            file_name = f"{regularization}_{method}"
            file_name += f"_{i}"
            if lambda_val is not None:
                file_name += f"_{lambda_val}"
            file_name += f"_{target}_0.txt"
            file_path = os.path.join(results_folder, 'results', file_name)
            loglikelihood = parse_loglikelihood(file_path)
            if loglikelihood is not None:
                loglikelihoods.append(loglikelihood)
        else:
            for j in range(1, m + 1):
                file_name = f"{regularization}_{method}"
                file_name += f"_{i}"
                if lambda_val is not None:
                    file_name += f"_{lambda_val}"
                file_name += f"_{target}_{j}.txt"
                file_path = os.path.join(results_folder, 'results', file_name)
                loglikelihood = parse_loglikelihood(file_path)
                if loglikelihood is not None:
                    loglikelihoods.append(loglikelihood)
    
    if loglikelihoods:
        mean, std_dev = np.mean(loglikelihoods), np.std(sorted(loglikelihoods), ddof=1)
        return mean, std_dev, loglikelihoods
    else:
        return None, None, []

def find_best_lambda(results_folder, reg, method, target_splits, lambda_values, n, m):
    validation_min = int(n * 0.8) + 1
    test_max = int(n * 0.8)
    # Test on 20% validation set
    means = {}
    std_devs = {}

    for lambda_val in lambda_values:
        means[lambda_val] = []
        std_devs[lambda_val] = []
        
        for target_split in target_splits:
            mean, std_dev, _ = aggregate_statistics(results_folder, reg, lambda_val=lambda_val, method=method, target=target_split, n=n, m=m, n_min=validation_min)
            means[lambda_val].append(mean)
            std_devs[lambda_val].append(std_dev)

    best_lambda = max(means, key=lambda x: np.mean(means[x]))

    # With the best lambda, calculate the mean and std dev for the test set
    best_means = []
    best_std_devs = []
    for target_split in target_splits:
        mean, std_dev, _ = aggregate_statistics(results_folder, reg, lambda_val=best_lambda, method=method, target=target_split, n=test_max, m=m)
        best_means.append(mean)
        best_std_devs.append(std_dev)    

    return best_lambda, best_means, best_std_devs

    

def reg_to_label(reg, best_lambdas):
    my_char = "GREEK SMALL LETTER LAMDA"
    char_lambda = unicodedata.lookup(my_char)
    if reg == 'no_reg':
        return 'No Reg'
    elif reg == 'l1':
        return 'L1 (' + char_lambda + ' = ' + str(best_lambdas[reg]) + ')'
    elif reg == 'l2':
        return 'L2 (' + char_lambda + ' = ' + str(best_lambdas[reg]) + ')'
    elif reg == 'damln_no_reg':
        return 'DAMLN'
    else:
        return reg

# Let's plot the results with the best lambda for l1 and l2
def plot_results(results_folders, methods, regularizations, lambda_values, n, m):
    colors = {
        'no_reg': 'red',
        'l1': 'lime',
        'l2': 'green',
        'damln_no_reg': 'blue'
    }

    markers = {
        'no_reg': 's',
        'l1': 'o',
        'l2': 'x',
        'damln_no_reg': '^'
    }

    for (results_folder, target_splits, all_size) in results_folders:
        means = {}
        std_devs = {}
        sizes = []
        best_lambdas = {}

        for reg in ['no_reg', 'damln_no_reg', 'l1', 'l2']:
            means[reg] = []
            std_devs[reg] = []

        for target_split in target_splits:
            size = all_size if target_split == 'all' else int(target_split)
            sizes.append(size)

        for method in methods:
            for reg in regularizations:
                if reg == 'no_reg' or reg == 'damln_no_reg':
                    for target_split in target_splits:
                        mean, std_dev, _ = aggregate_statistics(results_folder, reg, method=method, target=target_split, n=n, m=m)
                        means[reg].append(mean)
                        std_devs[reg].append(std_dev)
                elif reg in ['l1', 'l2']:
                    best_lambda, best_means, best_std_devs = find_best_lambda(results_folder, reg, method, target_splits, lambda_values, n=n, m=m)
                    print(f"Best lambda for {reg} {method} {target_splits}: {best_lambda}")
                    best_lambdas[reg] = best_lambda
                    means[reg] = best_means
                    std_devs[reg] = best_std_devs

        # Normalize with no_reg baseline
        for reg in ['l1', 'l2', 'damln_no_reg']:
            means[reg] = list(np.array(means[reg]) - np.array(means['no_reg']))

        # set no_reg to 0
        means['no_reg'] = [0 for _ in range(len(sizes))]
                        
        class Labeloffset:
            def __init__(self, ax, label="", axis="y", fontsize=26):
                self.axis = {"y": ax.yaxis, "x": ax.xaxis}[axis]
                self.label = label
                self.fontsize = fontsize
                ax.callbacks.connect(axis+'lim_changed', self.update)
                ax.figure.canvas.draw()
                self.update(None)

            def update(self, lim):
                fmt = self.axis.get_major_formatter()
                self.axis.offsetText.set_visible(False)
                # Apply the font size to the label text
                self.axis.set_label_text(self.label + " " + fmt.get_offset(), fontsize=self.fontsize)

        # Now let's plot the results for this dataset
        plt.figure(figsize=(10, 6))
        ax = plt.gca()

        # Setup the formatter and apply it
        formatter = ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((0,0))
        ax.yaxis.set_major_formatter(formatter)


        for reg in means:
            color = colors.get(reg, 'black')  # Use black if the reg method isn't in the colors dictionary
            marker = markers.get(reg, 'o')
            plt.plot(sizes, means[reg], color=color, marker=marker, markersize=16, label=reg_to_label(reg, best_lambdas))  # Plot data

        plt.tick_params(axis='both', which='major', labelsize=22)
        # Apply the Labeloffset with the desired font size
        my_char = "GREEK CAPITAL LETTER DELTA"
        Delta = unicodedata.lookup(my_char)
        lo = Labeloffset(ax, label=Delta + " Average LL", axis="y", fontsize=26)

        plt.xlabel('Domain size', fontsize=26)

        plt.legend(loc="upper left", frameon=False, fontsize=24)
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{results_folder}_likelihoods_mean.eps'), format='eps')
        plt.show()

def calculate_results(results_folders, methods, regularizations, lambda_values, n, m):
    for (results_folder, target_splits, _) in results_folders:
        print("\n#################################")
        print(f"Results for {results_folder.split('/')[-1]}")
        print("#################################\n\n")

        for target_split in target_splits:

            print("\n\n##############################################")
            print(f"Results for Target Split {target_split}")
            print("##############################################\n\n")

            for method in methods:
                for reg in regularizations:
                    if reg == 'no_reg' or reg == 'damln_no_reg':
                        mean, std_dev, loglikelihoods = aggregate_statistics(results_folder, reg, method=method, target=target_split, n=n, m=m)
                        print(f'{reg.upper()} {method.upper()} Mean Loglikelihood: {mean}, Standard Deviation: {std_dev}')
                    elif reg == 'l1' or reg == 'l2':
                        for lambda_val in lambda_values:
                            mean, std_dev, loglikelihoods = aggregate_statistics(results_folder, reg, lambda_val=lambda_val, method=method, target=target_split, n=n, m=m)
                            print(f'{reg.upper()} {method.upper()} Lambda {lambda_val} Mean Loglikelihood: {mean}, Standard Deviation: {std_dev}')
                    
if __name__ == '__main__':
    # Define experiments, their respective directories, and subset sizes
    results_folders = [
        ('./smoking', ['100', '200', '300', '400', 'all'], 500),
        ('./imdb', ['100', '150', '200', '250', 'all'], 268), 
        ('./webkb', ['100', '200', '300', '400', '500', '600', '700', 'all'], 746),
        ('./nations', ['8', '10', '12', 'all'], 14)
    ]
    lambda_values = [0.01, 0.1, 1.0, 10.0, 100.0]
    methods = ['lbfgs']
    regularizations = ['no_reg', 'l1', 'l2', 'damln_no_reg'] # 

    plot_results(results_folders, methods, regularizations, lambda_values, n=20, m=5)
    calculate_results(results_folders, methods, regularizations, lambda_values, n=20, m=5)