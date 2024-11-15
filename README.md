# VirtualTool_CoRe
This repository is for the final project, the virtual tool game, for the PKU course Cognitive Reasoning.

## Installing Description

First, set up the conda environment

```bash
conda create -n virtool python=3.7
conda activate virtool
```

Then, install required packages

```bash
# These packages are required for the tool-games
pip install pygame PyExecJS numpy scipy jupyter
pip install pymunk==5.7.0

# Register the tool-games
cd ./tool-games/environment/
python setup.py build
cd -

```

You also need to install nodejs to run the default task display. You can check if nodejs is installed by:

```bash
# Check it
node -v

# If not installed, install it
sudo apt-get install nodejs npm
```

By now, you should be able to run the default task display by:

```bash
cd ./tool-games/environment/
python make_basic_trial.py
```

Due to pymunk's change, 'pm.Vec2d()' only receives two arguments instead of one. All such thing should be changed before running the code.
