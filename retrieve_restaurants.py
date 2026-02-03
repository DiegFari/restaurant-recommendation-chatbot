import csv 
import os
from enum import Enum
import pandas as pd
from pandas import DataFrame, Series
from typing import List
import numpy as np
from classes import Preference_Object,Pricerange,Area, Extra_Requirement, Match



def get_restaurants_from_file(file_name: str = 'datasets/extended_restaurant_info.csv'):
  #//>>
 """
 This function reads the restaurants from the csv file and turns it into a list of dictionaries 
 """

 dir = os.path.dirname(os.path.abspath(__file__))
 file_path = os.path.join(dir, file_name)
 

 with open(file_path, newline = '', encoding='utf_8') as csvfile: 
    reader = csv.DictReader(csvfile)
    restaurants = list(reader) # convert the reader into a list of dictionaries 

 return restaurants
 #//<<



def filter_restaurants(pref: Preference_Object):
  #//>>
  """
  This function filters the restaurants from restaurant_info.csv based on the preferences given in the 
  preference object 

  the function returns a list of all the restaurants that passed the filter, this list can be empty 
  """

  restaurants = get_restaurants_from_file() #read the restaurants from the file 
  
  #use list comprehension to retrieve all preffered restaurants 
  # if a value is None allow it because there was no preference by the user 
  pref_list = [
  x for x in restaurants
  if ( pref.restaurantname is None or (pref.restaurantname.lower() == x['restaurantname'].lower()))
  and  (pref.pricerange is None or  (pref.pricerange == x['pricerange'])or pref.pricerange== Pricerange.ANY)
  and  (pref.area is None or ( pref.area == x['area']) or (pref.area == Area.ANY))
  and  (pref.food is None or  (pref.food.lower() == x['food'].lower()) or pref.food.lower() == "any")
  ]
  return pref_list
#//<<


"""From now on the script deals with the extension of the dataset based on the additional properties"""


def filter_aditional_requirements(selected_restaurants : List[Match] , extra_requirements: Extra_Requirement):
  
 
  reqlist = [
  x for x in selected_restaurants
  if (extra_requirements.assign_seats is None or (str(extra_requirements.assign_seats) == x.assign_seats))
  and (extra_requirements.child_friendly is None or (str(extra_requirements.child_friendly) == x.child_friendly))
  and (extra_requirements.romantic is None or (str(extra_requirements.romantic) == x.romantic))
  and (extra_requirements.touristic is None or (str(extra_requirements.touristic) == x.touristic))
  ]

  return reqlist


def explain_requirement(match : Match, requirement:Extra_Requirement):
  #explains one requirement for one restaurant
  """
  this function needs as input one restaurant and an extra requirement, it returns a dictionary with as keys the requirements that are 
  in this restaurant and as value why
  """
  explain = dict()
  if requirement.romantic:
     if match.crowdedness not in ["busy","overcrowded"] and int(match.length_of_stay) > 60:
        explain["romantic"] = "people stay for long and it is not busy"
  if requirement.assign_seats:
     if(match.crowdedness in ["busy" , "overcrowded"]):
        explain["assigned seats"] = "it can be busy"
  if requirement.child_friendly:
     if(int(match.length_of_stay) < 45 ):
        explain["child friendly"] = "people tend to stay eat for a short time"
  if requirement.touristic:
     if(match.food_quality in ["good","excellent"] and match.pricerange == "cheap" and match.food != "romanian"):
        explain["touristic"]  = "it has good food and a cheap price"
  return explain



def assign_touristic(row) -> bool:
    if row['food'] == "romanian":
        return False
    elif (row["food_quality"] in ["good", "excellent"]) and row["pricerange"] == "cheap":
        return True
    return False

def assign_seats(row) -> bool:
    if row["crowdedness"] == "busy" or row["crowdedness"] == "overcrowded":
        return True
    return False

def assign_child_friendliness(row) -> bool:
    if row["length_of_stay"] > 45:
        return False
    return True

def assign_romanticism(row) -> bool:
    if row["crowdedness"] == "busy" or row["crowdedness"] == "overcrowded":
        return False
    elif row["length_of_stay"] > 60:
        return True
    return False


def expand_data():
# Extending the dataset:

# 1. Getting the original data

    data: DataFrame = pd.read_csv("datasets/restaurant_info.csv")

# 2. extend the dataset (with randomness):
#//>>
    data = data.assign(food_quality = np.random.choice(["terrible", "insufficient", "average", "good", "excellent"], len(data), [0.1,0.2,0.4,0.2,0.1]))
    data = data.assign(crowdedness = np.random.choice(["empty", "calm", "normal", "busy", "overcrowded"], len(data), [0.05,0.15,0.4,0.2,0.2]))
    data = data.assign(length_of_stay = np.random.randint(5, 180, len(data), int))
# print(data.head())
#//<<

# 3. extend the dataset (with rules):
    data["touristic"] = data.apply(assign_touristic, axis=1)
    data["assign_seats"] = data.apply(assign_seats, axis=1)
    data["child_friendly"] = data.apply(assign_child_friendliness, axis=1)
    data["romantic"] = data.apply(assign_romanticism, axis=1)
    data.head()

# 4. save the dataset:
    data.to_csv("datasets/extended_restaurant_info.csv")

