from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import  SQLAlchemy
import joblib
import numpy as np
import pytz
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'This is flower'
db = SQLAlchemy(app)
app.app_context().push()

# For creating table 
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sepal_length = db.Column(db.Float, nullable =False)
    sepal_width = db.Column(db.Float, nullable =False)
    petal_length = db.Column(db.Float, nullable=False)
    petal_width = db.Column(db.Float, nullable=False)
    flower = db.Column(db.String(56), nullable =False)
    indian_time = pytz.timezone('Asia/Kolkata')
    created = db.Column(db.DateTime, default = datetime.now(indian_time), nullable =False)

    def __repr__(self):
        return f"Sepal_Length : {self.sepal_length}"

@app.route('/')
def index():
    return render_template('index.html')

flower_class = {0 : 'Iris setosa' ,
                1 :'Iris versicolor',
                2 : 'Iris virginica'}

model = joblib.load('flower_model.joblib')

# For the Prediction
@app.route('/prediction', methods =['GET', 'POST'])
def prediction():
    if request.method =='POST':
        
        # Take data from the form
        sepal_length = float(request.form['sepal_length'])
        sepal_width = float(request.form['sepal_width'])
        petal_length = float(request.form['petal_length'])
        petal_width = float(request.form['petal_width'])    

        # print(sepal_length, sepal_width, petal_length, petal_width)
        
        # Convert the feature variable to an numpy array
        feature = np.array([sepal_length, sepal_width, petal_length, petal_width])
        
        # Predict the result using model this will return the class label like 0, 1 and 2
        predict = model.predict([feature])
        # print(predict[0])
        # We use the predict as key to search the value from flower class dictionary
        predict_class = flower_class[predict[0]]
        # print(predict_class)
        
        user = User(sepal_length = sepal_length, sepal_width =sepal_width, petal_length=petal_length, petal_width=petal_width,
                    flower  = predict_class)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Your data has been saved.', "success")
            redirect('/')
        except Exception as e:
            flash("An Error occured while saving your data", 'danger')
            print(str(e))
            return redirect(url_for('index'))
            
        return render_template('index.html', predict = f"This data refers to {predict_class} this class.")
    
    
    
if __name__ == "__main__":
    app.run(debug=True)