# Experiments for Understanding Domain-Size Generalization in Markov Logic Networks

These are the experiments we conducted to evaluate the effect of reducing parameter variance on generalization behavior across varying domain sizes.

Here is is explanation of the files, code, and usage.

## Datasets

The folders **smoking**, **imdb**, **webkb** and **nations** contain the full dataset as well as the formulas for the to-be-trained MLN.

Each folder also contains a results folder which contains our results. In a result file one can also see the trained MLNs with the weights. The .zip file contains these same results. The folds and learned_mlns folders are necessary to run the experiments.

## Utility Scripts

**scripts/smokerDatasetCreation.py** creates the dataset for Friends & Smokers (FS).  
Parameters about the resulting dataset can be edited and the script can be called to create a new FS dataset.

**domainSizeCounting.py** is a utility script that counts the domain sizes of datasets.

## Weight Learning

To learn the weights we worked with the Forclift software by Van den Broek et al. It is available on github: [https://github.com/UCLA-StarAI/Forclift](https://github.com/UCLA-StarAI/Forclift)    
We added slight adjustments to include L1 and L2 regularization in the training process, the resulting compiled jar files in the jars folder are used during training of the MLNs.  
For the sake of completeness, we also added a copy of the Forclift software with our adaptations in the 'Forclift' folder.

The formulas for the Markov Logic Networks, except for the Nations formulas, where we used a handcrafted MLN, were also taken from Van den Broek et al.

Our own implementation of Domain-Size Aware Markov Logic Networks can be found in the damlnSmoking.py, damlnImdb.py, damlnWebkb.py and damlnNations.py files, which calculate the scaling factor based on the test set and downscale the weights learned by the regular generative weight learning process accordingly. 

## Experiment Setup

Our experiments are defined in **experiments.py**. First, training and test folds are sampled. Then for each training sample, regularization method, and tested hyperparameter value, the weights of the MLN are learned. The experiments can be run by calling the script **experiments.py**, adjustments to the experiment setup can be made in the code.

**Attention:** To run the experiments a 'folds', 'learned_mlns' and 'results' folder need to be present in each dataset folder. Running the experiments will overwrite the contained results. You can recover our results through the .zip files or by saving them prior to running the experiments.

## Results

Plots and summary statistics are generated and calculated in **calculateStatistics.py**. This assumes that the results are present in the results folders for the individual datasets. Note that in case of a change in the experiment setup, changes in the results calculation could also be necessary.