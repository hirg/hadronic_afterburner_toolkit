#!/usr/bin/env python

import sys
from os import path, mkdir
import shutil
from glob import glob
import subprocess
import random

def generate_script(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '10:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir UrQMD_results
for iev in `ls OSCAR_events`
do
    cd osc2u
    ./osc2u.e < ../OSCAR_events/$iev
    mv fort.14 ../urqmd/OSCAR.input
    cd ../urqmd
    ./runqmd.sh
    mv particle_list.dat ../UrQMD_results/particle_list_`echo $iev | cut -f 2 -d _`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_JAM(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '10:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell


export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/scratch/irulan/chun/JAM/JAM_lib/lib
mkdir JAM_results
for iev in `ls OSCAR_events`
do
    eventid=`echo $iev | cut -f 2 -d "_" | cut -f 1 -d "."`
    cd JAM
    mv ../OSCAR_events/$iev ./OSCAR.DAT
    rm -fr phase.dat
    ./jamgo
    mv phase.dat ../JAM_results/particle_list_$eventid.dat
    mv OSCAR.DAT ../OSCAR_events/OSCAR_$eventid.dat
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_iSS(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '35:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l
#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell


mkdir UrQMD_results
for iev in `ls hydro_events --color=none | grep "surface"`
do
    event_id=`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd iSS
    if [ -d "results" ]; then
        rm -fr results
    fi
    mkdir results
    mv ../hydro_events/$iev results/surface.dat
    cp ../hydro_events/music_input_event_$event_id results/music_input
    ./iSS.e >> ../output.log
    mv results/surface.dat ../hydro_events/$iev
    cd ../osc2u
    ./osc2u.e < ../iSS/OSCAR.DAT >> ../output.log
    mv fort.14 ../urqmd/OSCAR.input
    cd ../urqmd
    ./runqmd.sh >> ../output.log
    mv particle_list.dat ../UrQMD_results/particle_list_$event_id.dat
    #mv ../iSS/OSCAR.DAT ../UrQMD_results/OSCAR_$event_id.dat
    rm -fr ../iSS/OSCAR.DAT
    rm -fr OSCAR.input
    cd ..
done
""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_HBT(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '20:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir HBT_results
for iev in `ls UrQMD_events | grep "particle_list"`
do
    eventid=`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../UrQMD_events/$iev results/particle_list.dat
    mv ../UrQMD_events/mixed_event_$eventid.dat results/particle_list_mixed_event.dat
    ./hadronic_afterburner_tools.e read_in_mode=1 run_mode=1 > output.log
    mv results/particle_list.dat ../UrQMD_events/$iev
    mv results/particle_list_mixed_event.dat ../UrQMD_events/mixed_event_$eventid.dat
    mv results ../HBT_results/event_$eventid
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_HBT_with_JAM(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '30:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir HBT_results
for iev in `ls JAM_events | grep "particle_list"`
do
    eventid=`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../JAM_events/$iev results/particle_list.dat
    mv ../JAM_events/mixed_event_$eventid.dat results/particle_list_mixed_event.dat
    ./hadronic_afterburner_tools.e run_mode=1 read_in_mode=5 > output.log
    mv results/particle_list.dat ../JAM_events/$iev
    mv results/particle_list_mixed_event.dat ../JAM_events/mixed_event_$eventid.dat
    mv results ../HBT_results/event_$eventid
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()

def generate_script_spectra_and_vn(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '1:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir spvn_results
for iev in `ls UrQMD_events | grep "particle_list"`
do
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../UrQMD_events/$iev results/particle_list.dat

    # pi+, pi-
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-211 distinguish_isospin=1 rap_type=1 >> output.log
    # K+, K-
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-321 distinguish_isospin=1 rap_type=1 >> output.log
    # protons and anti-protons
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-2212 distinguish_isospin=1 rap_type=1 >> output.log
    # Lambda and anti-Lambda
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3122 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3122 distinguish_isospin=1 rap_type=1 >> output.log
    # Xi- and anti-Xi+
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3312 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3312 distinguish_isospin=1 rap_type=1 >> output.log
    # Omega and anti Omega
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=3334 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-3334 distinguish_isospin=1 rap_type=1 >> output.log
    # phi(1020)
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=333 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=333 distinguish_isospin=1 rap_type=1 >> output.log
    # all positive charged hadrons
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9998 distinguish_isospin=0 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9998 distinguish_isospin=0 rap_type=0 rap_min=-1.0 rap_max=1.0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9998 distinguish_isospin=0 rap_type=0 rap_min=-2.5 rap_max=-0.5 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9998 distinguish_isospin=0 rap_type=0 rap_min=0.5 rap_max=2.5 >> output.log
    # all negative charged hadrons
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-9998 distinguish_isospin=0 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-9998 distinguish_isospin=0 rap_type=0 rap_min=-1.0 rap_max=1.0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-9998 distinguish_isospin=0 rap_type=0 rap_min=-2.5 rap_max=-0.5 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=-9998 distinguish_isospin=0 rap_type=0 rap_min=0.5 rap_max=2.5 >> output.log
    # charged hadrons
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9999 distinguish_isospin=0 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9999 distinguish_isospin=0 rap_type=0 rap_min=-1.0 rap_max=1.0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9999 distinguish_isospin=0 rap_type=0 rap_min=-2.5 rap_max=-0.5 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 particle_monval=9999 distinguish_isospin=0 rap_type=0 rap_min=0.5 rap_max=2.5 >> output.log

    mv results/particle_list.dat ../UrQMD_events/$iev
    mv results ../spvn_results/event_`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_particle_yield_distribution(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '1:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir spvn_results
for iev in `ls UrQMD_events | grep "particle_list"`
do
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../UrQMD_events/$iev results/particle_list.dat

    # pi+, pi-, and net charged pi
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # K+, K-, ant net charged K
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-321 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # protons, anti-protons, and net protons
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # Lambda, anti-Lambda, and net Lambda
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3122 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # Xi- and anti-Xi+
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3312 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3312 distinguish_isospin=1 rap_type=1 >> output.log
    # Omega and anti Omega
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=3334 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-3334 distinguish_isospin=1 rap_type=1 >> output.log
    # phi(1020)
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=333 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=333 distinguish_isospin=1 rap_type=1 >> output.log
    # all baryon
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=9997 distinguish_isospin=0 rap_type=0 >> output.log
    # all anti-baryon
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-9997 distinguish_isospin=0 rap_type=0 >> output.log
    # net baryon
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=9997 distinguish_isospin=0 rap_type=0 net_particle_flag=1 >> output.log
    # all positive charged hadrons
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=9998 distinguish_isospin=0 rap_type=0 >> output.log
    # all negative charged hadrons
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=-9998 distinguish_isospin=0 rap_type=0 >> output.log
    # net charged hadrons
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=9998 distinguish_isospin=0 rap_type=0 net_particle_flag=1 >> output.log
    # charged hadrons
    ./hadronic_afterburner_tools.e run_mode=2 particle_monval=9999 distinguish_isospin=0 rap_type=0 >> output.log

    mv results/particle_list.dat ../UrQMD_events/$iev
    mv results ../spvn_results/event_`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_particle_yield_distribution_with_OSCAR(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '1:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir spvn_results
for iev in `ls OSCAR_events`
do
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../OSCAR_events/$iev results/OSCAR.DAT

    # themal pi+, pi-, net charged pi
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=211 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # thermal K+, K-, and net charged K
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=321 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # thermal protons, anti-protons, and net protons
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=2212 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # thermal Lambda, anti-Lambda, andn net Lambda
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3122 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3122 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=0 net_particle_flag=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3122 distinguish_isospin=1 rap_type=1 net_particle_flag=1 >> output.log
    # thermal Xi- and anti-Xi+
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3312 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3312 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3312 distinguish_isospin=1 rap_type=1 >> output.log
    # thermal Omega and anti Omega
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=3334 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3334 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=-3334 distinguish_isospin=1 rap_type=1 >> output.log
    # thermal phi(1020)
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=333 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=2 particle_monval=333 distinguish_isospin=1 rap_type=1 >> output.log

    mv results/OSCAR.DAT ../OSCAR_events/$iev
    mv results ../spvn_results/event_`echo $iev | cut -f 2 -d _ | cut -f 1 -d .`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_spectra_and_vn_with_JAM(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '10:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir spvn_results
for iev in `ls JAM_events | grep "particle_list"`
do
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../JAM_events/$iev results/particle_list.dat
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-211 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-211 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-321 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-321 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-2212 distinguish_isospin=1 rap_type=0 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=-2212 distinguish_isospin=1 rap_type=1 >> output.log
    ./hadronic_afterburner_tools.e run_mode=0 read_in_mode=5 particle_monval=9999 distinguish_isospin=0 rap_type=0 >> output.log
    mv results/particle_list.dat ../JAM_events/$iev
    mv results ../spvn_results/event_`echo $iev | cut -f 3 -d _ | cut -f 1 -d .`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def generate_script_HBT_with_OSCAR(folder_name):
    working_folder = path.join(path.abspath('./'), folder_name)
    walltime = '10:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    script.write(
"""#!/bin/bash -l

#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J UrQMD_%s
#SBATCH -t %s
#SBATCH -L SCRATCH
#SBATCH -C haswell

mkdir HBT_results
for iev in `ls OSCAR_events`
do
    cd hadronic_afterburner_toolkit
    rm -fr results
    mkdir results
    mv ../OSCAR_events/$iev results/OSCAR.DAT
    ./hadronic_afterburner_tools.e read_in_mode=0 run_mode=1 > output.log
    mv results/OSCAR.DAT ../OSCAR_events/$iev
    mv results ../HBT_results/event_`echo $iev | cut -f 2 -d _ | cut -f 1 -d .`
    cd ..
done

""" % (working_folder.split('/')[-1], walltime))
    script.close()


def copy_UrQMD_events(number_of_cores, input_folder, working_folder):
    events_list = glob('%s/particle_list_*.dat' % input_folder)
    if events_list == []:
        events_list = glob('%s/particle_list_*.gz' % input_folder)
        if events_list == []:
            print("Error: can not find UrQMD events, events_list is empty! ",
                  events_list)
        else:
            print("Linking zipped binary UrQMD events, ",
                  "make sure read_in_mode is set to 2~")

    for iev in range(len(events_list)):
        folder_id = iev % number_of_cores
        filename = events_list[iev].split('/')[-1].split('.')[0]
        event_id = filename.split('_')[-1]
        folder_path = path.join(working_folder, 'event_%d' % folder_id, 
                                'UrQMD_events', '%s.dat' % filename)
        bashCommand = "ln -s %s %s" % (
            path.abspath(events_list[iev]), folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)
        mixed_id = random.randint(0, len(events_list)-1)
        filename_mixed = events_list[mixed_id].split('/')[-1].split('.')[0]
        mixed_event_id = filename_mixed.split('_')[-1]
        while (mixed_event_id == iev):
            mixed_id = random.randint(0, len(events_list)-1)
            filename_mixed = events_list[mixed_id].split('/')[-1].split('.')[0]
            mixed_event_id = filename_mixed.split('_')[-1]
        folder_path = path.join(
            working_folder, 'event_%d' % folder_id, 
            'UrQMD_events', 'mixed_event_%s.dat' % event_id)
        bashCommand = "ln -s %s %s" % (
            path.abspath(events_list[mixed_id]), folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)


def copy_JAM_events(number_of_cores, input_folder, working_folder):
    events_list = glob('%s/particle_list_*.dat' % input_folder)
    for iev in range(len(events_list)):
        folder_id = iev % number_of_cores
        filename = events_list[iev].split('/')[-1].split('.')[0]
        event_id = filename.split('_')[-1]
        folder_path = path.join(working_folder, 'event_%d' % folder_id, 
                                'JAM_events', '%s.dat' % filename)
        bashCommand = "ln -s %s %s" % (
            path.abspath(events_list[iev]), folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)
        mixed_id = random.randint(0, len(events_list)-1)
        filename_mixed = events_list[mixed_id].split('/')[-1].split('.')[0]
        mixed_event_id = filename_mixed.split('_')[-1]
        while (mixed_event_id == iev):
            mixed_id = random.randint(0, len(events_list)-1)
            filename_mixed = events_list[mixed_id].split('/')[-1].split('.')[0]
            mixed_event_id = filename_mixed.split('_')[-1]
        folder_path = path.join(working_folder, 'event_%d' % folder_id, 
                                'JAM_events', 'mixed_event_%s.dat' % event_id)
        bashCommand = "ln -s %s %s" % (path.abspath(events_list[mixed_id]),
                                       folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)


def generate_event_folder_UrQMD(working_folder, event_id, mode):
    event_folder = path.join(working_folder, 'event_%d' % event_id)
    mkdir(event_folder)

    if mode == 2:
        # calculate HBT correlation with OSCAR outputs
        mkdir(path.join(event_folder, 'OSCAR_events'))
        generate_script_HBT_with_OSCAR(event_folder)
    elif mode == 3:
        # calculate HBT correlation with UrQMD outputs
        mkdir(path.join(event_folder, 'UrQMD_events'))
        generate_script_HBT(event_folder)
    elif mode == 4:
        # calculate HBT correlation with UrQMD outputs
        mkdir(path.join(event_folder, 'UrQMD_events'))
        generate_script_spectra_and_vn(event_folder)
    elif mode == 8:
        # collect event-by-event particle distribution
        mkdir(path.join(event_folder, 'UrQMD_events'))
        generate_script_particle_yield_distribution(event_folder)
    elif mode == 9:
        # calculate event-by-event particle distribution with OSCAR outputs
        mkdir(path.join(event_folder, 'OSCAR_events'))
        generate_script_particle_yield_distribution_with_OSCAR(event_folder)


    shutil.copytree('codes/hadronic_afterburner_toolkit', 
                    path.join(path.abspath(event_folder), 
                    'hadronic_afterburner_toolkit'))


def generate_event_folder_JAM(working_folder, event_id, mode):
    event_folder = path.join(working_folder, 'event_%d' % event_id)
    mkdir(event_folder)

    if mode == 5:
        # run JAM with OSCAR files
        mkdir(path.join(event_folder, 'OSCAR_events'))
        generate_script_JAM(event_folder)
        shutil.copytree('codes/JAM', 
                        path.join(path.abspath(event_folder), 'JAM'))
    elif mode == 6:
        # collect particle spectra and vn with JAM outputs
        mkdir(path.join(event_folder, 'JAM_events'))
        generate_script_spectra_and_vn_with_JAM(event_folder)
        shutil.copytree('codes/hadronic_afterburner_toolkit', 
                        path.join(path.abspath(event_folder), 
                        'hadronic_afterburner_toolkit'))
    elif mode == 7:
        # calculate HBT correlation with JAM outputs
        mkdir(path.join(event_folder, 'JAM_events'))
        generate_script_HBT_with_JAM(event_folder)
        shutil.copytree('codes/hadronic_afterburner_toolkit', 
                        path.join(path.abspath(event_folder), 
                        'hadronic_afterburner_toolkit'))


def generate_event_folder(working_folder, event_id):
    event_folder = path.join(working_folder, 'event_%d' % event_id)
    mkdir(event_folder)
    mkdir(path.join(event_folder, 'OSCAR_events'))
    generate_script(event_folder)
    shutil.copytree('codes/osc2u', 
                    path.join(path.abspath(event_folder), 'osc2u'))
    shutil.copytree('codes/urqmd', 
                    path.join(path.abspath(event_folder), 'urqmd'))

def copy_OSCAR_events(number_of_cores, input_folder, working_folder):
    events_list = glob('%s/*.dat' % input_folder)
    for iev in range(len(events_list)):
        folder_id = iev % number_of_cores
        folder_path = path.join(
            working_folder, 'event_%d' % folder_id, 
            'OSCAR_events', events_list[iev].split('/')[-1])
        bashCommand = "ln -s %s %s" % (
            path.abspath(events_list[iev]), folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)


def generate_event_folder_iSS(working_folder, event_id):
    event_folder = path.join(working_folder, 'event_%d' % event_id)
    mkdir(event_folder)
    mkdir(path.join(event_folder, 'hydro_events'))
    generate_script_iSS(event_folder)
    shutil.copytree('codes/iSS', 
                    path.join(path.abspath(event_folder), 'iSS'))
    shutil.copytree('codes/osc2u', 
                    path.join(path.abspath(event_folder), 'osc2u'))
    shutil.copytree('codes/urqmd', 
                    path.join(path.abspath(event_folder), 'urqmd'))

def copy_hydro_events(number_of_cores, input_folder, working_folder):
    events_list = glob('%s/surface*.dat' % input_folder)
    for iev in range(len(events_list)):
        event_id = events_list[iev].split('/')[-1].split('_')[-1].split('.')[0]
        folder_id = iev % number_of_cores
        working_path = path.join(working_folder, 'event_%d' % folder_id,
                                 'hydro_events')
        folder_path = path.join(working_path, events_list[iev].split('/')[-1])
        bashCommand = "ln -s %s %s" % (
            path.abspath(events_list[iev]), folder_path)
        subprocess.Popen(bashCommand, stdout = subprocess.PIPE, shell=True)
        shutil.copy(path.join(input_folder, 
                              'music_input_event_%s' % event_id), 
                    working_path)


if __name__ == "__main__":
    try:
        from_folder = str(sys.argv[1])
        folder_name = str(sys.argv[2])
        ncore = int(sys.argv[3])
        mode = int(sys.argv[4])
    except IndexError:
        print("%s input_folder working_folder num_of_cores mode"
              % str(sys.argv[0]))
        exit(0)

    if mode == 0:   # run iSS + osc2u + UrQMD from hydro hypersurface
        for icore in range(ncore):
            generate_event_folder_iSS(folder_name, icore)
        copy_hydro_events(ncore, from_folder, folder_name)
    elif mode == 1:   # run UrQMD with OSCAR events
        for icore in range(ncore):
            generate_event_folder(folder_name, icore)
        copy_OSCAR_events(ncore, from_folder, folder_name)
    elif mode == 2:   # calculate HBT correlation with OSCAR events
        for icore in range(ncore):
            generate_event_folder_UrQMD(folder_name, icore, mode)
        copy_OSCAR_events(ncore, from_folder, folder_name)
    elif mode == 3:   # calculate HBT correlation with UrQMD events
        for icore in range(ncore):
            generate_event_folder_UrQMD(folder_name, icore, mode)
        copy_UrQMD_events(ncore, from_folder, folder_name)
    elif mode == 4:   # collect spectra and flow observables from UrQMD events
        for icore in range(ncore):
            generate_event_folder_UrQMD(folder_name, icore, mode)
        copy_UrQMD_events(ncore, from_folder, folder_name)
    elif mode == 5:   # run JAM with OSCAR events
        for icore in range(ncore):
            generate_event_folder_JAM(folder_name, icore, mode)
        copy_OSCAR_events(ncore, from_folder, folder_name)
    elif mode == 6:   # collect spectra and vn with JAM events
        for icore in range(ncore):
            generate_event_folder_JAM(folder_name, icore, mode)
        copy_JAM_events(ncore, from_folder, folder_name)
    elif mode == 7:   # calculate HBT correlation with JAM events
        for icore in range(ncore):
            generate_event_folder_JAM(folder_name, icore, mode)
        copy_JAM_events(ncore, from_folder, folder_name)
    elif mode == 8:  # collect particle yield distribution with UrQMD events
        for icore in range(ncore):
            generate_event_folder_UrQMD(folder_name, icore, mode)
        copy_UrQMD_events(ncore, from_folder, folder_name)
    elif mode == 9:  # collect particle yield distribution with OSCAR events
        for icore in range(ncore):
            generate_event_folder_UrQMD(folder_name, icore, mode)
        copy_OSCAR_events(ncore, from_folder, folder_name)

