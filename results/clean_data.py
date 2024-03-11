# coding=utf-8

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import ast
from tqdm import tqdm

import argparse
import os
import sys

import re
import utils
import importlib
importlib.reload(utils)

import GPT
importlib.reload(GPT)
gpt = GPT.GPT("gpt-3.5-turbo-1106")



def main(FEATURE,output_path):
    

    non_agreed_sentences = pd.read_csv("non_agreed_sentences_"+FEATURE+".csv")


    ########################################################################################################################################
    ### 0. Get the majority vote from the annotators (props_a20, props_a21, props_a22)
    ########################################################################################################################################

    # get the majority vote from the annotators (props_a20, props_a21, props_a22)
    # What to do when there is no majority? NA?

    # remove NaNs since they screw up the majority counting
    non_agreed_sentences[['props_a20','props_a21','props_a22']] = non_agreed_sentences[['props_a20','props_a21','props_a22']].fillna('[]')

    non_agreed_sentences['props_a_majority'] = non_agreed_sentences['props_a20']+", "+\
                                               non_agreed_sentences['props_a21']+", "+\
                                               non_agreed_sentences['props_a22']

    def convert(x):
        return list(ast.literal_eval(x))

    non_agreed_sentences['props_a_majority'] = non_agreed_sentences['props_a_majority'].apply(convert)
    non_agreed_sentences['props_a_majority'] = non_agreed_sentences['props_a_majority'].apply(lambda l: utils.find_majority(l)[0])
    ########################################################################################################################################


    ########################################################################################################################################
    ### 1. parse GPT response again taking account of new lines  
    ########################################################################################################################################
    def parseRes(x):
        try:
            result = gpt.parseResponse(x)[1][0]
        except:
            result = gpt.parseResponse(x)[1]
        
        return result

    non_agreed_sentences['gpt_props1'] = non_agreed_sentences.apply(lambda x: parseRes(x.res1),axis=1)
    non_agreed_sentences['gpt_props2'] = non_agreed_sentences.apply(lambda x: parseRes(x.res2),axis=1)
    non_agreed_sentences['gpt_props3'] = non_agreed_sentences.apply(lambda x: parseRes(x.res3),axis=1)
    ########################################################################################################################################


    ########################################################################################################################################
    ### 2. Fix property names  
    ########################################################################################################################################

    # Correct the GPT properties to match the annotators. Takes care of misspellings and underscores
    def mapProp(x):
        if type(x) == str:
            return [gpt.mapToProperty(elem,FEATURE) for elem in ast.literal_eval(x)]
        else:
            return [gpt.mapToProperty(elem,FEATURE) for elem in x]

    for col in ['gpt_props1','gpt_props2','gpt_props3']:
        non_agreed_sentences[col] = non_agreed_sentences[col].apply(lambda x: mapProp(x))

    ########################################################################################################################################


    ########################################################################################################################################
    ### 3. Recalculate the GPT majority 
    ########################################################################################################################################
    
    # move the previously calculated GPT4 majority property to props_gpt4_majority
    def get_gpt4Majority(row):
        if type(row['res1']) != str:
            return ast.literal_eval(row['props_gpt_majority'])
        else:
            return []

    non_agreed_sentences['props_gpt4_majority'] = non_agreed_sentences.apply(lambda x: get_gpt4Majority(x), axis=1)

   
    
    def listOfLists(*lists):
        new_list = []
        for l in lists:
            if len(l):
                new_list.append(l)
        return new_list

    non_agreed_sentences['props_gpt_list'] = non_agreed_sentences.apply(lambda x: listOfLists(x['gpt_props1'],
                                                                                              x['gpt_props2'],
                                                                                              x['gpt_props3']), axis=1)
    def find_majority(row):
        if len(row.props_gpt_list):
            return utils.find_majority(row.props_gpt_list)[0]
        else:
            return row.props_gpt_majority

    non_agreed_sentences['props_gpt_majority'] = non_agreed_sentences.apply(lambda x: find_majority(x),axis=1)
    non_agreed_sentences = non_agreed_sentences.drop(['props_gpt_list'], axis=1)

    ########################################################################################################################################


    ########################################################################################################################################
    ### 4. Recalculate human/GPT agreement
    ########################################################################################################################################

    non_agreed_sentences.to_csv(output_path+"/non_agreed_sentences_"+FEATURE+".csv",index=None)
    non_agreed_sentences = pd.read_csv(output_path+"/non_agreed_sentences_"+FEATURE+".csv")

    non_agreed_sentences['ann_gpt_agreemnt'] = non_agreed_sentences.apply(lambda x: utils.calcAgreement(x['props_a_majority'],x['props_gpt_majority']), axis=1)
    
    non_agreed_sentences.to_csv(output_path+"/non_agreed_sentences_"+FEATURE+".csv",index=None)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature",
                        default=None,
                        type=str,
                        required=True,
                        help="Feature")
    parser.add_argument("--output_path",
                        default="tests",
                        type=str,
                        help="Path to save the output to")
    args = parser.parse_args()
    FEATURE = args.feature
    output_path = args.output_path
    
    main(FEATURE,output_path)