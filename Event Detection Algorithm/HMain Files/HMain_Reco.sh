echo "Running HMain_NMin_FHR_FE.sh Script"

# Set the working directory to the directory of this script
cd /project/antares/lrootsel/montecarlo

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Print the working directory
echo "Working directory = " 
pwd
echo ""

# Set the path to the configuration file
configFilePath=/project/antares/lrootsel/montecarlo/config.ini
dataFilePath=/project/antares/lrootsel/montecarlo/data.pkl

# Add directory containing HClasses module to Python path
export PYTHONPATH=$PYTHONPATH:/project/antares/lrootsel/montecarlo

# Set the path to the Python script
pythonScriptPath=/project/antares/lrootsel/montecarlo/HMain_Reco.py

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Run the Python script with the configuration file
python HMain_Reco_1.py "$configFilePath"

source /project/antares/public_student_software_new/env_scripts/env_python-v3.7.5_root-v6.22.06_jpp-v18.0.0_aanet-v2.4.0.sh

python HMain_Reco_2.py "$dataFilePath"

echo "Finished Running HMain_Reco.sh Script"