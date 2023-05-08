from collections import defaultdict
import numpy as np
import json
from datetime import datetime

def make_vectors_dict(skill_list,model):
    word_vectors_dict=defaultdict(list)
    for word in skill_list:
        word_vectors_dict[word]=(model.get_word_vector(word.lower().replace(" ",""))).tolist()
    return word_vectors_dict 
    

def calculate_pariwise_distances(dict1,dict2,threshold):
    
    distances=[]
    
    skill_names1, skill_embeddings1 = list(dict1.keys()), np.array(list(dict1.values()))
    skill_names2, skill_embeddings2 = list(dict2.keys()), np.array(list(dict2.values()))

    A = skill_embeddings1
    B = skill_embeddings2

    dots = np.dot(A,B.T)
    l2norms = np.sqrt(((A**2).sum(1)[:,None])*((B**2).sum(1)))
    distance_scores = 1 - (dots/l2norms)

    for i, scores in enumerate(distance_scores):
        for j, dist in enumerate(scores):

            dist = max(0.0, float(dist)) # we don't like negative numbers and json dumps doesn't like float32s
            if dist < threshold:
                distances.append([skill_names1[i],skill_names2[j],f'{dist:f}']) # string format to supress scientific notation

    return distances



def calculate_pariwise_distances_for_recommendations(dict1,nparr,threshold,exact):
    
    distances=defaultdict(list)
    
    skill_names, skill_embeddings = list(dict1.keys()), np.array(list(dict1.values()))

    A = skill_embeddings
    B = nparr

    dots = np.dot(A,B.T)
    l2norms = np.sqrt(((A**2).sum(1)[:,None])*((B**2).sum(1)))
    distance_scores = 1 - (dots/l2norms)


    for sid, scores in enumerate(distance_scores):
        for idx, dist in enumerate(scores):

            dist = max(0.0, float(dist)) # we don't like negative numbers and json dumps doesn't like float32s
            dist = float(f'{dist:.5f}') 

            if exact:
                if dist < threshold:
                    distances[skill_names[sid]].append([idx,dist])
            else:    
                if dist < threshold and dist > 0:
                    distances[skill_names[sid]].append([idx,dist])


    return distances
     

def get_top_matches(distances, skillsinfo, n, taxonomy):
    '''
    INPUTS:
    distances: dictionary where skill1 is the key, and the value is a list of [index,distance] tuples.
        (the index is the location of the skill in: skillsinfo[index])
    skillsinfo: list of objects containing skill information: {skill label, skill statements, source}
    n: the number of recommendations to return


    Distances EXAMPLE:
        {'Firewall': [[34, 0.6713990569114685],
                      [2001, 0.699846476316452],
                      [69, 0.7960561364889145]],
         'Capacity Planning': [[457, 0.7718107253313065],
                      [126, 0.6308979392051697],
                      [10005, 0.6341510117053986]]}
    skillsinfo EXAMPLE:
        [{'skill': 'Code Review',
          'skillstatements': ['Implement automated scanning tools and methods for application security code reviews.',
           'Implement manual methods and techniques for application security code reviews.',
           'Implement manual penetration testing of deployed applications.',
           'Implement static application security testing.'],
          'source': 'RSD Skills - Information Systems Security 2022-02-08.csv'}]

    RETURNS:
    returns top n matches for each skill: 
         EXAMPLE:
         {'Information Security Mgmnt': [[{'skill': 'Information Security Audit', 'skillstatements': [None], 'source': 'EmsiSkills.csv'}, 0.05407059192657471], [{'skill': 'Information Security Management', 'skillstatements': ['Design an incident response plan for information security incidents.', 'Explain the relationship of information security to business goals, objectives, functions, processes, and practices.', 'Develop information security policies, standards, procedures, and guidelines.', 'Develop a process for information asset classification that ensures that the measures taken to protect assets are proportional to their business value.', 'Describe information security processes and resources, including people and technologies, in alignment with the organization?s business goals and methods for applying them.', 'Compare the information security program with the operational objectives of other business functions for ensuring that the information security program protects and adds value to the business.', 'Assess information asset valuation methodologies.', 'Analyze data collected from cyber defense tools for event scope determination.', 'Apply methods for identifying and evaluating the impact of internal or external events on information assets and the business.', 'Identify requirements for internal and external resources for executing the information security program.', 'Acquire requirements for internal and external resources for executing the information security program.', 'Manage requirements for internal and external resources for executing the information security program.', 'Define requirements for internal and external resources for executing the information security program.', 'Implement information security policies, standards, procedures, and guidelines.', 'Communicate information security policies, standards, procedures, and guidelines.', 'Assess methods for establishing an information asset classification model consistent with business objectives.'], 'source': 'RSD Skills - Information Systems Security 2022-02-08.csv'}, 0.09010922908782959], [{'skill': 'Information Security Management', 'skillstatements': [None], 'source': 'EmsiSkills.csv'}, 0.09010922908782959]]}

    '''
    _top_matches=defaultdict()

    for k,v in distances.items():

        # sv = [[skillsinfo[x[0]], x[1]] for x in v]

        # do not return the skill statements
        # todo: return only matches for a given source(s)
        # [a if C else b for i in items]

        if len(taxonomy):
            sv = [[{'skill':skillsinfo[x[0]]['skill'],'source':skillsinfo[x[0]]['source']}, x[1]] for x in v if skillsinfo[x[0]]['source'] in taxonomy] #if skillsinfo[x[0]]['source'] in ["ONET_Skills.csv"]
        else:
            sv = [[{'skill':skillsinfo[x[0]]['skill'],'source':skillsinfo[x[0]]['source']}, x[1]] for x in v]
        
        _top_matches[k] = sorted(sv, key=lambda x: x[1])[:n]


    return json.dumps(_top_matches)



def get_avg_dist(matched_skills):
    return np.sum(matched_skills, axis=0)[2]/len(matched_skills)



def get_ratio(job_skills,matched_skills):
    j = len(job_skills)
    m = len(np.unique(matched_skills[:,1]))
    return (m, j, m/j)