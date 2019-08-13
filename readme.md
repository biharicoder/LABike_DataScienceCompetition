This project is focused on analyzing the Los Angles Metro Bike Share
data. This operation provides rental bicycles 365 days a year since the 2nd quarter
of 2016. During this period, four regions in Los Angeles were served:
1. Downtown LA,
2. The Port of LA
3. Venice, and
4. Pasadena.


Metro Bike Share plan to expand their operations into other areas of Los Angeles.
The primary focus is on predicting the number of bicycles needed at each station, evaluating the pricing
system currently used to make recommendations for possible pricing changes and
expanding the network. A key question is how to manage bicycle staging to meet
demand, and where to look opportunities to expand into new regions in the LA
basin.
Statistical models are developed for forecasting demand for the coming month. From this, recommendations are prepared for:
1. Managing bicycle staging at the 140+ rental stations,
2. Forecasting income from ticket sales on a monthly basis for each region,
and make recommendations for possible pricing modifications.
3. Identifying key characteristics that identify whether a region will be successful
in the future by evaluating the four regions found in these data.


Following are the descriptions of each of the files in this repository:

LABikeData.xls: Excel file containing data downloaded from LA Metro Bike Sharing official website

LABike_sorting_visual_code.ipyng: Jupyter notebook for preliminary data analysis

Report.docx: Final report of the project

Station_Tables.xlsx: Data regarding the bike stations downloaded from the official website of LA Metro bike share company

data_cleaning.ipynb: Jupyter notebook for data cleaning and EDA

df_mod.csv: cleaned dataset

final_pre_processing.ipynb: Jupyter notebook for data preprocessing

linear_regression_monthly.ipynb: 

pricing_optimization.ipynb: Jupyter notebook for linear and quadratic optimization of the total revenue and pricing recommendation based on the analysis of old and current pricing model

unique_cordinates.csv: Excel file in which distance is calculated using Google Matrix API using start and end coordinates and the mode of transport set as bike ride

web_scraping.ipynb: A notebook that mines data from the LA Bike metro website

