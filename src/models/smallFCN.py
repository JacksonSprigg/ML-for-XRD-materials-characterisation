import torch.nn as nn
import torch.nn.functional as F

# The FCN from: https://onlinelibrary.wiley.com/doi/full/10.1002/aisy.202300140
# As described here: https://github.com/socoolblue/Advanced_XRD_Analysis/blob/main/XRD_analysis.ipynb
# Accessed 28/07/2024

# Modifications:
# I alter some of the final conv layers to account for the smaller input data (1,3501)
# I augment a second module to allow for multi-task outputs.

# TODO: Check it is implememnted correctly..

class smallFCN(nn.Module):
    def __init__(self):
        super(smallFCN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv1d(1, 16, kernel_size=6, padding=2)
        self.conv2 = nn.Conv1d(16, 16, kernel_size=6, padding=2)
        self.conv3 = nn.Conv1d(16, 32, kernel_size=6, padding=2)
        self.conv4 = nn.Conv1d(32, 32, kernel_size=6, padding=2)
        self.conv5 = nn.Conv1d(32, 64, kernel_size=6, padding=2)
        self.conv6 = nn.Conv1d(64, 64, kernel_size=6, padding=2)
        self.conv7 = nn.Conv1d(64, 128, kernel_size=6, padding=2)
        self.conv8 = nn.Conv1d(128, 128, kernel_size=6, padding=2)
        self.conv9 = nn.Conv1d(128, 256, kernel_size=6, padding=2)
        self.conv10 = nn.Conv1d(256, 256, kernel_size=6, padding=2)

        self.spg_conv_1 = nn.Conv1d(256, 256, kernel_size=6, padding=2)
        self.spg_conv_2 = nn.Conv1d(256, 230, kernel_size=1)
        
        # Pooling layer
        self.pool = nn.MaxPool1d(2)
        
        # Dropout layer
        self.dropout = nn.Dropout(0.3)
        
        # Flatten layer
        self.flatten = nn.Flatten()

    def forward(self, x):
        # Apply convolutions, activations, pooling, and dropout
        x = self.dropout(self.pool(F.relu(self.conv1(x))))
        x = self.dropout(self.pool(F.relu(self.conv2(x))))
        x = self.dropout(self.pool(F.relu(self.conv3(x))))
        x = self.dropout(self.pool(F.relu(self.conv4(x))))
        x = self.dropout(self.pool(F.relu(self.conv5(x))))
        x = self.dropout(self.pool(F.relu(self.conv6(x))))
        x = self.dropout(self.pool(F.relu(self.conv7(x))))
        x = self.dropout(self.pool(F.relu(self.conv8(x))))
        x = self.dropout(self.pool(F.relu(self.conv9(x))))
        x = self.dropout(self.pool(F.relu(self.conv10(x))))

        spg_out = self.dropout(F.relu(self.spg_conv_1(x)))
        spg_out = self.spg_conv_2(spg_out)
        spg_out = self.flatten(spg_out)
        
        return spg_out

class smallFCN_multi_task(nn.Module):
    def __init__(self):
        super(smallFCN_multi_task, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv1d(1, 16, kernel_size=6, padding=2)
        self.conv2 = nn.Conv1d(16, 16, kernel_size=6, padding=2)
        self.conv3 = nn.Conv1d(16, 32, kernel_size=6, padding=2)
        self.conv4 = nn.Conv1d(32, 32, kernel_size=6, padding=2)
        self.conv5 = nn.Conv1d(32, 64, kernel_size=6, padding=2)
        self.conv6 = nn.Conv1d(64, 64, kernel_size=6, padding=2)
        self.conv7 = nn.Conv1d(64, 128, kernel_size=6, padding=2)
        self.conv8 = nn.Conv1d(128, 128, kernel_size=6, padding=2)
        self.conv9 = nn.Conv1d(128, 256, kernel_size=6, padding=2)
        self.conv10 = nn.Conv1d(256, 256, kernel_size=6, padding=2)

        self.crysystem_conv_1 = nn.Conv1d(256, 64, kernel_size=6, padding=2)
        self.crysystem_conv_2 = nn.Conv1d(64, 7, kernel_size=1)

        self.blt_conv_1 = nn.Conv1d(256, 64, kernel_size=6, padding=2)
        self.blt_conv_2 = nn.Conv1d(64, 6, kernel_size=1)

        self.spg_conv_1 = nn.Conv1d(256, 256, kernel_size=6, padding=2)
        self.spg_conv_2 = nn.Conv1d(256, 230, kernel_size=1)

        self.composition_conv_1 = nn.Conv1d(256, 256, kernel_size=6, padding=2)
        self.composition_conv_2 = nn.Conv1d(256, 118, kernel_size=1)
        
        # Pooling layer
        self.pool = nn.MaxPool1d(2)
        
        # Dropout layer
        self.dropout = nn.Dropout(0.3)
        
        # Flatten layer
        self.flatten = nn.Flatten()

    def forward(self, x):
        # Apply convolutions, activations, pooling, and dropout
        x = self.dropout(self.pool(F.relu(self.conv1(x))))
        x = self.dropout(self.pool(F.relu(self.conv2(x))))
        x = self.dropout(self.pool(F.relu(self.conv3(x))))
        x = self.dropout(self.pool(F.relu(self.conv4(x))))
        x = self.dropout(self.pool(F.relu(self.conv5(x))))
        x = self.dropout(self.pool(F.relu(self.conv6(x))))
        x = self.dropout(self.pool(F.relu(self.conv7(x))))
        x = self.dropout(self.pool(F.relu(self.conv8(x))))
        x = self.dropout(self.pool(F.relu(self.conv9(x))))
        x = self.dropout(self.pool(F.relu(self.conv10(x))))
        
        # Multi-task specific layers
        crysystem_out = self.dropout(F.relu(self.crysystem_conv_1(x)))
        crysystem_out = self.crysystem_conv_2(crysystem_out)
        crysystem_out = self.flatten(crysystem_out)

        blt_out = self.dropout(F.relu(self.blt_conv_1(x)))
        blt_out = self.blt_conv_2(blt_out)
        blt_out = self.flatten(blt_out)

        spg_out = self.dropout(F.relu(self.spg_conv_1(x)))
        spg_out = self.spg_conv_2(spg_out)
        spg_out = self.flatten(spg_out)

        composition_out = self.dropout(F.relu(self.composition_conv_1(x)))
        composition_out = self.composition_conv_2(composition_out)
        composition_out = self.flatten(composition_out)
        
        return {
            'spg': spg_out,
            'crysystem': crysystem_out,
            'blt': blt_out,
            'composition': composition_out
        }