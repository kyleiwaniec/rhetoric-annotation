# APP 
This application makes it easier to annotate natural language text with liguistic devices discussed in Jeanne Fahnestock's Rhetorical Style - Uses of language in persuasion. 

It leverages ChatGPT as a model in the loop to aid the human annotator in the annotation process.

It takes as input constituency parse trees, and outputs a JSON tree with annotations for each sentence.

## Requirements

### Database

* MySQL 5.6.40 or higher

### API

* Python 3/Flask
* ChatGPT API key

### UI

* Javascript/ES6

# Results
This folder contains all the code used in analysis and prompting GPT. 

# Features and properties

The features and properties were extracted from Rhetorical Style: The use of language in persuasion, Fahnestock (2011). 

The json files containing all terms, definitions, and examples are in:
* APP/features-sentence.json
* APP/features-word.json