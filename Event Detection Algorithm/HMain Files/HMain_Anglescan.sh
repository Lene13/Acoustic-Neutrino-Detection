echo "Running HMain_Anglescan.sh Script"

# Set the working directory to the directory of this script
cd /project/antares/lrootsel/montecarlo

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Print the working directory
echo "Working directory = " 
pwd
echo ""

# Set the path to the configuration file
configFilePath=/project/antares/lrootsel/montecarlo/config.ini

# Add directory containing HClasses module to Python path
export PYTHONPATH=$PYTHONPATH:/project/antares/lrootsel/montecarlo

# Set the path to the Python script
pythonScriptPath=/project/antares/lrootsel/montecarlo/HMain_Anglescan.py

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Run the Python script with the configuration file
python HMain_Anglescan.py "$configFilePath"


echo "Finished Running HMain_Anglescan.sh Script"