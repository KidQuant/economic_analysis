#%%

import pandas as pd
import numpy as np
import scipy
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas_datareader.data as web

import warnings
warnings.filterwarnings('ignore', message='optional dependency requests_cache*', category=RuntimeWarning)
import pandasdmx as sdmx

from datetime import date

# %%

report_start
report_end = date.today()

# %%

MEAN_LEVEL_OF = 'Mean level of '
PARTICIPATION_RATE = 'Participation Rate'
MEAN_PARTICIPATION_RATE = MEAN_LEVEL_OF + PARTICIPATION_RATE
EMPLOYMENT_POPULATION_RATE = 'Employment Rate'
MEAN_EMPLOYMENT_POPULATION_RATE = MEAN_LEVEL_OF + EMPLOYMENT_POPULATION_RATE
UNEMPLOYMENT_RATE = 'Unemployment Rate'
MEAN_UNEMPLOYMENT_RATE = MEAN_LEVEL_OF + UNEMPLOYMENT_RATE
UNFILLED_VACANCIES_POPULATION_RATE = 'Unfilled Vacancies/Population Rate'
MEAN_UNFILLED_VACANCIES_POPULATION_RATE = MEAN_LEVEL_OF + UNFILLED_VACANCIES_POPULATION_RATE
UNFILLED_VACANCIES_LABOR_FORCE_RATE = 'Job-vacancy Rate'
MEAN_UNFILLED_VACANCIES_LABOR_FORCE_RATE = MEAN_LEVEL_OF + UNFILLED_VACANCIES_LABOR_FORCE_RATE
UNEMPLOYMENT_RATIOS_GRAPH_TITLE = 'US Participation, Employment/Population, Unemployment, and Unfilled Vacancies/Population Rates'
UNEMPLOYMENT_RATIOS_SUBSET_1_GRAPH_TITLE = 'US Participation and Employment Rates'
UNEMPLOYMENT_RATIOS_SUBSET_2_GRAPH_TITLE = 'US Unemployment, Unfilled Vacancies/Population and Unfilled Vacancies/Labor Force Rates'
UNEMPLOYMENT_RATIOS_SUBSET_2_1_GRAPH_TITLE = 'US Unemployment Rate'
UNEMPLOYMENT_RATIOS_SUBSET_3_GRAPH_TITLE = 'US Unfilled Vacancies/Population and Unfilled Vacancies/Labor Force Rates'
UNEMPLOYMENT_RATIOS_SUBSET_4_GRAPH_TITLE = 'US Job-vacancy rate (Unfilled Vacancies/Labor Force)'
UNEMPLOYMENT_RATIOS_SUBSET_5_GRAPH_TITLE = 'US Job Vacancies per Unemployed Person'
MEAN_VACANCIES_PER_UNEMPLOYED = 'Mean level of job vacancies per unemployed person'
CORRELATION_FFR_PR_GRAPH_TITLE = 'Correlation between annual changes in Fed Funds and Participation Rates'
CORRELATION_FFR_UR_GRAPH_TITLE = 'Correlation between annual changes in Fed Funds and Unemployment Rates'
ANNUAL_PERCENTAGE_CHANGES = ' Annual Percantage Changes'

# %%

oecd_json_override = '{"id": "OECD", "data_content_type": "JSON",\
    "url": "https://sdmx.oecd.org/public/rest",\
    "documentation": "https://sdmx.oecd.org/public/rest/",\
    "name": "Organisation for Economic Co-operation and Development"}'
sdmx.add_source(oecd_json_override, id='OECD', override=True)

data = web.get_data_fred(['CNP16OV', 'CLF16OV'])