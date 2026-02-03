"""
In this file I put together all the machine learning models constructed as well as the evaluation of them
"""
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from bag_of_words import get_BoW_representation, encode_labels, convert_to_bow, data_statystics
from sklearn.metrics import classification_report, log_loss
import matplotlib.pyplot as plt
import numpy as np 
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import joblib

# 0. Print the statystics of the dataset as required by the report: 

avrg_utterance_length, labels_distribution = data_statystics()

print("DATA STATYSTICS:\n\n")
print(f"Average utterance lenght: {avrg_utterance_length}\n")
print(f"Labels distribution:\n{labels_distribution}\n\n")



# 1. get the feature set and the test set:

X, labels, _ = get_BoW_representation(output_name="datasets/output_original.json")
X_dedu, labels_dedu, _ = get_BoW_representation(output_name="datasets/output_dedu.json", unique= True)
y , unique = encode_labels(json_path="datasets/output_original.json")
y_dedu, unique_dedu = encode_labels(json_path="datasets/output_dedu.json")
#turn the labels into integers to instead of vectors
y_int = np.argmax(y, axis =1 )
y_int_dedu= np.argmax(y_dedu, axis =1)
n_labels = len(unique) 
n_labels_dedu = len(unique_dedu)


# 2. construct the training-, validation- & test-set taken from the decision tree file

X_train, X_test, y_train, y_test = train_test_split(X, y_int, test_size=0.15, random_state=1)
X_train_dedu, X_test_dedu, y_train_dedu, y_test_dedu = train_test_split(X_dedu, y_int_dedu, test_size=0.15, random_state=1)


# 3. DECISION TREE


decision_tree:  DecisionTreeClassifier = DecisionTreeClassifier(criterion="gini",
                                                                splitter="best",
                                                                max_depth=None,
                                                                random_state=0
                                                                )

decision_tree_dedu: DecisionTreeClassifier= DecisionTreeClassifier(criterion="gini",
                                                                   splitter="best",
                                                                   max_depth=None,
                                                                   random_state=0)

# train the tree:
decision_tree.fit(X=X_train, y=y_train)
decision_tree_dedu.fit(X=X_train_dedu, y=y_train_dedu)

# make some predictions over the validation set:
y_pred = decision_tree.predict(X_test)
y_pred_prob = decision_tree.predict_proba(X_test)

y_pred_dedu = decision_tree_dedu.predict(X_test_dedu)
y_pred_prob_dedu = decision_tree_dedu.predict_proba(X_test_dedu)


# generate classification report and calculate log_loss
report_DT = classification_report(y_true = y_test, y_pred = y_pred, labels=np.arange(n_labels), target_names = unique)
logged_loss_DT = log_loss(y_test, y_pred_prob, labels= np.arange(n_labels))

report_DT_dedu = classification_report(y_true = y_test_dedu, y_pred = y_pred_dedu, labels = np.arange(n_labels_dedu), target_names= unique_dedu)
logged_loss_DT_dedu = log_loss(y_test_dedu, y_pred_prob_dedu, labels= np.arange(n_labels_dedu))

# plot decision tree:
plot_tree(decision_tree)
#plt.show() (uncomment in case you wanna see the plot)


# 4. RANDOM FOREST 

random_forest: RandomForestClassifier = RandomForestClassifier(criterion="gini",
                                                                max_depth=None,
                                                                random_state=0
                                                                )

random_forest_dedu: RandomForestClassifier = RandomForestClassifier(criterion="gini",
                                                                max_depth=None,
                                                                random_state=0
                                                                )

random_forest.fit(X=X_train, y=y_train)
random_forest_dedu.fit(X=X_train_dedu, y=y_train_dedu)

y_pred = random_forest.predict(X_test)
y_pred_prob = random_forest.predict_proba(X_test)

y_pred_dedu = random_forest_dedu.predict(X_test_dedu)
y_pred_prob_dedu = random_forest_dedu.predict_proba(X_test_dedu)


