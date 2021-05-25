# Project Name
Building Energy Management Toolkit (updated Feb 22, 2021)

## Downloading the toolkit
Download the contents of the repository.
Enesure the folder titled "toolkit" contains nine .py files and the folders titled, "outputs" and "reports" with its subfolders. 
> metadata.py /n
> energyBaseline.py \n
> ahuAnomaly.py
> zoneAnomaly.py
> endUseDisaggregation.py
> occupancy.py
> complaintsAnalytics.py
> outputs
> reports

## Running the toolkit
Download and install Anaconda:
> https://www.anaconda.com/products/individual

Create a virtual environment and install the required packages using the included requirements.txt file
In command prompt, navigate to the directory containing the *requirements.txt* file with the following command line:
> *cd C:\Users...\directory_with_file*

Run the following command line to set up a virtual environment named "newEnviro" with the required packages:
>*conda env create -f requirements.txt newEnviro*

Activate the virtual enviornment you just created by running the command:
> *conda activate newEnviro*

Navigate to the directory titled "toolkit":
> *cd C:\Users...\toolkit*
> 
Run the exe file:
> *python exe.py*
