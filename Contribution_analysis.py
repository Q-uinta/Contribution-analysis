import numpy as np
import pandas as pd

### IMPORT THE DATA ###

#Export the results for the single score from an LCA software, in this case SimaPro is taken as an example
#The header is the first row, only the first 3 columns are imported [Damage Category, Unit, Total]
#In this specific example The EF impact categories are used, and the activities and numbers are random between 0-100 - To be replaced by own data
impact_categories = pd.read_csv("Data/Single_score_randomnized.csv", sep= ";", header=0, usecols=[i for i in range(0,3)]) #https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

#Import the process contribution for each impact category
water_use = pd.read_csv("Data/Process_contributions/Water_use.csv", sep= ";", header=0)
acidification = pd.read_csv("Data/Process_contributions/Acidification.csv", sep= ";", header=0)
climate_change = pd.read_csv("Data/Process_contributions/Climate_change.csv", sep= ";", header=0)

#In this example SimaPro was assumed to be the LCA software. In SimaPro Ecotoxicity can be divided into multiple parts, in this case part 1 and 2. Both dataframes were combined and a new row was added 
# containing the totals of the combined dataframe
ecotoxicity_part_1 = pd.read_csv("Data/Process_contributions/Ecotoxicity_part_1.csv", sep= ";", header=0)
ecotoxicity_part_1 = ecotoxicity_part_1.drop(index=0).reset_index(drop=True) #drop the row containing the totals of ecotoxicity part 1
ecotoxicity_part_2 = pd.read_csv("Data/Process_contributions/Ecotoxicity_part_2.csv", sep= ";", header=0)
ecotoxicity_part_2 = ecotoxicity_part_2.drop(index=0).reset_index(drop=True) #drop the row containing the totals of ecotoxicity part 2

ecotoxicity = pd.concat([ecotoxicity_part_1, ecotoxicity_part_2], ignore_index=True).reset_index(drop=True) #Add both dataframes after eachother and reset the index (https://pandas.pydata.org/docs/reference/api/pandas.concat.html)

#The following is based on https://stackoverflow.com/questions/43408621/add-a-row-at-top-in-pandas-dataframe:
ecotoxicity.index += 1 #Increase the index with 1
ecotoxicity.loc[0] = ecotoxicity.sum() #Add a row which index is 0 (which does not exist yet as the index was increased by 1 for all the other rows), the row will be added to the end of the dataframe
ecotoxicity = ecotoxicity.sort_index() #sort the index so the row with the totals will be at the top again

eutrophication_freshwater  = pd.read_csv("Data/Process_contributions/Eutrophication_freshwater.csv", sep= ";", header=0)
eutrophication_marine = pd.read_csv("Data/Process_contributions/Eutrophication_marine.csv", sep= ";", header=0)
eutrophication_terrestrial = pd.read_csv("Data/Process_contributions/Eutrophication_terrestrial.csv", sep= ";", header=0)
human_toxicity_cancer = pd.read_csv("Data/Process_contributions/Human_toxicity_cancer.csv", sep= ";", header=0)
human_toxicity_non_cancer  = pd.read_csv("Data/Process_contributions/Human_toxicity_non_cancer.csv", sep= ";", header=0)
ionising_radiation = pd.read_csv("Data/Process_contributions/Ionising_radiation.csv", sep= ";", header=0)
land_use  = pd.read_csv("Data/Process_contributions/Land_use.csv", sep= ";", header=0)
ozone_depletion = pd.read_csv("Data/Process_contributions/Ozone_depletion.csv", sep= ";", header=0)
particulate_matter = pd.read_csv("Data/Process_contributions/Particulate_matter.csv", sep= ";", header=0)
photochemical_ozone_formation = pd.read_csv("Data/Process_contributions/Photochemical_ozone_formation.csv", sep= ";", header=0)
resource_use_fossils = pd.read_csv("Data/Process_contributions/Resource_use_fossils.csv", sep= ";", header=0)
resource_use_minerals_metals = pd.read_csv("Data/Process_contributions/Resource_use_minerals_metals.csv", sep= ";", header=0)

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
#to loop through the dataframes for the contribution of the activities and processes a dictionary is made, linking each dataframe to a variable
dictionary_all_impact_categories_and_dataframes = {'water_use': water_use, 'acidification': acidification, 'climate_change':climate_change, 'ecotoxicity':ecotoxicity, 'eutrophication_freshwater':eutrophication_freshwater, 'eutrophication_marine':eutrophication_marine, 'eutrophication_terrestrial':eutrophication_terrestrial, 'human_toxicity_cancer':human_toxicity_cancer, 'human_toxicity_non_cancer':human_toxicity_non_cancer, 'ionising_radiation':ionising_radiation, 'land_use':land_use, 'ozone_depletion':ozone_depletion, 'particulate_matter':particulate_matter, 'photochemical_ozone_formation':photochemical_ozone_formation, 'resource_use_fossils':resource_use_fossils, 'resource_use_minerals_metals':resource_use_minerals_metals}

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