# generate classification report and calculate log_loss
report_RF = classification_report(y_true = y_test, y_pred = y_pred, labels=np.arange(n_labels), target_names = unique)
logged_loss_RF = log_loss(y_test, y_pred_prob, labels= np.arange(n_labels))

report_RF_dedu = classification_report(y_true = y_test_dedu, y_pred = y_pred_dedu, labels=np.arange(n_labels_dedu), target_names=unique_dedu)
logged_loss_RF_dedu = log_loss(y_test_dedu, y_pred_prob_dedu, labels = np.arange(n_labels_dedu))


# 5. LOGISTIC REGRESSION

lcr = LogisticRegression(random_state=0)
lcr_dedu = LogisticRegression(random_state=0)

lcr.fit(X = X_train, y = y_train)
lcr_dedu.fit(X = X_train_dedu, y = y_train_dedu)

y_pred = lcr.predict(X_test)
y_pred_prob = lcr.predict_proba(X_test)

y_pred_dedu = lcr_dedu.predict(X_test_dedu)
y_pred_prob_dedu = lcr_dedu.predict_proba(X_test_dedu)


# generate classification report and calculate log_loss
report_lr = classification_report(y_true = y_test, y_pred = y_pred, labels=np.arange(n_labels), target_names = unique)
logged_loss_lr = log_loss(y_test, y_pred_prob, labels= np.arange(n_labels))

report_lr_dedu = classification_report(y_true = y_test_dedu, y_pred = y_pred_dedu, labels=np.arange(n_labels_dedu), target_names=unique_dedu)
logged_loss_lr_dedu = log_loss(y_test_dedu, y_pred_prob_dedu, labels= np.arange(n_labels_dedu))

# 6. MULTI LAYER PERCEPTRON

multi_layer_perceptron = MLPClassifier(solver='adam', alpha=1e-5,
                    hidden_layer_sizes=(64,32), random_state=1)
multi_layer_perceptron_dedu = MLPClassifier(solver='adam', alpha=1e-5,
                     hidden_layer_sizes=(64,32), random_state=1)

multi_layer_perceptron.fit(X = X_train, y = y_train)
multi_layer_perceptron_dedu.fit(X = X_train_dedu, y = y_train_dedu)

y_pred= multi_layer_perceptron.predict(X_test)
y_pred_prob = multi_layer_perceptron.predict_proba(X_test)

y_pred_dedu = multi_layer_perceptron_dedu.predict(X_test_dedu)
y_pred_prob_dedu = multi_layer_perceptron_dedu.predict_proba(X_test_dedu)


# generate classification report and calculate log_loss
report_MLP = classification_report(y_true = y_test, y_pred = y_pred, labels=np.arange(n_labels), target_names = unique)
logged_loss_MLP = log_loss(y_test, y_pred_prob, labels = np.arange(n_labels))

report_MLP_dedu = classification_report(y_true = y_test_dedu, y_pred = y_pred_dedu, labels= np.arange(n_labels_dedu), target_names = unique_dedu)
logged_loss_MLP_dedu = log_loss(y_test_dedu, y_pred_prob_dedu, labels = np.arange(n_labels_dedu))

# dumping all the models on joablib
labels_list = unique.tolist() if hasattr(unique, "tolist") else list(unique)
labels_list_dedu = unique_dedu.tolist() if hasattr(unique_dedu, "tolist") else list(unique_dedu)
joblib.dump(labels_list, "models/labels.pkl")
joblib.dump(labels_list_dedu, "models/labels_dedu.pkl")
joblib.dump(lcr, "models/lcr_model.pkl")
joblib.dump(lcr, "models/lcr_model_dedu.pkl")

# 7. PRINT THE REPORTS AND LOG_LOSS FOR EACH MODEL (in both versions)
print("\n\nClassification report and log_loss for DECISION TREE on original dataset: \n")
print(report_DT)
print("logged loss = ",logged_loss_DT)

print("\n\nClassification report and log_loss for DECISION TREE on deduplicated dataset: \n")
print(report_DT_dedu)
print("logged loss = ",logged_loss_DT_dedu)

