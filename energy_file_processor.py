
# coding: utf-8

# In[1]:

import pandas as pd
import matplotlib as plt
    get_ipython().magic(u'matplotlib inline')
    
def load_and_clean_energy_file():
    '''
    This function loads and cleans the energy file
    and returns the energy dataframe
    '''
    
    
    #load the energy indicators file and create the dataframe energy
    energy = pd.read_excel('Energy Indicators.xls',skiprows=9,skip_footer=38)
    #remove unwanted columns and rename the columns with appropriate label names
    del energy['Unnamed: 0'],energy['Unnamed: 1']
    energy = energy.rename(index = int,columns = 
                           {"Renewable Electricity Production":"% Renewable",
                            "Energy Supply per capita":"Energy Supply per Capita"})
    energy = energy.drop([0,1,2,3,4,5,6,7])
    energy = energy.reset_index()
    del energy['index']
    #energy supply values are converted to gigajoules
    energy['Energy Supply'] = energy['Energy Supply'].apply(lambda x:x*1000000)
    #country names are made appropriate, stripped unwanted data from country names
    for id in energy.index:
        if '(' in energy.iloc[id,0]:
            index = energy.iloc[id,0].index('(')
            value = energy.iloc[id,0][:index]
            energy.iloc[id,0] = value
        if any(char.isdigit() for char in energy.iloc[id,0]):
            result = ''.join([id for id in energy.iloc[id,0] if not id.isdigit()])
            energy.iloc[id,0] = result
    #certain country names are modified to the corresponding modern names    
    for id in energy.index:
    if energy.iloc[id,0] == 'Republic of Korea':
        energy.iloc[id,0] = 'South Korea'
    elif energy.iloc[id,0] == 'United States of America':
        energy.iloc[id,0] = 'United States'
    elif energy.iloc[id,0] == 'United Kingdom of Great Britain and Northern Ireland':
        energy.iloc[id,0] = 'United Kingdom'
    elif energy.iloc[id,0] == 'China, Hong Kong Special Administrative Region':
        energy.iloc[id,0] = 'Hong Kong'
        
    #unwanted spaces are removed
    energy['Country'] = energy['Country'].str.strip()
    
    return energy

def load_and_clean_gdp_file():
    '''
    This function loads and cleans the gdp file
    and returns the gdp dataframe
    '''
    GDP = pd.read_csv('world_bank.csv', skiprows=4)
    #country names are properly renamed in the gdp file
    for id in GDP.index:
        if GDP.iloc[id,0] == 'Korea, Rep.':
            GDP.iloc[id,0] = 'South Korea'
        elif GDP.iloc[id,0] == 'Iran, Islamic Rep.':
            GDP.iloc[id,0]='Iran'
        elif GDP.iloc[id,0] == 'Hong Kong SAR, China':
            GDP.iloc[id,0] = 'Hong Kong'
    # selects only the 2006-2015 years of gdp data
    GDP = GDP[list(GDP.columns[0:1])+list(GDP.columns[50:60])]
    
              
    return GDP
                                          
def load_scimen_file():
    '''
    This function loads the scimen file and returns the scimen dataframe
    '''
    Scimen = pd.read_excel('scimagojr-3.xlsx')
    return Scimen

def merge_df(energy,GDP,Scimen):
    '''
    This function merges the three dataframes based on the country name column
    and returns the top 15 rows corresponding to the top 15 countries
    in the Scimagojr Rank
    '''
    df_1 = pd.merge(Scimen,energy,left_on = 'Country',right_on = 'Country')
    df_2 = pd.merge(df_1,GDP,left_on = 'Country',right_on = 'Country Name')
    del df_2['Country Name']
    df_2= df_2.set_index('Country')
    top_15 = df_2.head(n = 15)
    return top_15

              
