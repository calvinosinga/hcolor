#!/bin/bash

#SBATCH --share
#SBATCH --job-name=benhi_pk
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=benhi_pk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
gunzip /lustre/cosinga/final_fields/benhi_99.0.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.1.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.1.hdf5 benhi_99.1_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.1.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.2.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.2.hdf5 benhi_99.2_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.2.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.3.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.4.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.5.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.6.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.7.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
gunzip /lustre/cosinga/final_fields/benhi_99.8.hdf5.gz
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py benhi_99.0.hdf5 benhi_99.0_pk.txt
python /lustre/cosinga/final_fields/compress.py benhi_99.0.hdf5
