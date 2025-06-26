from flask import Flask, render_template, request, redirect, url_for, request
import warnings
import pandas as pd
import numpy as np
import pickle
from lib_file import lib_path

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "secret key"

class_names = {0: "Poor", 3: "Average", 2: "Good", 1: "Very Good"}

with open(file="model/state_labels.pkl", mode='rb') as file:
    state_labels = pickle.load(file=file)

with open(file="model/season_labels.pkl", mode='rb') as file:
    season_labels = pickle.load(file=file)

with open(file="model/crop_labels.pkl", mode='rb') as file:
    crop_labels = pickle.load(file=file)

with open(file='model/KNeighborsClassifier_model.pkl', mode='rb') as file:
    class_model = pickle.load(file=file)

with open(file='model/RandomForestRegressor_model.pkl', mode='rb') as file:
    pred_model = pickle.load(file=file)

state_data = state_labels
season_data = season_labels
crop_data = crop_labels


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        state = request.form['q1']
        season = request.form['q2']
        crop = request.form['q3']
        area = float(request.form['q4'])
        rainfall = float(request.form['q5'])

        state1 = state_labels[state]
        season1 = season_labels[season]
        crop1 = crop_labels[crop]
        input_data = [state1, season1, crop1, area, rainfall]
        print(input_data)

        class_pred = class_model.predict([input_data])
        print(class_pred)
        prediction = class_names[class_pred[0]]
        print("Result : ", prediction)
        msg = 'Crop Yield Prediction is :'
        print(state_labels)
        return render_template("index1.html", prediction=prediction, msg=msg, state_data=state_data,
                               season_data=season_data, crop_data=crop_data)


@app.route('/classification', methods=['post', 'Get'])
def classify():
    if request.method == 'POST':
        state = request.form['q1']
        season = request.form['q2']
        state2 = state_labels[state]
        season2 = season_labels[season]
        pred_data = [state2, season2]
        print(pred_data)
        reg_pred = pred_model.predict([pred_data])
        print(reg_pred)
        prediction = round(reg_pred[0], 2)
        print("Rainfall : ", prediction)
        msg = 'Rain fall Prediction in {} , in the season of {} is :'.format(state, season)
        return render_template("index1.html", prediction=prediction, msg=msg, state_data=state_data,
                               season_data=season_data, crop_data=crop_data)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        graph_name = request.form['text']
        graph = ''
        name = ''
        if graph_name == "classification1":
            name = "kneighbors_classification_report"
            graph = "static/graph/kneighbors_classification_report.PNG"
        elif graph_name == 'classification2':
            name = "RidgeClassifier_classification_report"
            graph = "static/graph/RidgeClassifier_classification_report.PNG"
        elif graph_name == 'confusion1':
            name = "kneighbors_confusionmatrix"
            graph = "static/graph/kneighbors_confusionmatrix.png"
        elif graph_name == 'confusion2':
            name = "ridgeclassifier_Confusionmatrix"
            graph = "static/graph/ridgeclassifier_confusionmatrix.png"
        elif graph_name == 'result':
            name = "prediction_result"
            graph = "static/graph/prediction_result.png"
        elif graph_name == 'crop':
            name = "crop"
            graph = "static/graph/crop.png"
        elif graph_name == 'season':
            name = "season"
            graph = "static/graph/season.png"
        elif graph_name == 'state':
            name = "state"
            graph = "static/graph/state.png"
        return render_template('graphs.html', name=name, graph=graph)


@app.route('/back', methods=['POST', 'GET'])
def back():
    return render_template('index1.html', state_data=state_data, season_data=season_data, crop_data=crop_data)


@app.route("/")
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print("Form Data Received:", request.form)
        
        email = request.form["email"]
        pwd = request.form["password"]
        
        print("Email:", email)
        print("Password:", pwd)
        print("---------------------------")
        
        r1 = pd.read_excel('user.xls')

        user_exists = ((r1["email"] == email) & (r1["password"] == pwd)).any()

        if user_exists:
            return redirect(url_for("back"))
        else:
            msg = 'Invalid Login. Try Again'
            return render_template('login.html', msg=msg)

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['Email']
        password = request.form['Password']
        col_list = ["name", "email", "password"]
        r1 = pd.read_excel('user.xls', usecols=col_list)
        new_row = {'name': name, 'email': email, 'password': password}
        r1 = r1.append(new_row, ignore_index=True)
        r1.to_excel('user.xls', index=False)
        print("Records created successfully")
        msg = 'Registration Successful !! U Can login Here !!!'
        return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/graphs', methods=['POST', 'GET'])
def graphs():
    return render_template('graphs.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
