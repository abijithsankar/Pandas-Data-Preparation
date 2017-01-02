
# coding: utf-8

# In[ ]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from collections import OrderedDict
from scipy import stats

def get_states_mapping(order_flag):
    '''
    This function returns the mapping between state names and their aconyms
    It has two maps, one which has all the legal states in US
    and the other which has additional acronym information which
    is used in later stages of the hypothesis testing
    '''
    
    given_states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    inv_states = {'OH': 'Ohio', 'KY': 'Kentucky', 'NV': 'Nevada', 'WY': 'Wyoming', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'MS': 'Mississippi', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
    state_map_unordered = {v: k for k, v in inv_states.items()}
    state_map = OrderedDict(sorted(state_map_unordered.items(), key = lambda t: t[0]))
    #order flag is used to determine the type of statemapping required for the data analysis
    if order_flag == 1:
        return state_map
    else:
        return given_states
    
def get_list_of_university_towns():
    '''
    This function returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame is:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning is done:

    1. For "State", characters from "[" to the end are removed so as to have the proper state names.
    2. For "RegionName", when applicable, every character from " (" to the end is removed.
    3. newline character in the text files are also processed
    '''
    temp_list = []
    with open('university_towns.txt') as f:
        lines = f.read()
        temp_list.append(lines)
    linelist = ''.join(temp_list[0])
    town_list = linelist.split('\n')
    for id,name in enumerate(town_list):        
        if '[' in name and '(' not in name:
            index = name.index('[')
            town_list[id] = name[:index].strip()+"*"
        if '(' in name:
            index = name.index('(')
            town_list[id] = name[:index].strip()
    statelist = []
    regionlist = []
    count = -1
    state_name_list_from_map = []
    flag=0
    state_map = get_state_map(1)
    for key,value in state_map.items():
        state_name_list_from_map.append(key)
        
    for name in town_list:
        if '*' not in name:
            regionlist.append(name)
            statelist.append(state_name_list_from_map[count])
            flag = 1
        elif '*' in name:
            count = count+1
                
    
    
    town_df = pd.DataFrame({'RegionName':regionlist,'State':statelist})
    town_df = town_df.drop(town_df.index[len(town_df)-1])
    cols = town_df.columns.tolist()
    temp = cols[0]
    cols[0]= cols[1]
    cols[1]=temp
    town_df = town_df[cols]
    return town_df

def process_gdp_file():
    '''
    This function loads and process the gdp data of the states and
    returns gdp dataframe
    '''
    gdp = pd.read_excel('gdplev.xls',skiprows=219)
    label_names = gdp.columns.tolist()
    gdp = gdp.rename(columns={'Unnamed: 0':'Annual','Unnamed: 1':'GDPCurrent','Unnamed: 2':'Null','Unnamed: 3':'GDP2009Chained','1999q4':'Quarterly',9926.1:'GDPCurrentQ',12323.3:'GDPChainedQ','Unnamed: 7':'Null2'})
    del gdp['Annual']
    del gdp['GDPCurrent']
    del gdp['Null']
    del gdp['GDP2009Chained']
    del gdp['Null2']
    return gdp


def get_recession_start(gdp):
    '''
    This function returns the year and quarter 
    of the recession start time as a 
    string value in a format such as 2005q3
    '''
    
    for id in gdp.index:
        if gdp.iloc[id,2] > gdp.iloc[id + 1,2]:
            if gdp.iloc[id + 1,2]>gdp.iloc[id + 2,2]:
                return gdp.iloc[id + 1,0]
            
def get_recession_end(gdp):
    '''
    This function returns the year and quarter 
    of the recession end time as a 
    string value in a format such as 2005q3
    '''
    
    start_index = gdp[gdp['Quarterly'] == get_recession_start()].index.tolist()
    start = start_index[0].item()

    for id in range(start,len(gdp)):
        if gdp.iloc[id,2] < gdp.iloc[id + 1,2]:
            if gdp.iloc[id + 1,2] < gdp.iloc[id + 2,2]:
                return gdp.iloc[id + 2,0]
            
def get_recession_bottom():
    '''
    This function returns the year and quarter 
    of the recession bottom time as a 
    string value in a format such as 2005q3
    '''
    
    start_index = gdp[gdp['Quarterly'] == get_recession_start()].index.tolist()
    start = start_index[0].item()
    
    end_index = gdp[gdp['Quarterly'] == get_recession_end()].index.tolist()
    end = end_index[0].item()
    minimum_gdp = gdp.iloc[start,2]
    gdp_list = []
    for id in range(start + 1,end):
        if gdp.iloc[id,2] < minimum_gdp:
            minimum_gdp = gdp.iloc[id,2]
    bottom_row = gdp[gdp['GDPChainedQ'] == minimum_gdp]
    for id in bottom_row.index:
        return bottom_row.loc[id]['Quarterly']
    
    
def process_housing_data_file():
    '''
    This function loads and process the housing data file
    The date values are changed to datetime format
    The code is made pandorable using resampling technique
    '''
    hdata = pd.read_csv('City_Zhvi_AllHomes.csv')
    housingdata = hdata.drop(hdata.columns[3:51],axis = 1)
    del housingdata['RegionID']
    column_names = ['RegionName','State']
    date_values = []
    for c in housingdata.columns:
        if c != 'RegionName':
            if c!='State':
                name = pd.to_datetime(c)
                column_names.append(name)
    housingdata.columns = column_names
    housingdata_1 = housingdata[['RegionName','State']]
    housingdata_2 = housingdata.iloc[:,2:]
    housingdata_2.columns = pd.DatetimeIndex(housingdata_2.columns)
    transposed_df = housingdata_2.transpose()
    resampled_df = transposed_df.resample('3M',label = 'right',closed = 'left').mean()
    housingdata_3 = resampled_df.transpose()
    sampled_column_names = housingdata_3.columns
    quarter_list = []
    for val in sampled_column_names:
        quarter_list.append(str(val.year) + "q" + str(val.quarter))
    housingdata_3.columns = quarter_list
    housing_dataframe = housingdata_1.merge(housingdata_3,left_index = True,right_index = True)
    return housing_dataframe


def convert_housing_data_to_quarters():
    '''
    This function converts the housing data to quarters 
    and returns it as mean values in a dataframe. 
    This dataframe has columns for 2000q1 through 2016q3, 
    and has a multi-index in the shape of ["State","RegionName"].
    '''
    housing_dataframe = process_housing_data_file()
    housing_dataframe = housing_dataframe.replace({"State": given_states})
    housing_dataframe = housing_dataframe.set_index(['State','RegionName'])
    return housing_dataframe




def run_ttest():
    '''
    This function first creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a reduced market loss).
    '''
    housing_df = convert_housing_data_to_quarters()
    housing_df = housing_df.reset_index()
    recession_start = get_recession_start()
    recession_bottom = get_recession_bottom()
    start_index = housing_df.columns.get_loc(recession_start)
    bottom_index = housing_df.columns.get_loc(recession_bottom)
    pre_start_index = start_index - 1
    housing_df['Ratio'] = housing_df[housing_df.columns[pre_start_index]] / housing_df[hdf.columns[bottom_index]]
    
    
    
    univ_towns = get_list_of_university_towns()
    univ_towns_df = pd.merge(univ_towns,housing_df,how='left',on = ['State','RegionName'])
    mask = housing_df['State'].isin(housing_df['State']) & housing_df['RegionName'].isin(housing_df['RegionName'])
    #boolean masking
    non_univ_towns_df = housing_df[~mask]
    
    
    univ_towns_df = univ_towns_df[np.isfinite(univ_towns_df['Ratio'])]
    non_univ_towns_df = non_univ_towns_df[np.isfinite(non_univ_towns_df['Ratio'])]
    
    mean_ratio_dfu = univ_towns_df['Ratio'].mean()
    mean_ratio_dfnu = non_univ_towns_df['Ratio'].mean()
    
    if mean_ratio_dfu < mean_ratio_dfnu:
        better = "university town"
    else:
        better = "non-university town"
    
    t_test_result = stats.ttest_ind(univ_towns_df['Ratio'], non_univ_towns_df['Ratio'])
    different = False
    if t_test_result.pvalue < .01:
        different = True
    
    p = t_test_result.pvalue
    
    return different,p,better

def main():
    '''
    Performs the hypothesis testing, an important statistical analysis method
    
    A quarter is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
    A recession is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
    A recession bottom is the quarter within a recession which had the lowest GDP.
    A university town is a city which has a high percentage of university students compared to the total population of the city.
    
    Hypothesis: University towns have their mean housing prices less effected by recessions. 
    Run a t-test to compare the ratio of the mean price of houses in university towns 
    the quarter before the recession starts compared to the recession bottom. 
    (price_ratio=quarter_before_recession/recession_bottom)
    '''
    town_df = get_list_of_university_towns()
    gdp = process_gdp_file()
    
    recession_start = get_recession_start(gdp)
    print ('The recession start quarter is ',recession_start)
    
    recession_end = get_recession_end(gdp)
    print ('The recession end quarter is ',recession_end)
    
    recession_bottom = get_recession_bottom(gdp)
    print ('The recession bottom quarter is ', recession_bottom)
    
    housing_dataframe = convert_housing_data_to_quarters()
    print ('Result of t_test is ', run_ttest)
    
    
    
if name == "__main__":
    main()

