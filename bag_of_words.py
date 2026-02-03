"""
This file contains all the code related to the construction of the BoW-representation of the dataset, 
as well as functions that require some kind of interaction with the BoW-data, 
whether that be the matrix, token list or the list of labels.

COPY IF YOU WANT THE FOLLOWING:
1. only the bag-of-words matrix:
-> matrix_name, _, _ = get_BoW_representation()

2. only the list of corresponding labels:
-> _, label_list, _ = get_BoW_representation()

3. only the list of unique words (in lowercase)
-> _, _, token_list = get_BoW_representation()

4. convert a document to BoW row:
-> converted_doc = convert_to_bow(<doc variable>)

5. encode the labels to one-hot encoding:
-> encoded_labels = encode_labels()

6. Get some statystics on the data:
-> avrg_utterance_length, lables_distribution = data_statystics()
"""

# imports:
#//>>
from typing import List, Set, Tuple
import json
import numpy as np
from keras.utils import to_categorical
import os
from sklearn.model_selection import train_test_split
#//<<

def get_BoW_representation(file_name: str = "datasets/dialog_acts.dat", output_name: str = "datasets/output_original.json", unique: bool = False) -> Tuple[np.ndarray, List[str], List[str]]:
    #//>>
    """
    This function generates a BoW representation of the dialog_acts.dat file. 
    It returns a tuple containing the BoW matrix,  a list of labels corresponding to the rows, 
    and a list of the unique words in the corpus IN THAT ORDER.
    """
    # 0. get the data & variables ready
    # ---------------------------------------------
    dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir, file_name)
    with open(file_path, encoding="utf-8") as file:
        lines: List[str] = file.readlines()

    unique_docs: Set[List[str]] = set()
    labels: List[str] = []
    total_set: Set[str] = set()
    docu_lists: List[Tuple[str]] = []
    # /////////////////////////////////////////////

    # 1. iterate over line
    for line in lines:
    # ---------------------------------------------
        # 2. use .split() to get list of words
        line = line.strip()
        docu_list: List[str] = line.split(" ")

        # 3. remove label 
        label = docu_list.pop(0)
        # 3.5 save list into document_lists
        labels.append(label)

        # 3.6 check whether sentence is unique. Toss out if not:
        if unique:
            doc_tuple: Tuple[str] = tuple(docu_list)
            if doc_tuple in unique_docs:
                labels.pop()
                continue
            else:
                unique_docs.add(doc_tuple)

        # 4. turn list into set
        docu_set: Set[str] = set(docu_list)

        # 5. add to total_set docu_lists:
        total_set  = total_set.union(docu_set)
        docu_lists.append(docu_list)
    # /////////////////////////////////////////////

    # 6.  turn total_set into total_list:
    total_list: List[str] = ["UNKNOWN"] + list(total_set) #add the unknown word for unkown characters

    # 7.  save total_list
    with open(output_name, "w") as label_file:
        json.dump({"labels": labels, "index_list": total_list}, label_file, indent=4)

    # 8. iterate over document_lists:
    doc_vectors: List[np.ndarray] = []
    vector_size: int = len(total_list) 

    # for each document we:
    for doc_list in docu_lists:
    # ---------------------------------------------
        # 9. instantiate a zero-vector
        doc_vector = np.zeros(vector_size)

        # 10. increment the positions of the zero-vector based on tokens their index in total_list 
        for word in doc_list:
        # ---------------------------------------------
            word_idx: int = total_list.index(word)
            doc_vector[word_idx] += 1
        # /////////////////////////////////////////////

        # 11. "append" it to the "matrix"
        doc_vectors.append(doc_vector)
    # /////////////////////////////////////////////

    bow_matrix: np.ndarray = np.array(doc_vectors)
    np.save("datasets/bow_matrix.npy", bow_matrix)

    return (bow_matrix, labels, total_list)
    #//<<


def convert_to_bow(document: str, json_path: str = "datasets/output_original.json") -> np.ndarray:
    #//>>
    """This function converts a document to the bag-of-words representation 
    based in order to be of a similar format as the training data"""
    # 1. import the index list from the json file:
    with open(json_path, encoding="utf-8") as json_file:
        index_list: List[str] = json.load(json_file)["index_list"]

    # 2. create the BoW-version of the document (zero-vector with same amount of elements as the index list)
    bow_document: np.ndarray = np.zeros(len(index_list) ) 

    # 3. increment vector's element at word's corresponding position in index_list
    # ---------------------------------------------
    for word in document.strip().lower().split(" "):
        try:
            word_idx = index_list.index(word)
        except ValueError:
            word_idx = 0
        bow_document[word_idx]+=1
    # /////////////////////////////////////////////

    return bow_document
    #//<<

def encode_labels(json_path: str = "datasets/output_original.json"):
    #//>>
    """
    --> if you want the labels for the dataset, encoded & well, use this method <---
    this function converts the standard list of labels into a list of one-hot-encoded variants.
    """
    # 1. get the label list
    with open(json_path, "r", encoding="utf-8") as label_file:
        labels: List[str] = json.load(label_file)["labels"]

    # 2. extract the unique values from the list of labels:
    unique_labels: List[str] = sorted( list(set(labels)))
  


    # 3. map each label to its corresponding labels
    numbered_labels: List[int] = list(map(lambda x: unique_labels.index(x), labels))

    # 4. convert the numbered labels into one-hot-encoded ones:
    encoded_labels = to_categorical(numbered_labels, num_classes = len(unique_labels))
    #return np.asarray(encoded_labels)
    return encoded_labels,unique_labels #also return the unique labels for making predictions
    #//<<



def data_statystics(file_name: str = "datasets/dialog_acts.dat") -> Tuple[int, dict]:
    """
    This function serves to generate the statystics of the data for the report.
    It runs on the json file and it returns:
    - average utterance lenghts
    - Labels distribution
    """

    # 0. Read the dataset

    dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir, file_name)
    with open(file_path, encoding="utf-8") as file:
        lines: List[str] = file.readlines()

    # 1. Calculate average utterance length 

    lengths = np.array([])
    labels = []

    for l in lines: 
        tokens = l.split()
        labels.append(tokens[0])
        l = " ".join(tokens[1:]) # this is to get rid of the first word, which is the label
        lengths = np.append(lengths, len(l))
    
    avg_utterance_lenght = np.mean(lengths)

    # 2. Calculate labels distribution

    labels_distribution = dict()

    for l in labels: 
        if l in labels_distribution:
            labels_distribution[l] += 1
        else: 
            labels_distribution[l] = 1

    n_labels = len(labels)

    for l in labels_distribution:
        labels_distribution[l] = labels_distribution[l] / n_labels
    

    return avg_utterance_lenght, labels_distribution

    
