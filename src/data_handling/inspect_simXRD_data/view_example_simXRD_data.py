import matplotlib.pyplot as plt
from ase.db import connect
from collections import Counter
import torch
import numpy as np
from heapq import heappush, heappushpop

### Let's look at the simXRD data ###

# I save plots to /scratch. Don't accidentally overload this storage.
#  **READ MONARCH DOCUMENTATION TO MAKE SURE YOU DON'T CRASH THE MACHINE**

# ase.db stores a lot of different atomic data
# See https://wiki.fysik.dtu.dk/ase/ase/db/db.html#description-of-a-row
# I checked the files and will list ALL the USEFUL keys we have access to below.

################## Here is the data that we have access to ###########################
# _keys: Shows some keys
# key_value_pairs: Shows key value pairs
# get: Method that does?
# count_atoms: Method that does?
# toatoms: Method that does?

# I think these are the same?
# chem_form: ex. La2Pd2
# formula: ex. La2Pd2

# intensity: XRD intensities, normalised to 100 | 3501 x 1 vector
# latt_dis: Lattice distances | 3501 x 1 vector
# mass: Atomic mass
# natoms: Number of atoms | int
# numbers: Atomic numbers | int | (N,)
# pbc: Periodic boundary condition flags | bool | (3,) - I think these are all just false and there isn't actually any information here
# simulation_param: Yes - I don't know what this actually means
# symbols: A list, e.g., ['H', 'H', 'H', 'H', 'C', 'C', 'O', 'O', 'O', 'O', 'O', 'O']
# tager: [Space Group, Crystal System, ??something else??] - I think the something else is bravis lattice types?

# Note the crystal system meaning:
#  1 : Cubic
#  2 : Hexagonal
#  3 : Tetragonal
#  4 : Orthorhombic
#  5 : Trigonal
#  6 : Monoclinic
#  7 : Triclinic
#####################################################################################

## Note that you may need to change this path depending on permissions ##
train_data_path = "/monfs01/projects/ys68/XRD_ML/simXRD_partial_data/train.db"  # Train size = 5000
test_data_path = "/monfs01/projects/ys68/XRD_ML/simXRD_partial_data/test.db"    # Test size  = 2000
val_data_path = "/monfs01/projects/ys68/XRD_ML/simXRD_partial_data/val.db"      # Val size   = 1000
databs = connect(train_data_path)

# Creating an XRD plot
def plot_xrd_data(latt_dis, intensity, chem_form, atomic_mass, spg, crysystem, bravislatt_type, image_save_path):

    # Plot the X-ray diffraction data
    plt.figure(figsize=(12, 6))
    plt.plot(latt_dis, intensity, 'b-')
    plt.xlabel('Lattice Plane Distance')
    plt.ylabel('Intensity')
    plt.title(f'X-ray Diffraction Pattern for {(chem_form)}')
    plt.grid(True)

    # Get the name of the crystal system
    crystal_systems = {
    1: "Cubic",
    2: "Hexagonal",
    3: "Tetragonal",
    4: "Orthorhombic",
    5: "Trigonal",
    6: "Monoclinic",
    7: "Triclinic"}
    crystal_system_name = crystal_systems.get(crysystem, "Unknown")
    
    # Data information
    plt.text(0.95, 0.95, f'Formula: {chem_form}', transform=plt.gca().transAxes, 
        verticalalignment='top', horizontalalignment='right')
    plt.text(0.95, 0.90, f'Atomic mass: {atomic_mass}', transform=plt.gca().transAxes, 
            verticalalignment='top', horizontalalignment='right')
    plt.text(0.95, 0.75, f'Space Group: {spg}', transform=plt.gca().transAxes, 
             verticalalignment='top', horizontalalignment='right')
    plt.text(0.95, 0.70, f'Crystal System: {crystal_system_name}', transform=plt.gca().transAxes, 
             verticalalignment='top', horizontalalignment='right')
    plt.text(0.95, 0.65, f'Bravis Latt Type: {bravislatt_type}', transform=plt.gca().transAxes, 
             verticalalignment='top', horizontalalignment='right')

    # Save the plot as a PNG file
    plt.savefig(image_save_path+f'xrd_plot_{(chem_form)}.png')

    return

