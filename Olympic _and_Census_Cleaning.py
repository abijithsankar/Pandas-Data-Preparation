
# coding: utf-8

# In[ ]:

import pandas as pd
import numpy as np

def load_olympics_file():
        
    '''
    The olympic data set is loaded and basic cleaning operations are performed    
    '''
    olympic_df = pd.read_csv('olympics.csv', index_col=0, skiprows=1)

    for col in olympic_df.columns:
        if col[:2] == '01':
            olympic_df.rename(columns={col:'Gold' + col[4:]}, inplace=True)
        if col[:2] == '02':
            olympic_df.rename(columns={col:'Silver' + col[4:]}, inplace=True)
        if col[:2] == '03':
            olympic_df.rename(columns={col:'Bronze' + col[4:]}, inplace=True)
        if col[:1] == '№':
            olympic_df.rename(columns={col:'#' + col[1:]}, inplace=True)


    names_ids = olympic_df.index.str.split('\s\(') # split the index by '('


    olympic_df.index = names_ids.str[0] # the [0] element is the country name (new index) 

    olympic_df['ID'] = names_ids.str[1].str[:3] # the [1] element is the abbreviation or ID (take first 3 characters from that)

    olympic_df = olympic_df.drop('Totals')
    
    return olympic_df



def first_country_of_df(olympic_df):
    '''
    This function returns the first country details in the olympic dataframe
    '''
    first_country_series = pd.Series(olympic_df.iloc[0])
    return first_country_series

def most_gold_summer(olympic_df):
    '''
    This function returns the country that won the most number of Gold medals in summer games
    '''
    return olympic_df['Gold'].idxmax()

def biggest_diff_gold(olympic_df):
    '''
    This function returns the country with the biggest difference between their summer and winter golf counts
    '''
    olympic_df['Difference'] = olympic_df['Total'] - olympic_df['Total.1']
    return olympic_df['Difference'].idxmax()


def biggest_relative_diff(olympic_df):
    '''
    This function returns the country has the biggest difference between their 
    summer gold medal counts and winter gold medal counts relative to their 
    total gold medal count
    '''
    temp_olympic_df = olympic_df.copy()
    temp_olympic_df = temp_olympic_df.reset_index()
    relative_list=[]
    for id in temp_olympic_df.index:
        if(int(temp_olympic_df.iloc[id,2])>=1 and int(temp_olympic_df.iloc[id,7])>=1 and int(temp_olympic_df.iloc[id,12])!=0):
            relative_list.append((temp_olympic_df.iloc[id,2]-temp_olympic_df.iloc[id,7])/temp_olympic_df.iloc[id,12])
        else:
            relative_list.append(-1)
    
    max_value = max(relative_list)
    max_index = relative_list.index(max_value)
    
    return temp_olympic_df.iloc[max_index,0]

def get_total_points(olympic_df):
    '''
    This function returns a series with the total points of each country weighted by their type of medals
    3 points for Gold
    2 points for Silver
    1 point for Bronze
    '''
    olympic_df['Points'] = (3 * olympic_df['Gold.2']) + (2 * olympic_df['Silver.2']) + olympic_df['Bronze.2']
    return olympic_df['Points']

def load_census_file():
    '''
    This function loads the census file and returns the census dataframe
    '''
    census_df = pd.read_csv('census.csv')
    return census_df

def get_state_with_most_counties(census_df):
    '''
    This function returns the state with most counties in it
    Special care has to be taken while processing the SUMLEV column
    The SUMLEV code depicts different information about the columns STNAME and COUNTY
    '''
    cleaned_census_df = census_df[census_df['SUMLEV'] == 50]
    grouped_census_df = pd.DataFrame({"count":cleaned_census_df['COUNTY'].groupby(cleaned_census_df['STNAME']).size()})
    
    return grouped_census_df['count'].idxmax()
    

def get_largest_abs_pop_change(census_df):
    '''
    This function returns the county with the largest absolute change 
    in population within the period 2010-2015
    '''
    cleaned_census_df = census_df[census_df['SUMLEV'] == 50]
    cleaned_census_df = cleaned_census_df.reset_index()
    req_census_df = cleaned_census_df.ix[:,'POPESTIMATE2010':'POPESTIMATE2015']
    req_census_df['COUNTY'] = cleaned_census_df['CTYNAME']
    req_census_df['Diff'] = ""
    
    difference_list = []
    for id in req_census_df.index:
        largest_change = 0
        for loop in range(0 , 5):
            for newloop in range(loop + 1 , 5):
                difference_value = abs(req_census_df.iloc[id,loop] - req_census_df.iloc[id,newloop])
                if(difference_value > largest_change):
                    largest_change = diff
        difference_list.append(largest_change)
        
    max_value = max(difference_list)
    max_index = difference_list.index(max_value)
    return req_census_df.iloc[max_index,6]    

def query(census_df):
    '''
    This function is used as a query that finds the counties that belong to US regions 1 or 2, 
    whose name starts with 'Washington', and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.
    '''
    census_df_1 = census_df[census_df['SUMLEV'] == 50]
    census_df_2 = census_df_1[census_df_1['REGION'] == 1]
    census_df_3 = census_df_2[census_df_2['CTYNAME'].str.contains('Washington')]
    census_df_4 = census_df_3[census_df_3['POPESTIMATE2015'] > census_df_3['POPESTIMATE2014']]
    
    census_df_5 = census_df_1[census_df_1['REGION'] == 2]
    census_df_6 = census_df_5[census_df_5['CTYNAME'].str.contains('Washington')]
    census_df_7 = census_df_6[census_df_6['POPESTIMATE2015'] > newdf_6['POPESTIMATE2014']]
    
    final_query_df = census_df_4.append(census_df_7)[['STNAME','CTYNAME']]
    return final_query_df



def main():
    
        olympic_df = load_olympics_file()
        first_country = first_country_of_df(olympic_df) 
        print ('The first country in the dataframe is ',first_country)
        most_gold_in_summer = most_gold_summer(olympic_df)
        print ('The country with most gold medals in summer is ',most_gold_in_summer)
        country_with_biggest_diff_gold = biggest_diff_gold(olympic_df)
        print ('The country with most biggest difference in gold medals in summer  and winter is '
               ,country_with_biggest_diff_gold)
        country_with_biggest_relative_diff = biggest_relative_diff(olympic_df)
        print ('The country with highest relative medal difference is ',country_with_biggest_relative_diff)
        point_series = get_total_points(olympic_df)
        print ('The points series is  ',point_series)
        
        census_df = load_census_file()
        state_with_most_counties = get_state_with_most_counties(census_df)
        print ('The state with most counties is  ',state_with_most_counties)
        county_with_largest_abs_pop_change = get_largest_abs_pop_change(census_df)
        print ('The county with largest absolute change in population from 2010-2015 is  ',
               county_with_largest_abs_pop_change)
        query_df = query(census_df)
        print ('The result of the query is ',query_df)
        
        
        
        


if  __name__ =='__main__':main()

