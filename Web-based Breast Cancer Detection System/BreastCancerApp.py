from flask import Flask, render_template,request, redirect , url_for
import numpy as np
from sklearn import svm , cross_validation
import pandas as pd
import sqlite3
import os.path
import pygal
from plotly.offline import plot
from plotly.graph_objs import Scatter
from random import randint


result = []
example = []
#Pre-processing step

#data = pd.read_csv('~/PycharmProjects/BreastCancerApp/breast-cancer-wisconsin.csv')
#df = pd.DataFrame(data)
#newdf=df.replace('?', np.NaN)
#newdf = newdf.dropna(axis=0,how='any')
#newdf.to_csv('~/PycharmProjects/BreastCancerApp/breast-cancer-data-filtered.csv')

data = pd.read_csv('~/PycharmProjects/BreastCancerApp/breast-cancer-data-filtered.csv')

df = pd.DataFrame(data)
# al array by3tbroha fel python zy al estowana y3ny -1 btdek al element al a5er
train_features = df.iloc[:,2:-1]
train_target = df.iloc[:,-1]
# y_train btomasel al target aly hya 0 aw 1 wel x_train btmasel al dataset bt3tna
X_train, X_test, y_train, y_test = cross_validation.train_test_split(train_features, train_target,
                                                                                    test_size=0.2)
# svc support vector classifier takes one parameter(kernal aly hwa al 5t aly byfsel been al data)
svm_clf = svm.SVC(kernel='linear')
# al 5twa aly bndy feha kol x al label bta3to swa2 1 or 0
svm_clf.fit(X_train,y_train)

accuracyScore = svm_clf.score(X_test,y_test)
print(accuracyScore)

#application configuration
DEBUG = True
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "BreastCancer-DB")
with sqlite3.connect(db_path ,check_same_thread=False) as db:
    c = db.cursor()

@app.route('/graph')

def graph():

     data = pd.read_csv('~/PycharmProjects/BreastCancerApp/breast-cancer-data-filtered.csv')
     df = pd.DataFrame(data)
     df['age'] = np.random.randint(1, 100, df.shape[0])
     df['state'] = np.random.randint(5, size=len(df))
     n = df['state'].value_counts()


     print(n)
     graph = pygal.Bar(height = 500)
     graph.add('cairo',n[0])
     graph.add('giza',n[1])
     graph.add('alexandria',n[2])
     graph.add('Luxor', n[3])
     graph.add('Aswan', n[4])


     graph.title = 'Statistics of Breast Cancer in different states of Egypt'




     graph_data = graph.render_data_uri()
     return render_template("adminview.html", graph_data=graph_data)

@app.route("/home", methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        if request.form['result']:
            pid = request.form.get('patient_id')
            pname = request.form.get('patient_name')
            state = request.form.get('state')
            age = request.form.get('patient_age')
            feature1 = request.form.get('f1')
            feature2 = request.form.get('f2')
            feature3 = request.form.get('f3')
            feature4 = request.form.get('f4')
            feature5 = request.form.get('f5')
            feature6 = request.form.get('f6')
            feature7 = request.form.get('f7')
            feature8 = request.form.get('f8')
            feature9 = request.form.get('f9')

            example = [feature1, feature2 , feature3,
                       feature4,feature5,feature6,feature7,
                       feature8,feature9]

# deh al prediction bt3 al data bt5od al example aly ktbnah fel web app we btda5alo 3la al data wtkarno
            result = svm_clf.predict(np.array(example).reshape(1,9))


            if result == 2:
                result = 'Benign'
            else:
                result = 'malegnint'
            if pid and pname and state and age:
                c.execute("SELECT * FROM Patient_info "
                          "WHERE pid = '{}' ".format(pid))


                if c.fetchone() is None:

                    query = c.execute("INSERT INTO Patient_info (pid,p_name"
                          ",p_state,p_result,p_age) VALUES ('{}','{}','{}','{}','{}')".format(pid, pname,
                                                                                    state,result,age))
                    if query:
                        db.commit()
                        return render_template('home.html',variable = result)
                else:
                    return render_template('home.html',variable = 'Patient {} already exist'.format(pname))

    return render_template('home.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.form['Signup']:
            name = request.form.get('doc_name')
            username = request.form.get('doc_username')
            password = request.form.get('doc_pass')
            if name and username and password:
                c.execute("SELECT * FROM Doctors_info "
                                   "WHERE doctor_name = '{}' "
                                   "and doctor_username = '{}' "
                                   "and doctor_password = '{}' ".format(name,username,password))

                if c.fetchone() is None:

                    query = c.execute("INSERT INTO Doctors_info (doctor_name,doctor_username"
                          ",doctor_password) VALUES ('{}','{}','{}')".format(name,username,password))

                    if(query):
                        db.commit()
                        return render_template('login.html')
                else:

                    return render_template('signup.html', variable = 'Username or password already exist')
    return render_template('signup.html')



@app.route("/", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        if request.form['Login']:
           username = request.form.get('name')
           userpass = request.form.get('pass')
           if username and userpass:
                c.execute("SELECT doctor_username , "
                         "doctor_password FROM Doctors_info WHERE doctor_username = '{}' "
                         "and doctor_password = '{}' ".format(username,userpass))
           if c.fetchone() is not None:

               return render_template('home.html')
           else:
               return render_template('login.html',variable = 'Invalid username or password')
        if request.form['Register']:

            return redirect(url_for('signup'))


    return render_template('login.html')


if __name__ == "__main__":
    app.run()
