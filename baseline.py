
import os
import numpy as np
from sklearn.metrics import classification_report
from bag_of_words import get_BoW_representation


#2 baseline classifying on keywords
#keywords for labels:
#ack : okay, kay, good, 'thatll do', fine, well, great
#affirm	: yes
#bye : bye, goodbye, 'good bye'
#confirm : does, it, do, they, there
#deny : 'i dont', no, not, wrong, 'dont want'
#hello : hi, hello, halo, 
#inform	: "looking for", need, cheap, expensive, food, restaurant, care, price, priced, price, serves, serving
#negate	: no, sorry, dont, 
#null : cough , unintelligible , tv_noise , noise , sil , okay ,uh
#repeat	: again, repeat, back/'go back'
#reqalts : else, how, anything, about, there, is
#reqmore : else, more, there, is
#request : could, can, whats, what, there, address, postcode, is
#restart : start, over, reset, 
#thankyou : thank, you, goodbye, 'thank you good bye', 'thank you bye'

#build dynamic path
dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(dir, "datasets/dialog_acts.dat")

matrix, labels, words = get_BoW_representation()

#baseline 1
y_pred = np.full(shape=25501, fill_value="inform", dtype=object)
print(classification_report(y_true=labels, y_pred=y_pred, target_names = set(labels)))

#baseline 2
y_true2, y_pred2 = [], []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        label = parts[0]
        # lower case
        words = [w.lower().replace("’","'") for w in parts[1:]]
        y_true2.append(label)

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
        elif ("cough" in words or "unintelligible" in words or "tv_noise" in words
              or "noise" in words or "sil" in words or "uh" in words):
            pred = "null"
        # hello
        elif ("hi" in words) or ("hello" in words) or ("halo" in words):
            pred = "hello"
        # ack
        elif ("okay" in words) or ("kay" in words) or ("good" in words) or ("thatll" in words) \
             or ("fine" in words) or ("well" in words) or ("great" in words):
            pred = "ack"
        # affirm
        elif "yes" in words:
            pred = "affirm"
        # deny
        elif (("i" in words and "dont" in words) or ("dont" in words and "want" in words)
              or "wrong" in words):
            pred = "deny"
        #negate
        elif ("no" in words) or ("sorry" in words) or ("dont" in words) or ("don't" in words):
            pred = "negate"
        # confirm
        elif (("does" in words and "it" in words) or
              ("do" in words and "they" in words) or
              ("is" in words and "there" in words)):
            pred = "confirm"
        # reqalts
        elif (("anything" in words and "else" in words) or
              ("how" in words and "about" in words) or
              ("what" in words and "about" in words) or
              ("else" in words and len(words) <= 3)):
            pred = "reqalts"
        # reqmore
        elif (len(words) == 1 and words[0] == "more"):
            pred = "reqmore"
        # request
        elif (("address" in words) or ("phone" in words) or ("number" in words) or
              ("postcode" in words) or ("price" in words) or ("area" in words) or
              ("post" in words and "code" in words)):
            pred = "request"
        # repeat
        elif ("again" in words) or ("repeat" in words) or ("go" in words and "back" in words):
            pred = "repeat"
        # inform
        else:
            pred = "inform"


        y_pred2.append(pred)

print(classification_report(y_true=y_true2, y_pred = y_pred2))
