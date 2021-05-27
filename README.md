# Building Energy Management Toolkit
Updated May 27, 2021 - This repository contains a preliminary version of a multi-sourced, data-driven toolkit for addressing building energy deficiencies and is open-source for others to learn from, adapt, and foster into more specialised versions of multi-sourced, data-driven toolkits. At this stage, the toolkit is undergoing active development. 
Additions and revisions are expected and the repository will be updated periodically to reflect the most recent changes. Sample data are included (found in sampleData folder) and sample visuals and key performance indicators (KPIs) from the sample data are found in the "outputs" subfolder in the "toolkit" folder.  

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
1. Download and install Anaconda:
> https://www.anaconda.com/products/individual

2. Set the path to the location where Anaconda was installed.
> Press the windows key --> type *environment* --> select *Environmental Variables* --> Select the *path* variable and select *Edit* --> *Add* the directories where Anaconda is installed. These should be C:\Users\*Username*\anaconda3 and C:\Users\*Username*\anaconda3\Library\bin

3. Create a virtual environment and install the required packages.
In command prompt, create a new virtual environment and call it "newEnv" with the following command line:
> *conda create -n newEnv python=3.8 anaconda*

4. Activate the new virtual environment:
>*conda activate newEnv*

5. Install the following required packages using *pip*:
>*pip install geneticalgorithm*

>*pip install editdistance*

>*pip install ruptures*

>*pip install python-docx*

6. Navigate to the directory titled "toolkit":
> *cd C:\Users\...\toolkit*
> 
7. Run the exe.py file:
> *python exe.py*

## Using the toolkit
To be updated...

## Sample data, visuals, and reports
Sample data are provided in the folder titled "sampleData" and sample visualizations from sample data are included in 
the subfolder titled "outputs" within the "toolkit" folder. Sample reports are also included in the subfolder titled 
"reports."

## Editing the toolkit
The authors encourage community-driven efforts to improve and modify the toolkit. Refining the functions should not be limited to improving reliability but also to improve robustness. Derivations of multi-sourced toolkits incorporating additional, reduced, or altered functions to suit a particular set of buildings, or even establish explicit interdependencies between functions, are also encouraged. The toolkit is intended to act as a framework to initiate such efforts.

## Reference documentation
### Framework of the toolkit
This section will be updated when the reference documentation is available

### Metadata inferencing function (*metadata.py*)
> Chen et al., "A Metadata Inference Method for Building Automation Systems With Limited Semantic Information," 2020.
> https://doi.org/10.1109/TASE.2020.2990566

### Baseline energy function (*energyBaseline.py*)
Gunay et al., "Detection and interpretation of anomalies in building energy use through inverse modeling," 2019.
> https://doi.org/10.1080/23744731.2019.1565550
Afroz et al., "An inquiry into the capabilities of baseline building energy modelling approaches to estimate energy savings," 2021.
> https://doi.org/10.1016/j.enbuild.2021.111054

### AHU anomaly detection function (*ahuAnomaly.py*)
Gunay and Shi, "Cluster analysis-based anomaly detection in building automation systems," 2020.
> https://doi.org/10.1016/j.enbuild.2020.110445
Darwazeh et al., "Development of Inverse Greybox Model-Based Virtual Meters for Air Handling Units," 2021.
> https://doi.org/10.1109/TASE.2020.3005888

### Zone anomaly detection function (*zoneAnomaly.py*)
Gunay and Shi, "Cluster analysis-based anomaly detection in building automation systems," 2020.
> https://doi.org/10.1016/j.enbuild.2020.110445

### End-use disaggregation function (*endUseDisaggregation.py*)
Gunay et al., "Disaggregation of commercial building end-uses with automation system data," 2020.
> https://doi.org/10.1016/j.enbuild.2020.110222
Darwazeh et al., "Virtual metering of heat supplied by hydronic perimeter heaters in variable air volume zones," 2020.
> https://doi.org/10.1145/3427771.3429389


