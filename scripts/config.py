import os

######################### READ: idiosyncratic path error #########################################
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# This sets the current path to the parent directory. I was getting annoyed at being cd into the wrong places.
# You shouldn't need this and can comment out this block.
##################################################################################################

import torch.nn as nn
import torch.optim as optim
from src.models.CNNten import CNNten
from src.models.FCNten import FCNten
from src.models.MLPten import MLPten
from src.models.CNNten_multi_task import CNNten_multi_task
#from src.models.CrystalNet import 

# Paths
DATA_DIR = '/monfs01/projects/ys68/XRD_ML/simXRD_partial_data'
MODEL_SAVE_DIR = '/monfs01/projects/ys68/XRD_ML/trained_models'

# Data
TRAIN_DATA = os.path.join(DATA_DIR, 'train.db')
VAL_DATA = os.path.join(DATA_DIR, 'val.db')
TEST_DATA = os.path.join(DATA_DIR, 'test.db')

# For file naming purposes
NAME_OF_DATA_USED = "simXRD_partial_data"

# Model Setup
MODEL_TYPE = "CNNten"     # Options: "CNNten", "FCNten", "MLPten", "CNNten_multi_task"
MULTI_TASK = False                    # Set to True for multi-task learning (points train function to train_multi_spg_cryssystem_blt_element.py)
CRITERION_TYPE = "CrossEntropyLoss"  # Options: "CrossEntropyLoss", "MSELoss"
OPTIMIZER_TYPE = "Adam"              # Options: "Adam", "SGD"

# Multi-task specific settings. Ignore if not multi
MULTI_TASK_CRITERIA = {
    'spg': nn.CrossEntropyLoss(),
    'crysystem': nn.CrossEntropyLoss(),
    'blt': nn.CrossEntropyLoss(),
    'composition': nn.MSELoss()
}

# Hyper Parasms
LEARNING_RATE = 0.001
BATCH_SIZE = 32
NUM_EPOCHS = 25

# Data Loading Settings
NUM_WORKERS = 8

# WandB configuration (Note that there is already a basic WandB log in train.py)
WANDB_PROJECT_NAME = "test_2"
WANDB_SAVE_DIR = "/monfs01/projects/ys68/XRD_ML"
SAVE_MODEL_TO_WANDB_SERVERS = False
WANDB_LOG_ARCHITECTURE = False


############# DON'T TOUCH - Classes are the options for above) ##################
MODEL_CLASS = {
    "CNNten": CNNten,
    "FCNten": FCNten,
    "MLPten": MLPten,
    "CNNten_multi_task": CNNten_multi_task
}
CRITERION_CLASS = {
    "CrossEntropyLoss": nn.CrossEntropyLoss,
    "MSELoss": nn.MSELoss
}
OPTIMIZER_CLASS = {
    "Adam": optim.Adam,
    "SGD": optim.SGD
}