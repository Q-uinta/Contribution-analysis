import numpy as np
import pandas as pd

### IMPORT THE DATA ###

var_name_to_filename_dict = {'water_use': 'Water_use.csv', 
               'acidification': 'Acidification.csv', 
               'climate_change': 'Climate_change.csv', 
               'ecotoxicity': 'Ecotoxicity.csv', 
               'eutrophication_freshwater': 'Eutrophication_freshwater.csv',
               'eutrophication_marine':'Eutrophication_marine.csv', 
               'eutrophication_terrestrial': 'Eutrophication_terrestrial.csv',
               'human_toxicity_cancer': 'Human_toxicity_cancer.csv', 
               'human_toxicity_non_cancer': 'Human_toxicity_non_cancer.csv', 
               'ionising_radiation': 'Ionising_radiation.csv', 
               'land_use': 'Land_use.csv', 
               'ozone_depletion': 'Ozone_depletion.csv', 
               'particulate_matter': 'Particulate_matter.csv', 
               'photochemical_ozone_formation':'Photochemical_ozone_formation.csv', 
               'resource_use_fossils': 'Resource_use_fossils.csv', 
               'resource_use_minerals_metals':'Resource_use_minerals_metals.csv'
}

def filenames_to_df_dict(var_name_to_filename_dict_in={}):
     df_dict = {}
     for label, v in var_name_to_filename_dict_in.items():
          df = pd.read_csv("Data/Process_contributions/"+ v, sep= ";", header=0)
          df_dict[label]=df
     return df_dict

dictionary_all_impact_categories_and_dataframes = filenames_to_df_dict(var_name_to_filename_dict)

#Export the results for the single score from an LCA software, in this case SimaPro is taken as an example
#The header is the first row, only the first 3 columns are imported [Damage Category, Unit, Total]
#In this specific example The EF impact categories are used, and the activities and numbers are random between 0-100 - To be replaced by own data
impact_categories = pd.read_csv("Data/Single_score_randomnized.csv", sep= ";", header=0, usecols=[i for i in range(0,3)]) #https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

#The names in SimaPro of the impact categories often contain space, capitals etc. Therefore, a matching file was made to link the names given to the impact categories here (See above the names for the imported csv's) to the names used in SimaPro
matching_file = pd.read_excel("Matching_IC_simapro_python.xlsx")


### THE CALCULATIONS ###

#Calculate the contribution of the impact categories:
single_score = impact_categories['Total'].iloc[0] #Make a variable containing the single score (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iloc.html)
impact_categories['Contribution Impact Categories [%]'] = impact_categories['Total'].div(single_score)*100 #Calculate the contribution (%) of each impact category (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.div.html)
impact_categories = impact_categories.sort_values(by="Contribution Impact Categories [%]").reset_index(drop=True) #Sort the contribution (%) of the impact categories (ascending) (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html & https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html)
impact_categories['Cumulative'] = impact_categories['Contribution Impact Categories [%]'].cumsum() #Cummulative sum the contribution (%) of the impact categories (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.cumsum.html) 
impact_categories.drop(impact_categories[impact_categories.Cumulative <= 20].index , inplace=True) # #The smallest <=20% is not part of the most relevant impact categories and will be dropped
impact_categories = impact_categories.sort_values(by="Contribution Impact Categories [%]", ascending=False).reset_index(drop=True).drop(index=0).reset_index(drop=True).drop(['Total', 'Cumulative'], axis=1)
#Sort the dataframe from largest to smallest contribution, drop the value column Total and the cumulative column and drop the first row (containing the single score, so 100%, which will not be needed anymore)

List_most_relevant_impact_categories = impact_categories['Damage category'].tolist() # Make a list of the most relevant impact categories identified above (https://pandas.pydata.org/docs/reference/api/pandas.Series.to_list.html)
matching_file_filtered_for_most_relevant_impact_categories = matching_file[matching_file['SP_name'].isin(List_most_relevant_impact_categories)] #filter out the most relevant impact categories in the matching file (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html)

