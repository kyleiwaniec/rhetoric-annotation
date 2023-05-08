## Create db
```
docker run --name mapping_tool_mongodb -d -v <this-folder>/db:/data/db -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=iq4user -e MONGO_INITDB_ROOT_PASSWORD=iq4pass mongo
```

## Postman
https://web.postman.co/workspace/My-Workspace~290151f5-aa0e-4a8d-8a0f-67cca171e8f2/history/19827627-5b43f703-4ee6-4a3d-96ce-6af23bf14280


## API endpoints
POST
http://127.0.0.1:5000/api/v1/get_distances.  

Calculates pairwise distances between two lists of skills. The smaller the number (distance), the more similar the items.   

Takes as input an object with a skills key with a value of a list of two lists. Optionally, a threshold flag can be set to return only results below a threshold.

Example 1:   
```
{"skills":[["UX","UI","data management"], ["design","data administration"]]}
```   

Example 2:   
```
{"skills":[["UX","UI","data management"], ["design","data administration"]], "threshold":0.5}
```  

Returns a list of tuples of the form [skill1, skill2, distance].   

Example 1:
```
[
 ["UX", "design", 0.48709644615981473], 
 ["UX", "data administration", 0.8160752937128718], 
 ["UI", "design", 0.49080735861258595], 
 ["UI", "data administration", 0.7443347369705295], 
 ["data management", "design", 0.7433327222251169], 
 ["data management", "data administration", 0.4497042486319286]
]
```

Example 2:
```
[
 ["UX", "design", 0.48709644615981473], 
 ["UI", "design", 0.49080735861258595], 
 ["data management", "data administration", 0.4497042486319286]
]
```

Example use case:  calculate the "match" between a user and a job.    

====================================================================================================

POST
http://127.0.0.1:5000/api/v1/get_embeddings.   

Calls the model to get embeddings.    

Tale as input a list of skills:    
```
{"skills":["UX","UI"]}
```

Returns a dictionary with each skill as key, and the embedding as value.    
```
{
"UX": [0.12002389132976532, 0.2027219533920288, 0.382690966129303, ... 0.0640638917684555],
"UI": [0.2344559282064438, -0.01450124941766262, 0.46194663643836975, ... -0.4272909164428711]
}
```
Example use case:  perform your own calculations in vector space.     

====================================================================================================

POST
http://127.0.0.1:5000/api/v1/recommend-skills.    
Fetches the `n` most similar skills:    

Takes as input a json object with a list of skills and 2 parameters:    
```
{"skills":["UX","UI"],"exact":0,"n":3}
```
`n` -> how many items to return    
`exact`  (where 0 is false and 1 is true) -> whether to return exact matches (ie. distance == 0).   
`taxonomy` optional parameter to specify the taxonomy. Can be a single string, or a list of strings.    
Possible values are: `['RSD','JPMC','EMSI','LEIDOS','NICE','ONET','TK']`

Examples:

```
{"skills":["UX","UI"],"exact":0,"n":3,"taxonomy":"TK"}
{"skills":["UX","UI"],"exact":0,"n":3,"taxonomy":["TK","ONET"]}
```

Returns a dictionary with keys for each skill, and the n top matches as well as the source, and the distance.    
```
{"UX": [
[{"skill": "User-Centered Design", "source": "EmsiSkills.csv"}, 0.2460040017007361],
[{"skill": "Website Wireframe", "source": "EmsiSkills.csv"}, 0.24969331849857157],
[{"skill": "Usability", "source": "EmsiSkills.csv"}, 0.29377443771464107]],
"UI": [
[{"skill": "Prototype JavaScript Framework", "source": "EmsiSkills.csv"}, 0.19218134747995474],
[{"skill": "Bootstrap (Front-End Framework)", "source": "EmsiSkills.csv"}, 0.2045685966143309],
[{"skill": "JavaScript", "source": "ONET_Skills.csv"}, 0.20552098701841925]
]}
```

Example use case, skills recomendations.
