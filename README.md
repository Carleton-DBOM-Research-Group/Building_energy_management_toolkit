# Building Energy Management Toolkit
Updated May 26, 2021 - This repository contains a preliminary version of a multi-sourced, data-driven toolkit for addressing building energy deficiencies and is open-source for others to learn from, adapt, and foster into more specialised versions of multi-sourced, data-driven toolkits. At this stage, the toolkit is undergoing active development. 
Additions and revisions are expected and the repository will be updated periodically to reflect the most recent changes. Sample data is included (found in sampleData folder) and sample visuals and key performance indicators (KPIs) from the sample data are found in the "outputs" subfolder in the "toolkit" folder.  

## Downloading the toolkit
Download the contents of the repository.
Ensure the folder titled "toolkit" contains nine .py files and the subfolders titled "outputs" and "reports" with its subfolders are included. 
> metadata.py
> energyBaseline.py
> ahuAnomaly.py
> zoneAnomaly.py
> endUseDisaggregation.py
> occupancy.py
> complaintsAnalytics.py
> generate_report.py
> exe.py
> outputs
> reports

## Getting started
Download and install Anaconda:
> https://www.anaconda.com/products/individual

Create a virtual environment and install the required packages using the included requirements.txt file.
In command prompt, navigate to the directory containing the *requirements.txt* file with the following command line:
> *cd C:\Users...\directory_with_requirements_txt_file*

Run the following command line to set up a virtual environment named "newEnviro" with the required packages:
>*conda env create -f requirements.txt newEnviro*

Activate the virtual environment you just created by running the command:
> *conda activate newEnviro*

Navigate to the directory titled "toolkit":
> *cd C:\Users...\toolkit*
> 
Run the exe file:
> *python exe.py*

## Sample data, visuals, and reports
Sample data is provided in the folder titled "sampleData" and sample visualizations from sample data are included in 
the subfolder titled "outputs" within the "toolkit" folder. Sample reports are also included in the subfolder titled 
"reports."

## Editing the toolkit
The authors encourage community-driven efforts to improve and modify the toolkit. Refining the functions should not be limited to improving reliability but also to improve robustness. Derivations of multi-sourced toolkits incorporating additional, reduced, or altered functions to suit a particular set of buildings, or even establish explicit interdependencies between functions, are also encouraged. The toolkit is intended to act as a framework to initiate such efforts.

## Reference documentation
This section will be updated as soon as the reference documentation is available. 