# Have a look at the data
def looking_at_data(db_path, max_iterations, plot=False):
    count = 0
    
    spg_values = []
    crysystem_values = []
    blt_values = []
    composition_lengths = []
    element_counts = {}

    # Heap to keep track of the 50 largest compositions
    largest_compositions = []

    element_set = set([
        'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
        'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
        'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
        'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
        'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
        'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
        'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
        'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
        'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
        'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
        'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
        'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
    ])

    for row in databs.select():
        element = getattr(row, 'symbols')
        latt_dis = eval(getattr(row, 'latt_dis'))
        intensity = eval(getattr(row, 'intensity'))

        spg = eval(getattr(row, 'tager'))[0]
        crysystem = eval(getattr(row, 'tager'))[1]
        bravislatt_type = eval(getattr(row, 'tager'))[2]

        chem_form = getattr(row, 'chem_form')
        atomic_mass = getattr(row, 'mass')

        # Collect values for analysis
        spg_values.append(spg)
        crysystem_values.append(crysystem)
        blt_values.append(bravislatt_type)
        composition_length = len(element)
        composition_lengths.append(composition_length)

        # Process composition
        composition = Counter(element)
        for elem in composition:
            element_counts[elem] = element_counts.get(elem, 0) + composition[elem]

        # Keep track of the 50 largest compositions
        if len(largest_compositions) < 50:
            heappush(largest_compositions, (composition_length, chem_form))
        elif composition_length > largest_compositions[0][0]:
            heappushpop(largest_compositions, (composition_length, chem_form))

        # Print detailed information for the first few samples (unchanged)
        if count < 2:
            print(f"\nSample {count + 1}:")
            print(f"SPG: {spg}, Crystal System: {crysystem}, Bravais Lattice Type: {bravislatt_type}")
            print(f"Chemical Formula: {chem_form}")
            print(f"Elements: {element}")
            print(f"Atomic Mass: {atomic_mass}")
            print(f"Intensity shape: {len(intensity)}")
            print(f"Lattice distance shape: {len(latt_dis)}")
            print(f"Composition: {dict(composition)}")
            print(f"Number of elements in composition: {len(composition)}")
            
            # Debug prints
            print(f"SPG value: {spg}")
            print(f"Crystal System value: {crysystem}")
            print(f"Bravais Lattice Type value: {bravislatt_type}")

        if plot:
            plot_xrd_data(latt_dis, intensity, chem_form, atomic_mass, spg, crysystem, bravislatt_type, image_save_path)
        
        count += 1
        if count == max_iterations:
            break

    # Analyze collected data
    print("\nData Analysis:")
    print(f"Total samples analyzed: {count}")
    
    print("\nSPG:")
    print(f"Range: {min(spg_values)} - {max(spg_values)}")
    print(f"Unique values: {sorted(set(spg_values))}")
    
    print("\nCrystal System:")
    print(f"Range: {min(crysystem_values)} - {max(crysystem_values)}")
    print(f"Unique values: {sorted(set(crysystem_values))}")
    
    print("\nBravais Lattice Type:")
    print(f"Unique values: {sorted(set(blt_values))}")
    
    print("\nComposition:")
    print(f"Min elements: {min(composition_lengths)}")
    print(f"Max elements: {max(composition_lengths)}")
    print(f"Total unique elements: {len(element_counts)}")
    print("Most common elements:")
    for elem, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:118]:
        print(f"  {elem}: {count}")

    # Check for potential issues
    if min(spg_values) < 1 or max(spg_values) > 230:
        print("\nWARNING: SPG values out of expected range (1-230)")
    
    if min(crysystem_values) < 1 or max(crysystem_values) > 7:
        print("\nWARNING: Crystal system values out of expected range (1-7)")
    
    if len(set(blt_values)) != 6:
        print("\nWARNING: Unexpected number of unique Bravais lattice types (expected 6)")

    if len(element_counts) < len(element_set):
        print(f"\nNOTE: Only {len(element_counts)} out of {len(element_set)} possible elements are present in the dataset")

    # Print the 50 largest compositions
    print("\n50 Largest Compositions:")
    for size, formula in sorted(largest_compositions, reverse=True):
        print(f"Size: {size}, Formula: {formula}")

    return

