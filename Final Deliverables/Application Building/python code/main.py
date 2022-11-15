from flask import Flask,request, url_for, redirect, render_template,session
from flask_cors import CORS,cross_origin
from werkzeug.utils import secure_filename
import pickle
import numpy as np
import pandas as pd
import os
UPLOAD_FOLDER = os.path.join('static', 'uploads')
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, template_folder='templates', static_folder='static')
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'This is your secret key to utilize session in Flask'
@app.route('/')
def hello_world():
    return render_template("index.html")
@app.route('/home')
def home():
    return render_template("index.html")
@app.route('/login')
def login():
    return render_template("login.html")
@app.route('/form_login',methods=['POST','GET'])
def login1():
    database={'user1':'1234','user2':'abcd','admin':'admin'}
    name1=request.form['username']
    pwd=request.form['password']
    if name1 not in database:
        return render_template('login.html',info='Invalid User')
    else:
         if database[name1]!=pwd:
             return render_template('login.html',info='Invalid password')
         else:
             # return render_template('login.html',info='login Successfull')
             return render_template('upload.html',name=name1)
@app.route('/upload')
def upload_file():
    return render_template('upload.html')
@app.route('/', methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']

        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)

        # flask upload file to database (defined uploaded folder in static path)
        uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))

        # Storing uploaded file path in flask session
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

        return render_template('upload2.html')
@app.route('/show_data')
def showData():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)

    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # pandas dataframe to html table flask
    uploaded_df_html = uploaded_df.to_html()
    return render_template('preview.html', data_var=uploaded_df_html)
@app.route('/input_data',methods=['GET'])  # route to display the home page
@cross_origin()
def inputPage():
    return render_template("form1.html")
@app.route('/predict',methods=['POST','GET']) # route to show the predictions in a web UI
@cross_origin()
def predpage():
    if request.method == 'POST':
        try:
            #  reading the inputs given by the user
            gre_score=float(request.form['gre_score'])
            toefl_score = float(request.form['toefl_score'])
            university_rating = float(request.form['university_rating'])
            sop = float(request.form['sop'])
            lor = float(request.form['lor'])
            cgpa = float(request.form['cgpa'])
            is_research = request.form['research']
            if(is_research=='yes'):
                research=1
            else:
                research=0
            filename = 'final_model.pickle'

            # loading the model file from the storage
            loaded_model = pickle.load(open(filename, 'rb'))

            # predictions using the loaded model file
            prediction=loaded_model.predict([[gre_score,toefl_score,university_rating,sop,lor,cgpa,research]])
            print('prediction is', prediction)

            # showing the prediction results in a UI
            return render_template('results.html',prediction=round(100*prediction[0]))
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')
    else:
        return render_template('form1.html')
if __name__ == '__main__':
    app.run(debug=True)

