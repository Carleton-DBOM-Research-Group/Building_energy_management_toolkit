# Project Name
Building Energy Management Toolkit

## Downloading the toolkit
Download the seven functions and the folders titled, "outputs" and "reports" with the containing subfolders. 
Ensure they are located all located in the same directory
> metadata.py
> energyBaseline.py
> ahuAnomaly.py
> zoneAnomaly.py
> endUseDisaggregation.py
> occupancy.py
> complaintsAnalytics.py
> outputs
> reports

Download the *requirements.txt* file. This is required to run the functions.
> requirement.txt

## Downloading the sample data
Download the sample data. These do not need to be in the same directory as the functions.
> sampleData

## Running the toolkit
Download and install Anaconda:
> https://www.anaconda.com/products/individual

Create a virtual environment and install required packages
In command prompt, navigate to the directory containing the *requirements.txt* file and run the following:
> *cd C:\Users...\BEMToolkit*

Run the following command to set up a virtual environment:
>*conda env create -f requirements.txt newEnviro*

Activate the virtual enviornment you just created by running the command:
> *conda activate newEnviro*

Run the exe file:
> *python exe.py*
