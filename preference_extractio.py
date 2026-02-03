"""this file serves to extract the user preferences and return them as normalized values to pass to retrieve restaurant.py """

# imports:
#//>>
import pandas as pd
from pandas import DataFrame, Series
import Levenshtein as lv
import os
from classes import Preference_Object,Extra_Requirement
from typing import Dict, Optional, Set, Tuple, List

dir_name: str           = os.path.dirname(os.path.abspath(__file__))
file_path: str          = os.path.join(dir_name, 'datasets/restaurant_info.csv')
rest_info: DataFrame    = pd.read_csv(file_path, sep=",")


def get_unique_values(rest_info: DataFrame) -> Dict[str, List[str]]:
    #//>>
    """this function extracts the unique values that we need to compare on by reading the food types from csv files.
    returns a dictionary mapping each key with its unique values"""

    areas: List[str] = ["centre", "north", "east", "south", "west"]
    priceranges: List[str] = ["cheap", "moderate", "expensive"]

    cleaned_foodtypes: List[str] = list()
    foodtypes: Series = rest_info.iloc[:, 3].astype(str)
    for f in foodtypes:
        f: str = f.lower().strip()
        cleaned_foodtypes.append(f)
    foodtypes: Set[str] = set(cleaned_foodtypes)

    unique_values: Dict[str, List[str]] = {
        "areas": areas,
        "priceranges": priceranges,
        "foodtypes": list(foodtypes)
    }

    return unique_values
    #//<<

def normalize_string(utterance) -> Tuple[str, Set[str]]:
    #//>>
    """this function preprocesses the input of the user, lowercasing it, and then checks if the user already stated some dontcare preferences
    returns the processed text and a set of dontcare preferences"""
    lower_utterance: str = utterance.lower().strip()
    dontcare_preferences: set = set()

    # check for user apathy for certain atributes & add those to set:
    #//>>
    #checking if the user already stated some dontcare preferences
    if "any area" in lower_utterance or  "any part of town" in lower_utterance or "no preference for area" in lower_utterance or "anywhere" in lower_utterance:
        dontcare_preferences.add("area")
    
    if "any price" in lower_utterance or "price doesnt matter" in lower_utterance or "no preference for the price" in lower_utterance:
        dontcare_preferences.add("pricerange")

    if "any food" in lower_utterance or "any cuisine" in lower_utterance:
        dontcare_preferences.add("foodtype")
    #//<<

    return lower_utterance, dontcare_preferences
    #//<<

def resolution_to_unique(tokens: list[str], allowed: Set[str], field: str) -> Optional[str]:
    #//>>
    """this function serves to compare a candidate token to the allowed ones
    returns the best match (which can also be None)"""

    best_match: Optional[str] = None
    best_distance: int = 1000 #setting it to a unresonably high number
    token: str = ""

    #iterate trhough the tokens and allowed words, and keep the best match
    for t in tokens:
        if field == "area" and t == "eat":
            continue
        for w in allowed:
            distance = lv.distance(t,w)
            if distance < best_distance:
                best_distance = distance
                best_match = w
                token = t
    
    #check for a threshold of 3 for longer words
    if len(token) > 5 and best_distance <= 3: 
        return best_match
    elif best_distance <= 1: # for shorter words we consider a stricter threshold
        return best_match

    return None
#//<<

def extract_preference(utterance: str, asked: str, user_preference: Preference_Object) -> Preference_Object:
    #//>>
    """this function is the main one in this script, the purpose is to take the user utterance and store his preferences
    returns a Preference_Object Class:
    - if the preference was stated as insignificant the value is dontcare
    - if the preference was expressed the value is the preference
    - if it wasnt stated at all the value is None"""

    global rest_info

    # 1. get the utterance and apathetic attributes:
    utterance: str
    dontcare_preferences: Set[str]
    utterance, dontcare_preferences = normalize_string(utterance)

    if utterance == "any":
        if asked == "food":
            user_preference.food = "any"
        if asked == "pricerange":
            user_preference.pricerange = "any"
        if asked == "area":
            user_preference.area = "any"

    # 2. update values in Preference Object to represent apathetic attributes
    #//>>
    if "area" in dontcare_preferences:
        user_preference.area = "any"
    if "pricerange" in dontcare_preferences:
        user_preference.pricerange = "any"
    if "foodtype" in dontcare_preferences:
        user_preference.food = "any"
    #//<<

    # 3. get unique values for the attributes
    unique_values: Dict[str, List[str]] = get_unique_values(rest_info)

    # 6. split the utterance into tokens
    tokens: List[str] = utterance.split()

    # 7. update values to represent direct matches:
    #//>>
    for t in tokens:
        if user_preference.pricerange != "any" and t in unique_values["priceranges"]:
            user_preference.pricerange = t

    for t in tokens:
        if user_preference.area != "any" and t in unique_values["areas"]:
            user_preference.area = t

    for t in tokens:
        if user_preference.food != "any" and t in unique_values["foodtypes"]:
            user_preference.food = t
    #//<<

    # 8. If there is no exact match, try to find "similar matches" and represent those:
    #//>>
    if user_preference.pricerange == None:
        result_price: Optional[str] = resolution_to_unique(tokens, set(unique_values["priceranges"]), "price")
        if result_price is not None:
            user_preference.pricerange = result_price

    if user_preference.area == None:
        result_area: Optional[str] = resolution_to_unique(tokens, set(unique_values["areas"]), "area")
        if result_area is not None:
            user_preference.area = result_area

    if user_preference.food == None:
        result_food: Optional[str] = resolution_to_unique(tokens, set(unique_values["foodtypes"]), "food")
        if result_food is not None:
            user_preference.food = result_food
    #//<<

    return user_preference
    #//<<

