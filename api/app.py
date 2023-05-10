from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, session
import utils
from collections import defaultdict
import operator
import numpy as np
import json
import time 

import tiktoken
import os
import openai
from tqdm import tqdm
import ast
import re
import uuid, hashlib, datetime, math, urllib


from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:8887","http://localhost:5000"]}})

# connect to DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'annotations'
app.static_folder = 'ui'

app.secret_key = 'yoursecretkey'
 
mysql = MySQL(app)




# http://localhost:5000/ - the following will be our login page, which will use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():

    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', userid=session['id'],username=session['username'], firstname=session['firstname'])



    # Output message if something goes wrong...
    msg = ''
    username = ''
    password = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        
        password = request.form['password']
        email = request.form['email']
        username = email

        
        # Retrieve the hashed password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest();
        

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM annotators WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        
        # account (4, None, None, 'test@test.com', 'test', 'test') --> (id, firstname, lastname, email, username, password)

        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[4]
            session['firstname'] = account[1]
            # Redirect to home 
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'


    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('firstname', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''

    # Check if "password" and "email" POST requests exist (user submitted form)
    if (request.method == 'POST' 
        and 'password' in request.form 
        and 'email' in request.form 
        and 'firstname' in request.form 
        and 'lastname' in request.form):
        # Create variables for easy access


        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        email = request.form['email']
        username = email


        
        # Hash the password
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        hashed_password = hash.hexdigest();
        

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM annotators WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not username or not hashed_password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO annotators VALUES (NULL, %s, %s, %s, %s, %s)', (firstname, lastname, email, username, hashed_password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered! Please log in to proceed.'




    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)



# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', userid=session['id'],username=session['username'], firstname=session['firstname'])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM annotators WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))




# doing it this way so we can use template {{}} inside javascript
@app.route("/main_js")
def main_js():
    return render_template("/js/main.js")


def tech_to_list(s):
    return [int(i) for i in s[1:-1].split(" ") if len(i)>0]



@app.route("/api/v1/get_stats", methods=["OPTIONS","GET","POST"])
def get_stats():
    response = {"error":"no data"}
    request_data = request.get_json()

    if request_data:
        annotator_id = request_data['annotator_id']

        # query = '''SELECT COUNT(*) FROM annotations.annotations WHERE annotator_id=%s AND completed is NULL'''


        query = '''
        SELECT 
          COUNT( CASE WHEN completed is NULL THEN 1 END ) AS t1,
          COUNT( CASE WHEN completed=1 THEN 1 END ) AS t2
        FROM annotations.annotations WHERE annotator_id=%s
        '''

        cursor = mysql.connection.cursor()

        cursor.execute(query, (annotator_id, ))
        rows = cursor.fetchall() # store the result before closing the cursor
        mysql.connection.commit()
        cursor.close()


        print("rows",rows)
        response = json.dumps(rows)

    return response




@app.route("/api/v1/get_sentences_from_table", methods=["OPTIONS","GET","POST"])
def get_sentences_from_table():

    next_sentence = {"error":"no data"}
    json_data = request.get_json()
    
    
    if json_data:

        sentence_id = json_data["sentence_id"]
        annotator_id = json_data['annotator_id']

        if "direction" in json_data and json_data["direction"] == "next":
            query = '''
                    SELECT * FROM annotations.all_sentences as s
                    LEFT JOIN (SELECT * FROM annotations.annotations WHERE annotator_id=%s) as a 
                    ON s.id = a.sentence_id
                    WHERE s.id > %s AND a.completed is NULL ORDER BY s.id ASC LIMIT 1;
                    '''

        elif "direction" in json_data and json_data["direction"] == "prev":
            query = '''
                    SELECT * FROM annotations.all_sentences as s
                    LEFT JOIN (SELECT * FROM annotations.annotations WHERE annotator_id=%s) as a 
                    ON s.id = a.sentence_id
                    WHERE s.id < %s AND a.completed is NULL ORDER BY s.id DESC LIMIT 1;
                    '''
        else:            
            query = '''
                    SELECT * FROM annotations.all_sentences as s
                    LEFT JOIN (SELECT * FROM annotations.annotations WHERE annotator_id=%s) as a 
                    ON s.id = a.sentence_id
                    WHERE s.id = %s;
                    '''


        cursor = mysql.connection.cursor()

        cursor.execute(query, (annotator_id,sentence_id,))
        rows = cursor.fetchall() # store the result before closing the cursor
        mysql.connection.commit()
        cursor.close()

        ###### close when finished with the DB ##############################

        sentences_json = []

        for row in rows:
            sentences_json.append({
                "sentence_id" : row[0],
                "article_id" : row[1],
                "technique" : tech_to_list(row[2]),
                "offsets" : row[3],
                "label" : row[4],
                "text" : row[5],
                "parse_string" : row[6],
                "annotation" : row[10] or "",
                "annotator_id" : annotator_id, #row[11] or 0,
                "annotation_id" : row[9] or 0
                })
            
        next_sentence =  json.dumps(sentences_json) #jsonify(sentences_json)

    return next_sentence



