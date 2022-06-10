# D4_accessibility

D4 Accessibility Project

## Access Summarization to Zip Code Geometries

Summarization to ZCTAs
Last edited: Yesterday
Metrics to be summarized from TAZ level to ZCTA

#### Abreviation legend
    TTT = 
    TTD = 
    FF = Free Flowing traffic
    CG = Congested traffic
    EMP = 
    DU = Dwelling Units

#### SERPM jobs/housing balance
    zones: TAZs/SERPM8TAZ.shp [TAZ_REG]
        decayed:
            table: access_scores/SERPM_FF_{15 or 45}_TTD_Un_15_30_60.csv [index]
                fields: EMP_Max_15_Min_{CG or FF} /  DU_Max_15_Min_{CG or FF}
                fields: EMP_Max_30_Min_{CG or FF} /  DU_Max_30_Min_{CG or FF}
                fields: EMP_Max_45_Min_{CG or FF} /  DU_Max_45_Min_{CG or FF}
 
#### FLSWM jobs/housing balance
    zones: TAZs/2015_TAZs_Final.shp [NEWTAZ]
        decayed:
            table: access_scores/FLSWM_FF_{18 or 45}_TTD_Un_15_30_60.csv [index]
                fields: EMP_Max_15_Min_{CG or FF} /  DU_Max_15_Min_{CG or FF}
                fields: EMP_Max_30_Min_{CG or FF} /  DU_Max_30_Min_{CG or FF}
                fields: EMP_Max_45_Min_{CG or FF} /  DU_Max_45_Min_{CG or FF}

#### SERPM Cumulative opportunities (free flow and congested)
    zones: TAZs/SERPM8TAZ.shp [TAZ_REG]
        undecayed:
            table: access_scores/SERPM_FF_{15 or 45}_TTT_15_30_60.csv [index]
                field: EMP_Max_15{CG or FF}
                field: EMP_Max_30_{CG or FF}
                field: EMP_Max_60_{CG or FF}
        decayed:
            table: access_scores/SERPM_FF_{15 or 45}_TTD_Un_15_30_60.csv [index]
                field: EMP_Max_15_Min_{CG or FF}
                field: EMP_Max_30_Min_{CG or FF}
                field: EMP_Max_60_Min_{CG or FF}

#### FLSWM Cumulative opportunities (free flow and congested)
    zones: TAZs/2015_TAZs_Final.shp [NEWTAZ]        undecayed:
            table: access_scores/FLSWM_FF_{18 or 45}_TTT_15_30_60.csv [index]
                field: EMP_Max_15_{CG or FF}
                field: EMP_Max_30_{CG or FF}
                field: EMP_Max_60_{CG or FF}
        decayed:
            table: access_scores/FLSWM_FF_{18 or 45}_TTD_Un_15_30_60.csv [index]
                field: Max_15_Min_{CG or FF}
                field: Max_30_Min_{CG or FF}
                field: Max_60_Min_{CG or FF}

#### SERPM MSP
    zones: TAZs/SERPM8TAZ.shp [TAZ_REG] 
    msp table: AccessScores/SERPM_MSP_{CG or FF}_15.csv [TAZ]
    trip totals: trip_tables/SERPM_Trips_{CG or FF}_15.csv [TAZ]
        fields: {From/To}_MSP / {From/To}_Trips

#### FLSWM MSP
    zones: TAZs/2015_TAZs_Final.shp [NEWTAZ]    msp table: AccessScores/SERPM_MSP_{CG or FF}_15.csv [TAZ]
    trip totals:: trip_tables/FLSWM_Trips_{CG or FF}_18.csv [TAZ]
        fields: {From/To}_MSP / {From/To}_Trips
 
#### Proximity to transit
    best available transit service frequency
        zones: gtfs/gtfs_feeds/summarized_results/block_results_v4
            field: m1_weekday
    wtd average departure frequency
        zones: gtfs/gtfs_feeds/summarized_results/block_results_v4
            field: m5


## Getting Started
1 - Clone this repo.

2 - Create an environment with the requirements.
- open conda cmd prompt
    
```
        > cd /path/to/project_folder
        > make env
```

3 - What else?
## Project Organization
```
    ├── LICENSE
    ├── Makefile            <- Makefile with commands like `make data`
    ├── make.bat            <- Windows batch file with commands like `make data`
    ├── setup.py            <- Setup script for the library (D4_accessibility)
    ├── .env                <- Any environment variables here - created as part of project creation, 
    │                         but NOT syncronized with git repo for project.                
    ├── README.md           <- The top-level README for developers using this project.
    ├── data
    │   ├── external        <- Data from third party sources.
    │   ├── interim         <- Intermediate data that has been transformed.
    │   ├── processed       <- The final, canonical data sets for modeling.
    │   └── raw             <- The original, immutable data dump.
    ├── docs                <- A default Sphinx project; see sphinx-doc.org for details
    ├── notebooks           <- Jupyter notebooks. Naming convention is a 2 digits (for ordering),
    │   │                     descriptive name. e.g.: 01_exploratory_analysis.ipynb
    │   └── notebook_template.ipynb
    ├── references          <- Data dictionaries, manuals, and all other explanatory materials.
    ├── reports             <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures         <- Generated graphics and figures to be used in reporting
    ├── environment.yml     <- Requirements file for reproducing the analysis execution environment.
    │                         This includes far fewer dependencies and does not include arcpy.
    ├── environment_dev.yml <- Requirements file for reproducing the analysis deveopment environment.
    │                         This includes arcpy and everything needed to generate Sphinx docs.
    └── src                   <- Source code for use in this project - all scripts, modules and code.
        └── D4_accessibility  <- Library containing the bulk of code used in this 
                                                  project. 
```
