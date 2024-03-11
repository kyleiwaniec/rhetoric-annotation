# prompting GPT

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, OrderedDict, defaultdict
import utils
import features
import importlib
import ast
import tiktoken
import os
from tqdm import tqdm
import backoff
import logging
import requests
import re
import difflib as dl
from datetime import datetime

from openai import OpenAI
import openai



class GPT:
    def __init__(self, model):

        self.model = model
        self.errors = []
        
        # model = "gpt-3.5-turbo-0301"
        # model = "gpt-3.5-turbo-0613"
        # model = "gpt-3.5-turbo-1106"
        # model = "gpt-4"
        # model = "gpt-4-1106-preview" #gpt4-turbo
        
        logging.getLogger('backoff').handlers.clear()

        logging.basicConfig(filename='PTC_GPT.log', encoding='utf-8', level=logging.WARNING,
                    format='%(levelname)s \t %(asctime)s \t %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        logging.getLogger('backoff').addHandler(logging.FileHandler('gpt_reponse.log'))

        # openai.organization = os.getenv("OPENAI_ORG_ID")
        # openai.api_key = os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(
          api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
          timeout=20.0,
          max_retries=5
        )

        ################################################################################################################################
        
        # load features for ChatGPT

        propertiesDict = defaultdict(list)
        questionsDict = defaultdict()


        sentenceFeaturesDict = defaultdict(list)
        sentenceFeaturesList = []

        with open('../APP/features-sentence.json') as f:
            sentenceFeaturesList = json.load(f)

            for featureDict in sentenceFeaturesList:
                sentenceFeaturesDict[featureDict['key']] = {val:desc for val, desc in zip(featureDict['values'],featureDict['descriptions'])}

                questionsDict[featureDict['key']] = featureDict['question']

                propertiesDict[featureDict['key']] = featureDict['values']


        wordFeaturesDict = defaultdict(list)
        wordFeaturesList = []

        with open('../APP/features-word.json') as f:
            wordFeaturesList = json.load(f)
            for featureDict in wordFeaturesList:
                wordFeaturesDict[featureDict['key']] = {val:desc for val, desc in zip(featureDict['values'],featureDict['descriptions'])}

                questionsDict[featureDict['key']] = featureDict['question']

                propertiesDict[featureDict['key']] = featureDict['values'] # dictionary of features and their list of properties



        self.featuresDict = sentenceFeaturesDict | wordFeaturesDict
        
        self.propertiesDict = propertiesDict
        self.questionsDict = questionsDict



    def get_gpt_response(self,sentence,feature,sid,temp, model_version):
        feature = feature.replace("_", " ")

        responses = []

        question = self.questionsDict[feature]

        for prop, desc in self.featuresDict[feature].items():

            quest = question.replace("_PROP_",prop)

        
            #SYSTEM_PROMPT = f"""You are ChatGPT, a large language model trained by OpenAI, based on the {model_version} architecture. You are also an expert linguist and grammarian specializing in news corpora."""
            SYSTEM_PROMPT = f"""You are an expert linguist and grammarian specializing in news text."""

            USER_PROMPT = f"""Format your response as a JSON object with 'Answer' and 'Explanation' as the keys. The value of 'Answer' should be either 'yes' or 'no'. Explain your choice in the 'Explanation'.

            In the context of grammar, '{prop}' '{feature}' {desc}

            {quest}: {sentence}
            """
            

            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": USER_PROMPT}]

            def fatal_code(e):
                # print(e)
                logging.error("SID: %s, FatalCode: %s",sid,e)
                return True #400 <= e.response.status_code < 600

            def backoff_hdlr(details):
                print ("Backing off {wait:0.1f} seconds after {tries} tries calling function {target} with args {args} and kwargs {kwargs}".format(**details))
            
            @backoff.on_exception(backoff.expo, 
                                  (openai.APIError,
                                  openai.APIConnectionError,
                                  openai.RateLimitError,
                                  openai.APITimeoutError,
                                  openai.InternalServerError,
                                  openai.UnprocessableEntityError),
                        max_time=20,
                        raise_on_giveup=False,
                        giveup=fatal_code,
                        on_backoff=backoff_hdlr)
            
            def completions_with_backoff(**kwargs):
                return self.client.chat.completions.create(**kwargs)
            

            res = completions_with_backoff(model=self.model, 
                                           response_format={ "type": "json_object" },
                                           temperature=temp,
                                           messages=messages,
                                           max_tokens=1024)


            if res is not None:
                response = res.choices[0].message.content
                usage = res.usage
            else:
                response = "timeout"
                usage = ""

            responses.append([USER_PROMPT, prop, feature, response, usage])

        return responses

    def get_single_gpt_response(self,sentence,feature,sid,temp):
        feature = feature.replace("_", " ")

        responses = []

        question = self.questionsDict[feature]
        # quest = question.replace("_PROP_",prop)
        properties = []

        for prop, desc in self.featuresDict[feature].items():
            properties.append("* "+prop+" "+desc)

        properties = "\n".join(properties)
            

        
        SYSTEM_PROMPT = f"""You are ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture. You are also an expert linguist and grammarian specializing in news text. Knowledge cutoff: 2021-09 Current date: {datetime.now().date()}"""

        USER_PROMPT = f"""Format your response as a JSON object with "Answer" and "Explanation" as the keys. The value of "Answer" should be a list of zero or more of the provided properties. Explain your choice in the "Explanation".

        {question}

        {properties}

        Sentence: {sentence}
        """
        

        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": USER_PROMPT}]


        res = self.client.chat.completions.create(model=self.model, 
                                       response_format={ "type": "json_object" },
                                       temperature=temp,
                                       messages=messages,
                                       max_tokens=1024)


        if res is not None:
            response = res.choices[0].message.content
            usage = res.usage
        else:
            response = "timeout"
            usage = ""

        result = (USER_PROMPT, response, usage)

        return result
    
    def parseResponse(self,response):
        properties = set()
        all_properties = []

        if response and type(response) is str:
            response = response.replace("'","")
            response = response.replace("\n","")
            m = re.search("\[(.*?)\]", response)


            if m is not None:

                try:
                    # this is OK when the string is well formed, eg: ["antithesis","antimetabole"]
                    r = json.loads(m.group())
                except:
                    # sometimes there are no quotation marks around the property name: [antithesis, antimetabole]
                    s = m.group()
                    s = re.findall("(\[)(.*?)(\])", s)
                    r = s[0][1].split(",")
                    r = [i.strip() for i in r]


                r = [i.replace(" ","_") for i in r]
                properties.add(str(r))
                all_properties.append(r)
            else:
                properties.add("[]")
                all_properties.append([])

        return properties, all_properties
    
    def parseYNResponse(self,response,_property):

        _property = _property.replace(" ","_")
        
        _map = {'yes':[_property],'no':[],'error':['parse error']}

        
        if response and type(response) is str:
            if response == "timeout":
                return "timeout"
            else:
                response = response.replace("'","")
                response = response.replace("\n","")
                
                try:
                    r = json.loads(response)

                    legit_anws = ["yes","no","error"]

                    if r["Answer"].lower() not in legit_anws:
                        r["Answer"] = "error"

                except:
                    r = {'Answer':'error'}

                return _map[r["Answer"].lower()]

        else:
            return ""

    def responseToJson(self,response):
        if response and type(response) is str:
            if response == "timeout":
                return "timeout"
            else:
                response = response.replace("'","")
                response = response.replace("\n","")
                
                try:
                    r = json.loads(response)
                except:
                    r = {'Answer':'parse error'}

                return r
        else:
            return {'Answer':'parse error'}


    def mapToProperty(self,s,feature,cutoff=.4):
        correct_properties = self.propertiesDict[feature.replace("_"," ")]
        correct_properties = [p.strip() for p in correct_properties]
        try: 
            return dl.get_close_matches(s,correct_properties,n=1,cutoff=cutoff)[0].replace(" ","_")
        except: 
            return ''