@app.route("/api/v1/save_annotation", methods=["OPTIONS","POST"])
def save_annotation():
    
    request_json = request.get_json()


    # remove the following properties:
    properties = ["isCurrNode","depth","x","y","id","x0","y0"]

    if request_json:
        def removeProps(d): 
            for p in properties:
                if p in d:
                    if p == "isCurrNode":
                        d["isCurrNode"] = 0
                    else:
                        del d[p]
            if "children" in d:
                for child in d["children"]:
                    removeProps(child)

        removeProps(request_json)


        ###### open connection to the DB ##########################################
        cursor = mysql.connection.cursor()

        
        sentence_id   = request_json['sentence_id']
        annotation_id = request_json['annotation_id']
        annotator_id  = request_json['annotator_id']
           
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        
       

        query = '''INSERT INTO annotations.annotations (id, json_string, annotator_id, sentence_id, date_updated) VALUES (%s,%s,%s,%s,%s)
          ON DUPLICATE KEY UPDATE json_string=%s, annotator_id=%s, sentence_id=%s, date_updated=%s;'''


        cursor.execute(query, (annotation_id, json.dumps(request_json), annotator_id, sentence_id, date, 
                                json.dumps(request_json), annotator_id, sentence_id, date)) 
        
        mysql.connection.commit()
        cursor.close()
        ###### close when finished with the DB ##############################


    fetchDBresult = jsonify(request_json)

    return fetchDBresult
    

@app.route("/api/v1/mark_completed", methods=["OPTIONS","POST"])
def mark_completed():
    response = {"error":"no data"}
    request_data = request.get_json()

    if request_data:
        annotation_id = request_data['annotation_id']
        
        print("annotation_id",annotation_id)

        query = '''UPDATE annotations.annotations SET completed=1 WHERE id=%s'''

        cursor = mysql.connection.cursor()

        cursor.execute(query, (annotation_id,))
        rows = cursor.fetchall() # store the result before closing the cursor
        mysql.connection.commit()
        cursor.close()


        print("rows",rows)
        response = json.dumps(rows)

    return json.dumps({"asnswer":"marked completed"})


################################################################################################################################

# load features for ChatGPT
featuresDict = defaultdict(list)
with open('features.json') as f:
    for jsonObj in f:
        featureDict = json.loads(jsonObj)
        featuresDict[featureDict['key']] = [val+" : "+desc for val, desc in zip(featureDict['values'],featureDict['descriptions'])]



@app.route("/api/v1/get_gpt_response", methods=["OPTIONS","POST"])
def get_gpt_response():
    
    response = {"error":"no data"}
    json_data = request.get_json()


    
    if json_data:
        sentence = json_data['sentence']
        feature = json_data['feature']
        # prompt = json_data['prompt']

        types = "\n".join(featuresDict[feature])

        prompt = f"""
        Your task is to identify which, if any, of the following types of {feature} are used in the example text. 
        Each line is a type and a descrition separted by a colon
        
        {types}

        In the description explain your choice.
        The sentence is delimited with triple backticks. 
        Format your response as a JSON object with 
        "Type" and "Explanation" as the keys. 
        If the information isn't present, use "unknown" 
        as the value.
        Make your response as short as possible.
          
        Example text: ```{sentence}```
        """

        
        # topic_list = ['appeal to authority','hyperbole','name-calling', 'bandwagon']
        # prompt = f"""
        # Determine whether any of the rhetorical devices in the following list
        # is present in the example text. The example text
        # is delimited with triple backticks.

        # Give your answer as list with 0 or 1 for each device.
        # Explain your answer.

        # List of rhetorical devices: {", ".join(topic_list)}

        # Example text: ```{sentence}```
        # """




        openai.organization = os.getenv("OPENAI_ORG_ID")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        model = "gpt-3.5-turbo-0301"

                    
        messages=[{"role": "user", "content": prompt}]
        res = openai.ChatCompletion.create(
          model=model,
          messages=messages
        )
        

        response = res["choices"][0]["message"]["content"]

    return response

