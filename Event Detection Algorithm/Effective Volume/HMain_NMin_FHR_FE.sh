echo "Running HMain_NMin_FHR_FE.sh Script"

# Set the working directory to the directory of this script
cd /project/antares/lrootsel/effective_volume

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Print the working directory
echo "Working directory = " 
pwd
echo ""

# Set the path to the configuration file
configFilePath=/project/antares/lrootsel/montecarlo/config.ini

# Add directory containing HClasses module to Python path
export PYTHONPATH=$PYTHONPATH:/project/antares/lrootsel/effective_volume

# Set the path to the Python script
pythonScriptPath=/project/antares/lrootsel/effective_volume/HMain_NMin_FHR_FE.py

source /project/antares/lrootsel/montecarlo/Thoth/bin/activate

# Run the Python script with the configuration file
python HMain_NMin_FHR_FE.py "$configFilePath"


echo "Finished Running HMain_NMin_FHR_FE.sh Script"