def get_avg_gdp(Top_15):
    '''
    This function returns the average gdp over the 10 year period of each country
    '''
    
    avg_gdp = pd.DataFrame(Top15[['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015']].mean(axis = 1))
    avg_gdp = avg_gdp.sort([0], ascending = False)
    avg_gdp.columns = ['avgGDP']
    return avg_gdp['avgGDP']

def sixth_largest(avg_gdp):
    '''
    This function returns the country with 6th largest average gdp
    '''
    count=0
    for id in avg_gdp.index:
        count = count + 1 
        if(count == 6):
            return id
        
def get_gdp_change(average_gdp,Top15):
    '''
    This function returns the gdp change over 10 years for the country
    with sixth largest average gdp
    '''
    country_name = sixth_largest(average_gdp)
    
    gdp_2006 = Top15.get_value(country_name,'2006')
    gdp_2015 = Top15.get_value(country_name,'2015')
    return gdp_2015-gdp_2006
              
def get_mean_energy_supply_per_capita(Top15):
    '''
    This function returns the mean energy supply per capita
    '''
    mean_espc = Top15['Energy Supply per Capita'].mean(axis = 0)
    mean_espc = mean_espc.item()
    return mean_espc

def get_country_with_max_renew(Top15):
    '''
    This function returns the country with the maximum % Renewable energy
    '''
    max_renewable = Top15['% Renewable'].max(axis = 0)
    index = Top15['% Renewable'][Top15['% Renewable'] == max_renewable].index.tolist()
    return index[0],max_renewable

def citation_ratio(Top15):
    '''
    This function creates a new column which is the ratio of Self-citations to Citations
    and returns the country with the maximum ratio
    '''
    Top15['Ratio'] = Top15['Self-citations'] / Top15['Citations']
    max_ratio = Top15['Ratio'].max(axis = 0)
    index = Top15['Ratio'][Top15['Ratio'] == max_ratio].index.tolist()
    return index[0],max_ratio

