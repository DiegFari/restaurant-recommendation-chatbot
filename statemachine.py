# imports:
#//>>
from enum import Enum, auto
from dataclasses import dataclass, field
import numpy as np
import joblib
from retrieve_restaurants import  filter_restaurants , filter_aditional_requirements,explain_requirement
from bag_of_words import get_BoW_representation, encode_labels, convert_to_bow
from typing import Dict, List, Optional
from preference_extractio import extract_preference, extract_requirement,extract_extra_req
from classes import Preference_Object,Pricerange,Area, Extra_Requirement, Match
import time
from preference_extractio import extract_preference, extract_requirement
from bag_of_words import convert_to_bow
from typing import Tuple, List, Optional
#//<<

#----States----
class State(Enum):
    #//>>
    #initial state
    HELLO = auto()

    #state to check if all preferences have been filled
    CHECKPREF = auto()

    #If not all preferences have been filled, ask for the rest of them in a loop
    PREFLOOP = auto()

    #If all preferences have been filled, try to match to data
    MATCHING = auto()

    #NO Match has been found
    NOMATCH = auto()

    #Match(es) have been found
    MATCHSUCCESS = auto()

    #the user has been informed of the match
    USERMATCHED = auto()

    #User has requested data from the match
    FETCHDATA = auto()

    #The request of the user for data of the restaurant could not be forfilled
    NODATA = auto()

    #EXIT state
    EXIT = auto()
    # loop so that the user can give extra requirements 
    REQLOOP = auto()
    #the extra requirements the user gave resulted in 0 matches
    NOEQMATCH = auto()




    #
    #//<<