print("\n\nClassification report and log_loss for RANDOM FOREST on original dataset: \n")
print(report_RF)
print("logged loss = ",logged_loss_RF)

print("\n\nClassification report and log_loss for RANDOM FOREST on deduplicated dataset: \n")
print(report_RF_dedu)
print("logged loss = ",logged_loss_RF_dedu)


print("\n\nClassification report and log_loss for LOGISTIC REGRESSION on original dataset: \n")
print(report_lr)
print("logged loss = ",logged_loss_lr)

print("\n\nClassification report and log_loss for LOGISTIC REGRESSION on deduplicated dataset: \n")
print(report_lr_dedu)
print("logged loss = ",logged_loss_lr_dedu)

print("\n\nClassification report and log_loss for MULTI LAYER PERCEPTRON on original dataset: \n")
print(report_MLP)
print("logged loss = ", logged_loss_MLP)

print("\n\nClassification report and log_loss for MULTI LAYER PERCEPTRON on deduplicated dataset: \n")
print(report_MLP_dedu)
print("logged loss = ", logged_loss_MLP_dedu)

# defining a function to run the model on user input
def predict_from_input (model, labels, file_path):

    while True:
        #get the input and verify if the user doesn't wanna exit
        print('Instert a new sentence to be labeled (press "exit" to end):\n')
        sentence = input()
        if sentence == 'exit':
            print('END')
            break
        #convert the input sentence to a bow
        bow = convert_to_bow(sentence, json_path=file_path)
        #reshape the bow to make it usable for regression
        bow = np.array(bow).reshape(1, -1)
        #predict
        prediction =  model.predict(bow)
        print(prediction)
        #print the label of the prediction
        print(labels[prediction[0]])

# Testing difficult utterances from the dataset 

difficult_utterances = ["any thing else", "um doesnt matter if its in the center of the town"]

print("\n\nTESTING MODELS (DEDU VERSION) ON DIFFICULT UTTERANCES FOUND IN THE DATASET\n")
print(f"\nDifficult utterance 1 (session id: voip-88f198881b-20130326_032851):\n{difficult_utterances[0]}")

bow = convert_to_bow(difficult_utterances[0], json_path="datasets/output_original.json")

bow = np.array(bow).reshape(1, -1)
prediction =  decision_tree_dedu.predict(bow)
print(f"Prediction with decision tree {unique_dedu[prediction[0]]}")

prediction =  random_forest_dedu.predict(bow)
print(f"Prediction with random forest {unique_dedu[prediction[0]]}")

prediction =  lcr_dedu.predict(bow)
print(f"Prediction with logistic regression {unique_dedu[prediction[0]]}")

prediction =  multi_layer_perceptron_dedu.predict(bow)
print(f"Prediction with multi layer perceptron {unique_dedu[prediction[0]]}")

print(f"Difficult utterance 2 (session id: voip-b20968d1ea-20130323_112309):\n{difficult_utterances[1]}")

bow = convert_to_bow(difficult_utterances[1], json_path="datasets/output_original.json")

bow = np.array(bow).reshape(1, -1)
prediction =  decision_tree_dedu.predict(bow)
print(f"Prediction with decision tree {unique_dedu[prediction[0]]}")

prediction =  random_forest_dedu.predict(bow)
print(f"Prediction with random forest {unique_dedu[prediction[0]]}")

prediction =  lcr_dedu.predict(bow)
print(f"Prediction with logistic regression {unique_dedu[prediction[0]]}")

prediction =  multi_layer_perceptron_dedu.predict(bow)
print(f"Prediction with multi layer perceptron {unique_dedu[prediction[0]]}")


triggering_utterances = ["i dont want a chinese restaurant", "bye bye north east.", "give me east part of food."]

print("\n\nTESTING MODELS (DEDU VERSION) BY MEANS OF TRIGGERING UTTERANCES PURPOSELY CREATED\n")
print(f"\nTriggering utterance 1: {triggering_utterances[0]}")