# Look at the frequency of each space group
def analyze_space_groups(databs, max_iterations):
    space_groups = []
    count = 0
    for row in databs.select():
        spg = eval(getattr(row, 'tager'))[0]
        space_groups.append(spg)
        count += 1
        if count == max_iterations:
            break

    # Count the occurrences of each space group
    space_group_counts = Counter(space_groups)
    
    # Calculate percentages
    total = sum(space_group_counts.values())
    space_group_percentages = {spg: (count / total) * 100 for spg, count in space_group_counts.items()}
    
    # Sort the dictionary by value (percentage) in descending order
    sorted_percentages = sorted(space_group_percentages.items(), key=lambda x: x[1], reverse=True)
    
    # Print the results
    print("Space Group Frequencies:")
    for spg, percentage in sorted_percentages:
        print(f"Space Group {spg}: {percentage:.2f}%")


if __name__ == "__main__":
    image_save_path = "/home/jsprigg/scratch/"
    #image_save_path = "/home/jsprigg/ys68/XRD_ML/data_manipulation/example_XRD_plots/"

    # Prints the data, you can also plot it by changing the plot variable
    # The plot is in a loop so be careful.
    limit = 4900         # The amount of XRD rows you want to go through
    plot = False
    looking_at_data(databs, limit, plot)

    # This function shows the frequency of each space group in the dataset.
    # analyze_space_groups(databs, max_iterations=float('inf'))

# Here is an output of analyze_space_groups() for the partial train dataset.

# Space Group Frequencies:
# Space Group 38: 25.90%
# Space Group 216: 10.30%
# Space Group 221: 7.90%
# Space Group 225: 6.40%
# Space Group 187: 4.70%
# Space Group 1: 4.30%
# Space Group 25: 3.20%
# Space Group 11: 3.10%
# Space Group 63: 2.60%
# Space Group 62: 2.40%
# Space Group 12: 2.40%
# Space Group 2: 2.20%
# Space Group 123: 2.00%
# Space Group 194: 1.90%
# Space Group 139: 1.80%
# Space Group 191: 1.60%
# Space Group 14: 1.30%
# Space Group 6: 1.10%
# Space Group 71: 1.00%
# Space Group 15: 0.90%
# Space Group 115: 0.80%
# Space Group 65: 0.70%
# Space Group 229: 0.60%
# Space Group 36: 0.60%
# Space Group 8: 0.60%
# Space Group 47: 0.60%
# Space Group 129: 0.50%
# Space Group 9: 0.50%
# Space Group 7: 0.50%
# Space Group 5: 0.40%
# Space Group 19: 0.40%
# Space Group 51: 0.40%
# Space Group 140: 0.40%
# Space Group 44: 0.30%
# Space Group 4: 0.30%
# Space Group 107: 0.30%
# Space Group 119: 0.20%
# Space Group 131: 0.20%
# Space Group 186: 0.20%
# Space Group 189: 0.20%
# Space Group 64: 0.20%
# Space Group 13: 0.20%
# Space Group 122: 0.20%
# Space Group 40: 0.20%
# Space Group 74: 0.20%
# Space Group 72: 0.20%
# Space Group 141: 0.20%
# Space Group 60: 0.20%
# Space Group 77: 0.10%
# Space Group 58: 0.10%
# Space Group 124: 0.10%
# Space Group 37: 0.10%
# Space Group 26: 0.10%
# Space Group 121: 0.10%
# Space Group 20: 0.10%
# Space Group 61: 0.10%
# Space Group 174: 0.10%
# Space Group 86: 0.10%
# Space Group 21: 0.10%
# Space Group 69: 0.10%
# Space Group 57: 0.10%
# Space Group 127: 0.10%
# Space Group 53: 0.10%
# Space Group 24: 0.10%
# Space Group 46: 0.10%
# Space Group 99: 0.10%
# Space Group 10: 0.10%
# Space Group 28: 0.10%
# Space Group 33: 0.10%
# Space Group 193: 0.10%
# Space Group 180: 0.10%
# Space Group 3: 0.10%
# Space Group 96: 0.10%
# Space Group 85: 0.10%
# Space Group 29: 0.10%