def get_third_most_populous(Top15):
    '''
    This function returns the third most populous country 
    '''
    Top15['Population'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15 = Top15.sort(columns = 'Population',axis = 0, ascending = False)
    count = 0
    for id in Top15.index:
        count = count + 1
        if(count == 3):
            return id

def get_corr(Top15):
    '''
    This function returns the pearson correlation between citable documents per capita
    and energy supply per capita
    '''
    Top15['Population'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable_doc_per_capita'] = Top15['Citable documents'] / Top15['Population']
    Top15['Energy Supply per Capita'] = Top15['Energy Supply per Capita'].astype(float)
    Top15['Citable_doc_per_capita'] = Top15['Citable_doc_per_capita'].astype(float)
    
    return Top15['Citable_doc_per_capita'].corr(Top15['Energy Supply per Capita'])

def visualize(Top15):
    '''
    This function plots citable documents per capita 
    and energy supply per capita
    '''
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable docs per Capita'] = Top15['Citable documents'] / Top15['PopEst']
    Top15.plot(x = 'Citable docs per Capita', y = 'Energy Supply per Capita', kind='scatter', xlim = [0, 0.0006])

def median_check(row, Top15):
    '''
    This function finds the flag value after checking if the % renewable value for a country is 
    greater than or less than the median
    Returns 1 if value > median
    Returns 0 if value < median
    '''
    median_value = Top15['% Renewable'].median(axis = 0)
    if row['% Renewable'] >= median_value:
        val = 1
    else:
        val = 0
    return val

def get_median_check_flag(Top15):
    '''
    This function returns a new column HighRenew after performing median check
    '''
    Top15['HighRenew'] = Top15.apply(median_check,axis=1,Top15)
    return Top15['HighRenew']

ContinentDict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}

def get_pop_stats(Top15):
    '''
    This function groups the countries into continents based on the continent dictionary
    Then returns the number of countries in each continent,
    total population, mean population and standard deviation of the populaiton
    '''
    Top15['Population'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    df = Top15.reset_index()
    df_1 = df[['Country','Population']].copy()
    
    continent = ['Asia','North America','Asia','Europe','Europe','North America','Europe','Asia','Europe','Asia','Europe','Europe','Asia','Australia','South America']
    continent_series = pd.Series(continent)
    df_1['Continent'] = continent_series
    df_2 = df_1.copy()
    grouped = pd.DataFrame({'size' : df_1.groupby('Continent').size(),
                            'sum':df_1.groupby('Continent')['Population'].sum()}).reset_index()
                
    grouped['mean'] = grouped['sum'] / grouped['size']
    df_2['Population'] = df_2['Population'].astype(float)
    std_grouped = pd.DataFrame({'Std': df_2.groupby('Continent')['Population'].std()})
    std_series = std_grouped['Std']
    grouped = grouped.set_index('Continent')
    grouped['std'] = pd.Series(std_series,index = grouped.index)
    return grouped

def get_cuts(Top15):
    '''
    This function cuts the % Renewable into 5 bins,
    Performs grouping into continents and these bins,
    returns the countries in each of these groups
    '''
    Top15['% Renewable'] = pd.cut(Top15['% Renewable'],5)
    continent = ['Asia','North America','Asia','Europe','Europe','North America','Europe','Asia','Europe','Asia','Europe','Europe','Asia','Australia','South America']
    continent_series = pd.Series(continent)
    df = Top15.reset_index()
    df['Continent'] = continent_series
    grouped = df.groupby(['Continent','% Renewable'])
    
    return grouped.size()

def convert_to_thousands(Top15):
    '''
    This function converts the PopEst series values into a string
    with thousands operator, seperated with commas
    '''
    Top15['Population'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    df = Top15[['Population']].copy()
    df = df.reset_index()
    id = 0
    for loop in df['Population']:
        df.iloc[id,1] = '{0:,}'.format(loop)
        id = id + 1
    
    df = df.rename(index = int,columns = {'Population':'PopEst'})
    df = df.set_index('Country')
    
    return df['PopEst']


def main():
    energy = load_and_clean_energy_file()
    gdp = load_and_clean_gdp_file()
    scimen = load_scimen_file()
    ranking_df = merge_df(energy,gdp,scimen)
    average_gdp = get_avg_gdp(ranking_df)
    print ('The average gdp of each country from the year 2006-2015 is ',average_gdp)
    gdp_change = get_gdp_change(average_gdp,ranking_df)
    print ('The gdp change of the country with sixth largest gdp change over 10 year span is',
          gdp_change)
    mean_espc = get_mean_energy_supply_per_capita(ranking_df)
    print ('The mean energy supply per capita is ',mean_espc)
    country_with_max_renew, value = get_country_with_max_renew(ranking_df)
    print ('{} is the country with maximum % Renewable energy and the value is {}',country_with_max_renew,value)
    country_with_max_citation_ratio, ratio_value = citation_ratio(ranking_df)
    print ('{} is the country with maximum citation ratio and the value is {}',
           country_with_max_citation_ratio, ratio_value)
    third_most_populous = get_third_most_populous(ranking_df)
    print ('{} is the third most populous country ', third_most_populous)
    correlation = get_corr(ranking_df)
    print ('The pearson correlation between citable documents per capita and energy supply per capita is'
          correlation)
    print ('Plot between citable documents per capita and energy supply per capita is',visualize(ranking_df))
    high_renewable_series = get_median_check_flag(ranking_df)
    print ('The series after median check is ', high_renewable_series)
    continent_stats = get_pop_stats(ranking_df)
    print ('The continent-wise population stats: ',continent_stats)
    binned_series = get_cuts(ranking_df)
    print ('The binned series is ',binned_series)
    pop_estimate = convert_to_thousands(ranking_df)
    print ('The popestimate series converted to thousands values ',pop_estimate)
    
    
    
    
    
    
    
    
    

    
    
    
if  __name__ =='__main__':main()