bow = convert_to_bow(triggering_utterances[0], json_path="datasets/output_original.json")

bow = np.array(bow).reshape(1, -1)
prediction =  decision_tree_dedu.predict(bow)
print(f"Prediction with decision tree {unique_dedu[prediction[0]]}")

prediction =  random_forest_dedu.predict(bow)
print(f"Prediction with random forest {unique_dedu[prediction[0]]}")

prediction =  lcr_dedu.predict(bow)
print(f"Prediction with logistic regression {unique_dedu[prediction[0]]}")

prediction =  multi_layer_perceptron_dedu.predict(bow)
print(f"Prediction with multi layer perceptron {unique_dedu[prediction[0]]}")

print(f"Triggering utterance 2: {triggering_utterances[1]}")

bow = convert_to_bow(triggering_utterances[1], json_path="datasets/output_original.json")

bow = np.array(bow).reshape(1, -1)
prediction =  decision_tree_dedu.predict(bow)
print(f"Prediction with decision tree {unique_dedu[prediction[0]]}")

prediction =  random_forest_dedu.predict(bow)
print(f"Prediction with random forest {unique_dedu[prediction[0]]}")

prediction =  lcr_dedu.predict(bow)
print(f"Prediction with logistic regression {unique_dedu[prediction[0]]}")

prediction =  multi_layer_perceptron_dedu.predict(bow)
print(f"Prediction with multi layer perceptron {unique_dedu[prediction[0]]}")

print(f"Triggering utterance 3: {triggering_utterances[2]}")

bow = convert_to_bow(triggering_utterances[2], json_path="datasets/output_original.json")

bow = np.array(bow).reshape(1, -1)
prediction =  decision_tree_dedu.predict(bow)
print(f"Prediction with decision tree {unique_dedu[prediction[0]]}")

prediction =  random_forest_dedu.predict(bow)
print(f"Prediction with random forest {unique_dedu[prediction[0]]}")

prediction =  lcr_dedu.predict(bow)
print(f"Prediction with logistic regression {unique_dedu[prediction[0]]}")

prediction =  multi_layer_perceptron_dedu.predict(bow)
print(f"Prediction with multi layer perceptron {unique_dedu[prediction[0]]}")


# predicting user input
while True:
    print("\nWhich model do you want to run ?\n1: DECISION TREE \n2: RANDOM FOREST \n3: LOGISTIC REGRESSION \n4: MULTI LAYER PERCEPTRON \n5: exit\n")
    choice = input()

    if choice == "1": 
        print("If you want to use the model trained on the original dataset press 1, if you want to use the model trained on the deduplicated dataset press 2:")
        choice = input()
        if choice == "1":
            predict_from_input(decision_tree, unique, "datasets/output_original.json")
        if choice =="2":
            predict_from_input(decision_tree_dedu, unique_dedu, "datasets/output_dedu.json")
    elif choice == "2": 
        print("If you want to use the model trained on the original dataset press 1, if you want to use the model trained on the deduplicated dataset press 2:")
        choice = input()
        if choice == "1":
            predict_from_input(random_forest, unique, "datasets/output_original.json")
        if choice =="2":
            predict_from_input(random_forest_dedu, unique_dedu, "datasets/output_dedu.json")
    elif choice == "3": 
        print("If you want to use the model trained on the original dataset press 1, if you want to use the model trained on the deduplicated dataset press 2:")
        choice = input()
        if choice == "1":
            predict_from_input(lcr, unique, "datasets/output_original.json")
        if choice =="2":
            predict_from_input(lcr_dedu, unique_dedu, "datasets/output_dedu.json")
    elif choice == "4": 
        print("If you want to use the model trained on the original dataset press 1, if you want to use the model trained on the deduplicated dataset press 2:")
        choice = input()
        if choice == "1":
            predict_from_input(multi_layer_perceptron, unique, "datasets/output_original.json")
        if choice =="2":
            predict_from_input(multi_layer_perceptron_dedu, unique_dedu, "datasets/output_dedu.json")
    elif choice == "5": 
        break