# --Finite State Machine of dialog system--
@dataclass
class FSM:
#//>>
# class variables:
    #//>>
    model_path: str = "models/lcr_model_dedu.pkl"
    labels_path: str = "models/labels.pkl"
    labels: list[str] = field(init=False)
    current_state: State = State.HELLO
    pref: Preference_Object = field(init=False) 
    ex_req: Extra_Requirement = None
    matches: list[Match] = field(default_factory=list)  
    match_index: int = 0
    reqalts_type: str = "null" 
    asked: Optional[str] = None
    restaurants: Optional[List[Dict]] = None      
    last_request: Optional[List[str]] = None
    new_match_selected: bool = False
    all_caps_config: bool = False # configuration if all sentences should be in all caps
    delay_config: bool = False # Configuration if all sentences should be printed with delay
    informal_config: bool = False # configuration if the system needs to print informa replies
    baseline_config: bool = False # configuration if the system needs to classify using the baselines instead of the ML model
    first_transition: bool = True
    #//<<

   

    def __post_init__(self):
        #//>>
        self.pref = Preference_Object(None, None, None, None, None, None, None)
        self.model = joblib.load(self.model_path)
        self.labels = joblib.load(self.labels_path)
        #//<<

    # ---get speech acts from user input---
    def predict_act(self, user_input: str) -> str:
        #//>>
        bow: np.ndarray = convert_to_bow(user_input.strip().lower())
        bow: np.ndarray = np.array(bow).reshape(1, -1)
        if self.baseline_config:
            return baseline_keywords(user_input)
        else:
            pred_idx: int = int(self.model.predict(bow)[0])
            return self.labels[pred_idx]
        #//<<

    # ---make sure al preferences have been filled---
    def check_preferences_complete(self) -> bool:
        #//>>
        return (
            self.pref.pricerange is not None and
            self.pref.area is not None and
            self.pref.food is not None
        )

    def next_match(self) -> Optional[Match]:
        if not self.matches:
            return None
        m = self.return_match()  # advances index
        if m is not None:
            self.new_match_selected = True
        return m
                                      

    #//<<

    #---update preferences when asked---
    def update_preferences_from_input(self, user_input: str) -> list[str]:
        #//>>
        changed: list[str] = []
        user_pref: Preference_Object = Preference_Object(None, None, None, None, None, None, None)
        new_pref: Preference_Object = extract_preference(user_input, self.asked, user_pref)   # -> Preference_Object

        # --- update pricerange in  pref object
        if new_pref.pricerange is not None:
            if self.pref.pricerange != new_pref.pricerange:
                self.pref.pricerange = new_pref.pricerange
                changed.append("pricerange")

        # --- update area in pref object---
        if new_pref.area is not None:
            if self.pref.area != new_pref.area:
                self.pref.area = new_pref.area
                changed.append("area")

        # -- update food in pref obejct---
        if new_pref.food is not None:
            val = (new_pref.food or "").strip().lower()
            if self.pref.food != val:
                self.pref.food = val
                changed.append("food")

        return changed
    #//<<

    #-- function to check if there is anything mentioned in reqalts---
    def has_any_pref_from_input(self, user_input: str,) -> bool:
        #//>>
        pref = extract_preference(user_input, None, Preference_Object(None, None, None, None, None, None, None))  
        return any(getattr(pref, slot) is not None for slot in ("pricerange", "area", "food"))
        #//<<

    #---match data on csv file, return list of matches---
    def find_matches(self) -> List[Match]:
        #//>>
        rows = filter_restaurants(self.pref)      
        self.restaurants = rows           
        self.matches[:] = [Match.from_row(r) for r in rows]  
        self.match_index = 0
        return self.matches
        #//<<

    #--- return match that has been shown to user-- p.s. we need to do -1 index because return match does + 1
    def active_match(self) -> Optional[Match]:
        #//>>
        idx = self.match_index - 1
        if 0 <= idx < len(self.matches):
            return self.matches[idx]
        return None
        #//<<

    #---return first mtach from list---
    def return_match(self):
        #//>>
        i = self.match_index
        if 0 <= i < len(self.matches):
            self.match_index = i + 1
            return self.matches[i]
        if self.informal_config:
            return f"There are you other restaurants conforming to your requirements, {self.matches[i-1].restaurantname} is the only match."

        return f"Im sorry but there are no other restaurants that conform to your mentioned requirements, unfortunately {self.matches[i-1].restaurantname} is the only match"
        #//<<

    #-- return if the user has No requirements 
    def no_extra_requirements(self):
        #//>>
        if self.ex_req is None:
            return True

        return all( x is None for x in [self.ex_req.assign_seats,self.ex_req.child_friendly,self.ex_req.romantic,self.ex_req.touristic])
        #//<<

    #---return missing pref fields---
    def _missing_slots(self) -> list[str]:
        #//>>
        missing: List[str] = []
        if self.pref.pricerange is None: missing.append("pricerange")
        if self.pref.area is None:       missing.append("area")
        if self.pref.food is None:       missing.append("food")
        return missing
        #//<<

    def check_capitalize(self, input : str) -> str:
        #//>>
        if self.all_caps_config:
            return input.upper()
        else: return input
        #//<<

    #---let the finite state machine handle the input from the console---
    def handle_input(self, user_input: str) -> str:
        #//>>
        self.first_transition = True
        self.transition(user_input)
        prompt: str = self.get_prompt()
        if self.delay_config == True:
            time.sleep(3)
        return self.check_capitalize(prompt)
        #//<<

    #-- extract what has been requested after user is informed of match
    def extract_request(self, userinput: str):
        #//>>
        requests = extract_requirement(userinput)
        return requests
        #//<<

    def extract_extra_requirement(self,userinput: str):
        if not userinput: 
            return None 
        return extract_extra_req(userinput)
    
    #-- match new requirments to old one---
    def merge_extras(self, old: Extra_Requirement | None,
                 new: Extra_Requirement | None) -> Extra_Requirement:
        if old is None:
            old = Extra_Requirement(None, None, None, None)
        if not new:
            return old
        for k, v in vars(new).items():
            if v is not None:           
                setattr(old, k, v)
        return old
    
    #-- check if the requiremts object is empy
    def empty_req(self, req: Extra_Requirement | None) -> bool:
        return (
            req is None or
            all(getattr(req, k, None) is None
                for k in ("touristic", "romantic", "child_friendly", "assign_seats"))
        )

    # function to return a correct prompt provided the requested information of the user, match all requested data en create a flexible string to inform the user
    def get_inform_prompt(self, requested: List[str]) -> str:
        #//>>
        m = self.active_match()
        if not m:
            return "Something went wrong, could not retreive the restaurant data"

        found_bits: list[str] = []
        missing_bits: list[str] = []

        for key in requested:
            val = getattr(m, key, None)
            val_str = (str(val) if val is not None else "").strip()

            if val_str:
                found_bits.append(f"the {key} is {val_str}")
            else:
                missing_bits.append(key)

        if found_bits and not missing_bits:
            return "Sure — " + "; ".join(found_bits) + "."

        if found_bits and missing_bits:
            return (
                "Here’s what I found: " + "; ".join(found_bits) +
                f". I don’t have {', '.join(missing_bits)}."
            )

        if missing_bits:
            return "Sorry, I couldn’t find the" + ", ".join(missing_bits) + " for this restaurant."
        

        if self.informal_config:
            return "Sorry something went wrong, we were not able to retreive the data you asked for."
        else: 
            return "Our deepest apologies but something went wrong, we could not retrieve the data you asked for."
        #//<<

    # --logical transitions between states--
    def transition(self, user_input: str) -> None:
        #//>>
        """transitions object to new state based on user input"""
        act = self.predict_act(user_input)

        # global exit
        #//>>
        if act == "bye":
            self.current_state = State.EXIT
        #//<<

        #global restart
        elif act == "restart":
            #reset the preference object
            self.pref = Preference_Object(None,None,None,None,None,None,None) 
            #reset Requirements
            self.ex_req = None
            self.current_state = State.HELLO

        elif self.current_state == State.HELLO:
            #//>>
            self.current_state = State.CHECKPREF
            self.transition(user_input)
            #//<<

        elif self.current_state == State.CHECKPREF:
            #//>>
            self.update_preferences_from_input(user_input)
            if self.check_preferences_complete():
                self.current_state = State.MATCHING
                self.transition(user_input)
            else:
                self.current_state = State.PREFLOOP
            #//<<

        elif self.current_state == State.PREFLOOP:
            #//>>
            if act == "inform":
                self.update_preferences_from_input(user_input)
            if self.check_preferences_complete():
                self.current_state = State.MATCHING
                self.transition(user_input)
            else:
                self.current_state = State.PREFLOOP
            #//<<

        elif self.current_state == State.MATCHING:
            self.matches = self.find_matches()
            if len(self.matches) > 1:
                self.match_index = 0
                self.current_state = State.REQLOOP
            elif self.matches:
                self.match_index = 0
                self.current_state = State.MATCHSUCCESS
            else:
                self.current_state = State.NOMATCH


        elif self.current_state == State.NOMATCH:
            act = self.predict_act(user_input)
            if act == "reqalts" or act == "inform" or act == "req":
                self.update_preferences_from_input(user_input)
                self.current_state = State.CHECKPREF
                self.transition(user_input)

        elif self.current_state == State.MATCHSUCCESS:
            if act == "reqalts":
                self.current_state = State.MATCHSUCCESS
            else:
                self.current_state = State.USERMATCHED
                self.transition(user_input)

        elif self.current_state == State.REQLOOP: 
            new_eq = self.extract_extra_requirement(user_input)
            self.ex_req = self.merge_extras(self.ex_req, new_eq)
            if self.no_extra_requirements(): # when no requirements continue
                self.current_state = State.MATCHSUCCESS
            elif self.empty_req(new_eq):
                self.current_state = State.MATCHSUCCESS
            else: 
                reqMatch  : List[Match]
                reqMatch = filter_aditional_requirements(self.matches,self.ex_req)
                if len(reqMatch) == 0:
                    self.current_state = State.NOEQMATCH
                else: 
                    self.matches = reqMatch
                    if len(self.matches) == 1:
                        self.match_index = 0
                        self.current_state = State.MATCHSUCCESS
                    else: 
                        self.current_state = State.REQLOOP

        elif self.current_state == State.NOEQMATCH:
            self.current_state = State.REQLOOP


        elif self.current_state == State.USERMATCHED:
            if act == "request":
                self.last_request = self.extract_request(user_input)
                self.current_state = State.FETCHDATA
            if act == "reqalts":
                self.current_state = State.MATCHSUCCESS

        elif self.current_state == State.FETCHDATA:
            self.current_state = State.USERMATCHED
            self.transition(user_input)



        elif self.current_state == State.NODATA:
            self.current_state = State.USERMATCHED
            #//<<
        if act == "reqalts" and self.has_any_pref_from_input(user_input) and self.first_transition:
            self.current_state = State.CHECKPREF
            self.first_transition = False
            self.transition(user_input)

    # ---some states have a standard promt to print----
    def get_prompt(self) -> str:
        if self.current_state == State.HELLO:
          if self.informal_config:
           return "Hi welcom by B2 restaurant finder, give your pricerange, area and foodtype of choice"
          return "Hello, welcome to B2's restaurant finder, please inform us of a pricerange, area and foodtype you are interested in"

        if self.current_state == State.CHECKPREF:
            return ""
        if self.current_state == State.PREFLOOP:
            ms = self._missing_slots()
            if ms:
                self.asked = ms[0]
                if self.informal_config:
                    return f"Tell me your preffered {ms[0]}"
                return f"Could you tell me your preferred {ms[0]}?"
            else:
                return "Got it. Searching…"
        if self.current_state == State.MATCHING:
            return ""
        if self.current_state == State.NOMATCH:
            pref = self.pref
            if self.informal_config:
                return f"I couldn't find a {pref.pricerange} restaurant serving {pref.food} food in the {pref.area} part of town. Do you have an alternative pricerange, area or food?"
            else:
                return f"Deepest apologies but I couldn't find a {pref.pricerange} restaurant serving {pref.food} food in the {pref.area} part of town. Do you have an alternative pricerange, area or food?"
        if self.current_state == State.MATCHSUCCESS:
            m = self.return_match()
            if isinstance(m, str):
                return m
            if self.no_extra_requirements():
                if self.informal_config:
                    return f"I found {m.restaurantname} it has {m.food} for a {m.pricerange} in the {m.area} part of town. Do you need other information about the restaurant?"
                return f"I found a nice restaurant called {m.restaurantname} serving {m.food} food, at a {m.pricerange} price in the {m.area} part of town. Any other information about the restaurant we can help you with?"
            else:
                requirements: dict = explain_requirement(m,self.ex_req)
                reqitem = list(requirements.items())[0]
                if self.informal_config:
                    return f"I found {m.restaurantname} it has {m.food} for a {m.pricerange} in the {m.area} part of town. It is {reqitem[0]} because {reqitem[1]}. Do you need other information about the restaurant?"
                return f"I found a nice restaurant called {m.restaurantname} serving {m.food} food, at a {m.pricerange} price in the {m.area} part of town.The restaurant is {reqitem[0]} because {reqitem[1]}. Any other information about the restaurant we can help you with?"
        if self.current_state == State.USERMATCHED:
            if self.informal_config:
                return f"Thank you for using our service, do you need some other info?"
            return f"Thank you for using our service, any other information about the restaurant i can help you with?"
        if self.current_state == State.FETCHDATA:#something needs to happen that if the data is found it is being returned
            return self.get_inform_prompt(self.last_request)
        
        if self.current_state == State.REQLOOP:
            if self.informal_config:
                return f"We found {len(self.matches)} restaurants that are okey with your preferences. Any other requirements? We can filter on: child friendlyness, romantic and toursitic"
            return f"We currently have found {len(self.matches)} restaurants that comply with your preferences. Would you like to give any additional requirements. We can filter on: child friendlyness, romantic and touristic"
        if self.current_state == State.NOEQMATCH:
            if self.informal_config:
                return "The extra requirements you provided resulted in 0 matches, provide us with new requirements or do not to get the restaurants we found without them"
            else:
                return "Im sorry but the extra requirements you provided resulted in 0 matches, please provide us with new requirements or do not to get the restaurants we found without them"
        if self.current_state == State.EXIT:
            return "Thanks! Goodbye."
        return None
    #//<<
