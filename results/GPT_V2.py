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
import openai
from tqdm import tqdm
import backoff
import logging
import requests
import re
import difflib as dl

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

        logging.basicConfig(filename='gpt_reponse.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.getLogger('backoff').addHandler(logging.FileHandler('gpt_reponse.log'))

        openai.organization = os.getenv("OPENAI_ORG_ID")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        ################################################################################################################################
        
        # load features for ChatGPT

        propertiesDict = defaultdict(list)


        sentenceFeaturesDict = defaultdict(list)
        sentenceFeaturesList = []

        with open('../APP/features-sentence.json') as f:
            sentenceFeaturesList = json.load(f)

            for featureDict in sentenceFeaturesList:
                sentenceFeaturesDict[featureDict['key']] = [val+" : "+desc for val, desc in zip(featureDict['values'],featureDict['descriptions'])]
                propertiesDict[featureDict['key']] = featureDict['values']


        wordFeaturesDict = defaultdict(list)
        wordFeaturesList = []

        with open('../APP/features-word.json') as f:
            wordFeaturesList = json.load(f)
            for featureDict in wordFeaturesList:
                wordFeaturesDict[featureDict['key']] = [val+" : "+desc for val, desc in zip(featureDict['values'],featureDict['descriptions'])]
                propertiesDict[featureDict['key']] = featureDict['values']



        self.featuresDict = sentenceFeaturesDict | wordFeaturesDict
        
        self.propertiesDict = propertiesDict



    def get_gpt_response(self,sentence,feature,sid,temp):
        feature = feature.replace("_", " ")
        properties = "\n".join(self.featuresDict[feature])
        multiplicity = ["multiple properties","only one property"][0]
        

        # global prompt
        prompt = f"""
        You are a rhetoretician and linguist specializing in identifying grammatical features in news text. 

        Your task is to identify which, if any, of the following properties of {feature} are used in the example text. 
        Each line contains a property followed by a colon, followed by a brief definition and example(s):

        {properties}

        Format your response as a JSON object with "Properties" and "Explanation" as the keys. The value of "Properties" should be a list. Choose only from the properties provided, and list the relevant properties exactly as they appear without any modification. You may select {multiplicity}. Explain your choice in the "Explanation". Make your response as short as possible.
        """
        

        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": sentence}]


        def fatal_code(e):
            # print(e)
            self.errors.append([sid,e])
            return True #400 <= e.response.status_code < 600

        def backoff_hdlr(details):
            print ("Backing off {wait:0.1f} seconds after {tries} tries calling function {target} with args {args} and kwargs {kwargs}".format(**details))

        @backoff.on_exception(backoff.expo,
                              (openai.error.RateLimitError,
                               openai.error.APIError,
                               openai.error.APIConnectionError,
                               openai.error.Timeout,
                               openai.error.ServiceUnavailableError,
                               requests.exceptions.Timeout),
                        max_time=20,
                        raise_on_giveup=False,
                        giveup=fatal_code,
                        on_backoff=backoff_hdlr)

        def completions_with_backoff(**kwargs):
            return openai.ChatCompletion.create(**kwargs)
        
        # temperature between 0-2, default = 1 (lower is more consistent)
        
        res = completions_with_backoff(model=self.model, 
                                       response_format={ "type": "json_object" },
                                       temperature=temp,
                                       messages=messages,
                                       max_tokens=1024,
                                       request_timeout=300)

        if res is not None:
            response = res["choices"][0]["message"]["content"]
            usage = res["usage"]
        else:
            response = "timeout"
            usage = ""

        return (prompt,response, usage)
    
    def parseResponse(self,response):
        properties = set()
        all_properties = []

        if response and type(response) is str:
            response = response.replace("'","")
            response = response.replace("\n","")
            m = re.search("\[(.*?)\]", response)

            if m is not None:

                try:
                    # this is OK when the sting is well formed, eg: ["antithesis","antimetabole"]
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
    
    def mapToProperty(self,s,feature,cutoff=.4):
        correct_properties = self.propertiesDict[feature.replace("_"," ")]
        correct_properties = [p.strip() for p in correct_properties]
        try: 
            return dl.get_close_matches(s,correct_properties,n=1,cutoff=cutoff)[0].replace(" ","_")
        except: 
            return ''