def extract_requirement(utterance) -> Set[str]:
    #//>>
    """this function serves to identify what attribute the user wants to know more 
    about based on the utterance given by the user.
    It returns a string representing the attribute of the restaurant"""

    # 1. preprocess the string:
    utterance, _ = normalize_string(utterance)

    req_type: List[str] = ["restaurantname","pricerange","area","food","phone","addr","postcode", "food_quality", "crowdedness", "length_of_stay", "assign_seats", "child_friendly", "romantic", "touristic"]

    restaurantname_indicators: List[str] = ["name", "called", "named"]
    pricerange_indicators: List[str] = ["priced", "price", "money", "spend", "cost", "cheap", "expensive"]
    area_indicators: List[str] = ["zone", "part", "side", "where", "where is it", "located", "place"]
    food_indicators: List[str] = ["cuisine", "dishes", "food", "type", "kind"]
    phone_indicators: List[str] = ["phone", "number", "phone number", "contact", "telephone", "call", "reference"]
    addr_indicators: List[str] = ["street", "square", "located precisely", "where can i find it", "address", "address number", "street number"]
    postcode_indicators: List[str] = ["postcode", "zip", "postal code"]
    foodquality_indicators: List[str] = ["quality", "level"]
    crowededness_indicators: List[str] = ["people", "busy", "amount of people"]
    lengthofstay_indicators: List[str] = ["minutes", "hours", "how many minutes"]
    assign_seats_indicators: List[str] = ["seats","seat" ,"how many seats", "seated", "chairs", "room", "space", "freely take a"]
    child_friendly_indicators: List[str] = ["children", "kids", "childfriendly", "child", "babies", "baby"]
    romantic_indicators: List[str] = ["romantic", "atmosphere", "couple", "date"]
    touristic_indicatos: List[str] = ["touristic", "local", "tourstis"]

    result: List[str] = []

    for i in restaurantname_indicators:
        if i in utterance:
            result.append(req_type[0])

    for i in pricerange_indicators:
        if i in utterance:
            result.append(req_type[1])

    for i in area_indicators:
        if i in utterance:
            result.append(req_type[2])

    for i in food_indicators:
        if i in utterance:
            result.append(req_type[3])

    for i in phone_indicators:
        if i in utterance:
            result.append(req_type[4])

    for i in addr_indicators:
        if i in utterance:
            result.append(req_type[5])

    for i in postcode_indicators:
        if i in utterance:
            result.append(req_type[6])

    for i in foodquality_indicators: 
        if i in utterance:
            result.append(req_type[7])

    for i in crowededness_indicators: 
        if i in utterance:
            result.append(req_type[8])

    for i in lengthofstay_indicators: 
        if i in utterance:
            result.append(req_type[9])

    for i in assign_seats_indicators: 
        if i in utterance:
            result.append(req_type[10])

    for i in child_friendly_indicators: 
        if i in utterance:
            result.append(req_type[11])

    for i in romantic_indicators: 
        if i in utterance:
            result.append(req_type[12])

    for i in touristic_indicatos: 
        if i in utterance:
            result.append(req_type[13])

    result = [t for t in req_type if t in result]
    return result
        

def extract_extra_req(utterance: str) -> Extra_Requirement:
    nonList = ["no","none","nothing","don't","not"]
    for n in nonList:
        if n in utterance: 
            return Extra_Requirement(None,None,None,None)
    reqtypes = extract_requirement(utterance)
    if "touristic" in reqtypes: 
        return (Extra_Requirement(True,None,None,None))
    elif "romantic" in reqtypes:
        return (Extra_Requirement(None,True,None,None))
    elif "child_friendly" in reqtypes:
        return(Extra_Requirement(None,None,True,None))
    elif "assign_seats" in reqtypes:
        return(Extra_Requirement(None,None,None,True))
    else :
        return (Extra_Requirement(None,None,None,None))

