# VirtualTool_CoRe
This repository is for the final project, the virtual tool game, for the PKU course Cognitive Reasoning.

## Setting Up

### Installing Description

First, set up the conda environment

```bash
conda create -n virtool python=3.7
conda activate virtool
```

Then, install required packages

```bash
# These packages are required for the tool-games
pip install -r requirements.txt

# Register the tool-games
cd ./tool-games/environment/
pip install -e .  
```
<!-- Note! 'pip install -e .' will create a soft link to the tool-games package, so you can modify the tool-games package and the changes will be reflected in the environment. And also, after you install it, you won't need to put the file into the environment. -->

### Issues

1. tool-games is a submodule. You need to clone the submodule by:
    ```bash
    git submodule init
    git submodule update
    ```
    If you encounter error with the submodule, you can try : 【ToDo】
2. You also need to install nodejs to run the default task display. You can check if nodejs is installed by:
    ```bash
    # Check it
    node -v

    # If not installed, install it
    sudo apt-get install nodejs npm
    ```
3. The version of pymunk is strict. You need to install 5.7.0 to run the tool-games. Check if you have the correct version if you encouter error with Vec2d.
4. If you encounter `execjs._exceptions.ProgramError: Error: Cannot find module 'PhysicsGaming'`, modify line 184 in file `tool-games\environment\pyGameWorld\toolpicker_js.py` as `self._ctx = execjs.compile(ctxstr, cwd=os.path.dirname(__file__))`
5. 