#//<<

# This function contains the keyword baseline for the configurability 'baseline'

def baseline_keywords(utterance: str) -> str:

    words: list[str] = utterance.lower().split()

    # thankyou 
    if "thank" in words or ("thank" in words and "you" in words):
        pred = "thankyou"
    #bye
    elif "goodbye" in words or ("good" in words and "bye" in words) or (words == ["bye"]):
        pred = "bye"
    # restart
    elif "reset" in words or ("start" in words and "over" in words):
        pred = "restart"
    # null 
    elif ("cough" in words or "unintelligible" in words or "tv_noise" in words or "noise" in words or "sil" in words or "uh" in words):
        pred = "null"
    # hello
    elif ("hi" in words) or ("hello" in words) or ("halo" in words):
        pred = "hello"
    # ack
    elif ("okay" in words) or ("kay" in words) or ("good" in words) or ("thatll" in words) or ("fine" in words) or ("well" in words) or ("great" in words):
        pred = "ack"
    # affirm
    elif "yes" in words:
        pred = "affirm"
    # deny
    elif (("i" in words and "dont" in words) or ("dont" in words and "want" in words) or "wrong" in words):
        pred = "deny"
    #negate
    elif ("no" in words) or ("sorry" in words) or ("dont" in words) or ("don't" in words):
        pred = "negate"
    # confirm
    elif (("does" in words and "it" in words) or ("do" in words and "they" in words) or ("is" in words and "there" in words)):
        pred = "confirm"
    # reqalts
    elif (("anything" in words and "else" in words) or ("how" in words and "about" in words) or ("what" in words and "about" in words) or ("else" in words and len(words) <= 3)):
        pred = "reqalts"
    # reqmore
    elif (len(words) == 1 and words[0] == "more"):
        pred = "reqmore"
    # request
    elif (("address" in words) or ("phone" in words) or ("number" in words) or ("postcode" in words) or ("price" in words) or ("area" in words) or ("post" in words and "code" in words)):
        pred = "request"
    # repeat
    elif ("again" in words) or ("repeat" in words) or ("go" in words and "back" in words):
        pred = "repeat"
    # inform
    else:
        pred = "inform"
    
    return pred
