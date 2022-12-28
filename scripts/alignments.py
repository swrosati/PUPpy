# Load libraries
import subprocess
import sys
import pandas as pd
import argparse
from colorama import init
from colorama import Fore, Style
import glob, os

######################################################## flags ###########################################################################

parser = argparse.ArgumentParser(
    prog='PROG',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='''
    PUPpy: A Phylogenetically Unique Primer pipeline in PYthon for high resolution classification of defined microbial communities
    ''')

# Setting up flags in python
parser.add_argument("-c", "--CDS_folder", help="Directory containing the defined community CDS files to perform multiple sequence alignment on", required=True)
parser.add_argument("-o", "--out_folder", help="Relative path to the output folder.", default="MSAoutput")
parser.add_argument("-i", "--identity", help="Identity threshold to report multiple sequence alignments by MMseqs2.", default=0.3, type=float)

args = parser.parse_args()


######################################################## variables ###########################################################################

# Path to folder with CDS files
cds = os.path.abspath(args.CDS_folder)
# Path to output directory
output = os.path.abspath(args.out_folder)
# Path to CDS filenames with .fna extension
cds_filenames = os.path.join(cds, "*.fna")

# Check if output folder exists. If it does, exit the program, otherwise create it.
if os.path.exists(output):
    print(Fore.YELLOW + 'Output folder ({}) already exists. Any existing outputs will be overwritten.'.format(args.out_folder) + Style.RESET_ALL)
else:
    os.mkdir(output)

######################################################## Functions ###########################################################################

def rename_fasta(f, species_name):
    """
    Function to modify all the FASTA headers in each input CDS file.
    """
    with open(f,'r') as f1:
        data = f1.readlines()
        new_lines = rename_fasta_headers(data, species_name)

    with open(f, 'w') as f2:
        f2.writelines(new_lines)

def rename_fasta_headers(list_of_lines, species_name):
    """
    Function to select FASTA header lines to which apply name changes
    """
    # run for loop to parse every line and change the headers
    new_lines = []
    for line in list_of_lines:
        if line.startswith(">"):
            new_lines.append(change_header(line, species_name))
        else:
            new_lines.append(line)
    return(new_lines)


def change_header(line, name):
    """
    Function to rename FASTA headers to include species name.
    """
    # find the | in the string
    if "|" in line:
        pipe_index = line.index("|") + 1
    else:
        pipe_index = 1

    #add the species name to the string
    if name in line:
        return(line)
    elif "|" not in line:
        header_name = line[pipe_index:]
        separator_index = header_name.index("_")
        New_line = ">lcl|" + name + "-" + header_name[:separator_index] + "_cds" + header_name[separator_index:]
        return(New_line)
    else:
        New_line = ">lcl|" + name + "-" + line[pipe_index:]
        return(New_line)

##################################################### RENAME FASTA HEADERS #################################################################


# Rename FASTA headers
for f in glob.glob(cds_filenames):
    name = os.path.basename(f)
    i = name.index("_cds")
    rename_fasta(f, name[:i])


##################################################### Alignments with MMseqs2 #################################################################

subprocess.run(['chmod', '755', './MMseqs2.sh'])
subprocess.check_call(['./MMseqs2.sh', output, cds, str(args.identity)])

print(Fore.GREEN + 'Done!' + Style.RESET_ALL)