total_overview = pd.DataFrame()
contribution_processes_combined = pd.DataFrame()
empty_dataframe = pd.DataFrame()

for y in matching_file_filtered_for_most_relevant_impact_categories['PY_name']:
              impact_categories_for_activities_and_processes = dictionary_all_impact_categories_and_dataframes[y]
              
              #Calculate the contribution of the activities:
              contribution_activities = impact_categories_for_activities_and_processes.loc[[0]].drop(['No', 'Process', 'Project', 'Unit'], axis=1).transpose() # Select the first row drop all descriptive columns and transpose the dataframe (https://stackoverflow.com/questions/67445064/how-to-drop-all-rows-except-specific-one-in-pandas)
              contribution_activities = contribution_activities.reset_index().rename(columns={0:'Value', 'index':'Activity'}) #Add an index and rename the columns 
              total_characterized_score_impact_category = contribution_activities['Value'].iloc[0] #Calculating the total characterized 
              contribution_activities = contribution_activities.drop(index=0).reset_index(drop=True) #remove row with totals
              contribution_activities['Contribution Activities [%]']  = contribution_activities['Value'].div(total_characterized_score_impact_category)*100 #Calculating the contribution (%) of the activities to the impact category  (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.div.html)
              contribution_activities['Contribution Activities [%]'] = contribution_activities['Contribution Activities [%]'].round(2) # Round to two decimals (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html)
              contribution_activities = contribution_activities.sort_values(by="Contribution Activities [%]").reset_index(drop=True) #Sort the contribution (%) of the activities (ascending) (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html & https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html)
              contribution_activities['Cumulative'] = contribution_activities['Contribution Activities [%]'].cumsum() #Cummulative sum the contribution (%) of the activities (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.cumsum.html)
              contribution_activities['activities_to_delete'] = contribution_activities['Contribution Activities [%]']<=20 #The smallest <=20% is not part of the most relevant activities
              contribution_activities = contribution_activities.sort_values(by="Contribution Activities [%]", ascending=False).reset_index(drop=True).drop(['Value', 'Cumulative'], axis=1)
              #Sort the dataframe from largest to smallest contribution and drop the value column and the cumulative column 

              #Calculate the contribution of the processes:
              processes = impact_categories_for_activities_and_processes.drop(['No', 'Total', 'Project', 'Unit'], axis=1).drop(index=0) # drop descriptive columns (except for process names) and the row containing the totals per activity
              percentages_processes_unsorted = processes.iloc[:,1:(len(processes.columns))]/total_characterized_score_impact_category*100 #calculate the contribution for each process(https://stackoverflow.com/questions/56311638/how-how-iloc-1-works-can-any-one-explain-1-params)
              
              activity=0
              while activity<=(len(percentages_processes_unsorted.columns)-1): #For every activity
                   contribution_processes = pd.DataFrame()
                   contribution_processes['Contribution Processes [%]'] = percentages_processes_unsorted.iloc[:,activity] #Take over the percentages and add them to the new dataframe Contribution_processes)
                   contribution_processes.insert(0, 'Activity', percentages_processes_unsorted.columns[activity]) #insert the name of the activity as a column at index 0
                   contribution_processes_expanded_with_names = pd.concat([processes.iloc[:,0],contribution_processes],axis=1) #combine the name of the processes, the names of the activities and the contribution of the processes all in one dataframe
                   contribution_processes_combined = pd.concat([contribution_processes_combined, contribution_processes_expanded_with_names]) #combine all process contribution analyses in one dataframe
                   activity+=1 #continue to the next activity


              contribution_processes_sorted = contribution_processes_combined.sort_values(by="Contribution Processes [%]").reset_index(drop=True)  #Sort the contribution (%) of the processes (ascending) (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html & https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html) 
              contribution_processes_sorted['Cumulative'] =  contribution_processes_sorted['Contribution Processes [%]'].cumsum() #Cummulative sum the contribution (%) of the processes (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.cumsum.html)
              contribution_processes_sorted.drop(contribution_processes_sorted[contribution_processes_sorted.Cumulative <= 20].index, inplace=True)  #The smallest <=20% is not part of the most relevant processes and will be dropped
              contribution_processes_sorted = contribution_processes_sorted.sort_values(by="Contribution Processes [%]", ascending=False).reset_index(drop=True).drop(['Cumulative'], axis=1) #Sort the dataframe from largest to smallest contribution and drop the cumulative column 
              contribution_processes_sorted['Contribution Processes [%]'] = contribution_processes_sorted['Contribution Processes [%]'].round(2) # Round to two decimals (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html)
              
              names_impact_categories_simapro_format = matching_file.loc[matching_file['PY_name']==y] #Filter the selected (y) most relevant impact categories
              names_impact_categories_simapro_format = names_impact_categories_simapro_format['SP_name'].reset_index(drop=True).iloc[0] #select the connected name in the SimaPro export 
              names_impact_categories_simapro_format = impact_categories[impact_categories['Damage category'] == names_impact_categories_simapro_format].reset_index(drop=True).drop(["Unit"], axis=1) #Filter from the contribution analysis on the most relevant impact category (name connected to y)
              contribution_processes_sorted = contribution_processes_sorted.merge(contribution_activities, on='Activity', how='left') #Merge the processes and activities together in one dataframe (https://pandas.pydata.org/docs/reference/api/pandas.merge.html)
              contribution_processes_sorted.insert(0, 'Contribution Activities [%]', contribution_processes_sorted.pop('Contribution Activities [%]')) #Isolate the contribution activities column, remove from dataframe and insert the contribution activities column at place 0 (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pop.html & https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.insert.html)
              contribution_processes_sorted = contribution_processes_sorted.sort_values(by=["Contribution Activities [%]", 'Contribution Processes [%]'], ascending=[False, False]).reset_index(drop=True) #sort first by the contribution of the most relevant activities and second by the contribution of the most relevant processes (https://stackoverflow.com/questions/17141558/how-to-sort-a-pandas-dataframe-by-two-or-more-columns)
              contribution_processes_sorted = pd.concat([names_impact_categories_simapro_format, contribution_processes_sorted], axis=1) #Combine the most relevant impact categories, activities and processes
              
              contribution_processes_sorted['To_delete'] = contribution_processes_sorted["Activity"] == contribution_processes_sorted["Activity"].shift()  # if the value in the Activity column is the same as the value on the previous row, the activity name will be removed (replaced by nan), here characterized by true (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.shift.html & https://stackoverflow.com/questions/24944355/pandas-dataframe-delete-rows-that-have-same-value-at-a-particular-column-as-a)
              total_overview = pd.concat([total_overview , contribution_processes_sorted]) #Add the contribution analysis for each impact category to the final overview
              contribution_processes_combined = empty_dataframe #reset the dataframe for the contribution of processes for the next impact category (this makes sure every impact category is evaluated by itself instead of all together)



### THE OUTPUT ###

total_overview.insert(2, 'Activity', total_overview.pop('Activity')) #Isolate the activity column, remove from dataframe and insert the activity column at place 2 (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pop.html & https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.insert.html)
total_overview.loc[total_overview.To_delete == True, ['Activity', 'Contribution Activities [%]']] = np.nan #replace the activity and activity percentages with nan if the value is equal to the value in the previous row (https://stackoverflow.com/questions/19226488/change-one-value-based-on-another-value-in-pandas)
total_overview = total_overview.drop(["To_delete"], axis=1) #drop the column which was used for filtering the activity names

total_overview["Contribution Processes [%]"] = total_overview["Contribution Processes [%]"].round(2) # Round to two decimals (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.round.html)

total_overview.loc[total_overview.activities_to_delete == True, ['Contribution Activities [%]']] = np.nan #replace the contribution of the activities 
total_overview = total_overview.drop(["activities_to_delete"], axis=1)

total_overview.to_csv("output.csv", sep=';',index=False) #export results to csv
