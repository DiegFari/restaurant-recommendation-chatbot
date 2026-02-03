from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


#--Data/Match class--

@dataclass
class Match:
    restaurantname: str
    pricerange: str
    area: str
    food: str
    phone: str
    addr: str
    postcode: str
    assign_seats: str
    child_friendly:str
    romantic: str
    touristic: str
    food_quality:str
    length_of_stay:str
    crowdedness:str
    

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "Match":
        return cls(
            restaurantname=row.get("restaurantname", ""),
            pricerange=row.get("pricerange", ""),
            area=row.get("area", ""),
            food=row.get("food", ""),
            phone=row.get("phone", ""),
            addr=row.get("addr", ""),
            postcode=row.get("postcode", ""),
            assign_seats = row.get("assign_seats",""),
            child_friendly = row.get("child_friendly",""),
            romantic = row.get("romantic",""),
            touristic = row.get("touristic",""),
            food_quality = row.get("food_quality",""),
            length_of_stay= row.get("length_of_stay",""),
            crowdedness = row.get("crowdedness","")

        )
#//<<

class Pricerange(str, Enum):
  #//>>
  CHEAP ="cheap"
  MODERATE ="moderate"
  EXPENSIVE="expensive"
  ANY = "any"
  #//<<


class Area(str,Enum):
  #//>>
  CENTRE = "centre"
  NORTH = "north"
  EAST = "east"
  SOUTH = "south"
  WEST = "west"
  ANY = "any"
  #//<<


class Preference_Object:
  #//>>
  """
  class used to represent the preference of the user to be used in filtering 
  """
  restaurantname: str | None
  pricerange: Pricerange | None
  area : Area | None
  food: str  | None
  phone: str | None
  addr: str | None
  postcode : str | None

  

  def __init__(self,restaurantname : str|None, pricerange: str|None, area: Area|None, food: str|None, phone: str|None, addr:str|None, postcode:str|None):
    #//>>
    self.restaurantname: str | None = restaurantname
    try:  #set the pricerange to one of the ranges in the enum otherwise make it none 
      self.pricerange: str | None =  Pricerange(pricerange.lower()) if pricerange  else None
    except: self.pricerange = None

    try:  # set the area to one of the areas in the enum otherwise set it to none 
      self.area: str | None = Area(area.lower()) if area else None
    except:
      self.area = None
    self.food: str | None = food
    self.phone: str | None = phone
    self.addr: str | None = addr
    self.postcode: str | None = postcode
    #//<<
  #//<<


class Extra_Requirement:
 touristic: bool | None
 romantic: bool  | None
 child_friendly: bool | None 
 assign_seats: bool |None

 def __init__(self,touristic: bool, romantic: bool, child_friendly: bool, assign_seats: bool):
   self.touristic = touristic
   self.romantic = romantic
   self.child_friendly = child_friendly
   self.assign_seats = assign_seats
