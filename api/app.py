from flask import Flask, request, jsonify, make_response
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

from flask import Flask,render_template, request
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:8887"}})

# connect to DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'annotations'
 
mysql = MySQL(app)

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

