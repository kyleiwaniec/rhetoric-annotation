// https://wesbos.com/template-strings-html
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals


const word_properties = [
    {	key: 'Language of origin', 
    	values: ["Old English core",
			"Norman French",
			"Latin/Greek"], 
    	descriptitons: [
		    	" ",
				" ",
				" "]
    },
    {	key: 'New words and changing uses', 
    	values: ["foreign borrowing",
			"compounds",
			"prefixes/suffixes",	
			"clipping",
			"blends",
			"conversions",
			"catachresis",
			"acronyms",
			"proper nouns to common nouns",
			"analogy",
			"fabrication",
			"onomatopoeia",
			"taboo deformation",
			"doubling"],
    	descriptitons: ["borrowing a word from another language	cafe latte",
	    	"when users yoke exisitng words together to create a compound.	open house; open-minded; open-ended; political correctness; special interests",
	    	"when prefixes or suffixes change meaning	(co-, hyper-, multi-) multimedia; hyperpartisan; Truman-esque",
	    	"making a shorter version of a word	fax from facsimilie; porn from pornography, app from application",
	    	"visiblly and phonetically combine terms to dreate new entities	televangelist (televeision + evangelist); shockumentary (shock + documentary)",
	    	"pressing a term from one part of speech into service in another	to lame out; slather; I just texted him (text is originally a noun)",
	    	"borrowing af an available word to designate something that lacks a label.	spam for unwanted email",
	    	"words fromed from the first letters of strings of words	FBI; CIA; LOL",
	    	"using names of people or products	kleenex; xerox; She is a Mata Hari",
	    	"a new word is formed according to the model of another word that is close in meaning	prequel and interequel were formed by analogy from sequel;  NOTE: the similarity in naming 'proteonomics' and 'genomics' suggests equal importance and hence equal funding rights.",
	    	"totally made up words. often used in advertising.	fribble; taffy; kluge/kludge",
	    	"'sound words'	cock-a-doodle-do; swish; hee-haw",
	    	"euphemisms	darn it; gee-whiz;",
	    	"duplication: goody-goody; riff-raff; sing-song"] 
    },
    {	key: 'Lexical and semantic fields', 
    	values: ["general",	
			"specific",	
			"prototype",	
			"abstract",	
			"concrete",	
			"indefinite/thesis", 	
			"definite/hypothesis" ],
	    descriptitons: ["hypernyms, for example: 'animal' is a hypernym of 'dog'",
	    	"hyponyms, for example: 'Australin Cattle Dog' is a hyponym of 'dog'",
	    	"a specific member of a group which representative of that group	robin as a standin for bird",
	    	"broad catergories or relationships	'implement (as opposed to shovel)'",
	    	"physical objects and actions or immediate sense impressions 'shovel (as opposed to implment)'",
	    	"general - no reference to specific persons, time, place should a man marry?",
	    	"specific people or things should Cato marry?"] },
    {	key: 'Language varieties', 
    	values: ["correctness",
			"clarity",
			"forcefulness",
			"appropriateness",
			"low",
			"middle",
			"high",
			"maxims/proverbs",
			"Allusions"],
    	descriptitons: ["well formed grammatically",
    		"understandable to the intended audience",
    		"finding memorable or striking expresion which reinforces the message",
    		"tied to cultural norms of propriety",
    		"informal or colloquial (sometimes vulgar)	'I was like, dude..'",
    		"Standard Edited American English - widely accpte conventions, typical of reputable books, magazines, and newspapers",
    		"Formal English, 'grand', official documents and scholarly publications",
    		"words/sentences/phrases which express common wisdom 'don't put all your eggs in one basket'; 'if anything can go wrong, it will'",
    		"the importation of a phrase from another context without explictly naming the other context - intertextuality. Requires cultural knowledge. 'Cage against the machine' used in a headline about Nicalas Cage alluding to the band name 'Rage against the machine'"
    		]  
    },
    {	key: 'Tropes', 
    	values: ["synecdoche",
			"metonymy",
			"antonomasia",
			"metaphor",
			"allegory",
			"simile",
			"full analogies",	
			"irony",
			"hyperbole",
			"litotes" ,
			"amphiboly",
			"paradox",
			"paralepsis/praeteritio",
			"euphemism"	
    		],
    	descriptitons: ["parts representing the whole; 'farm hand'",
    		"substitutions with terms chosen according to some recoverable, specifiable principle or association; 'suit' for business man",
    		"NP subsitution for proper name; replacing a proper name with a descriptive label that characterizes while renaming",
    		"bringing a term from an 'alien' semantic field to create a novel pariing that expresses a point trenchantly",
    		"Story w hidden meaning; extended metaphor",
    		" (as brave as a lion)",
    		"explictly stated metaphors or analogies. Often in entire passages",
    		" ",
    		"overstatement;	exaggerated statements or claims not meant to be taken literally.",
    		"understatement",
    		"ambiguity in grammar; a phrase that can genuinely be construed to have two meanings",
    		"delibeartely self-contradicting. The speaker maintains a contradiciton knowing that the audience will percieve it as such, and then goes on to resolve it.",
    		"Saying something while denyong saying it",
    		"substitution of a mild or polite phrase for a crude or offensive one. Often used to minimize the gravity of something"
			]  
    },
    {	key: 'Figures of word choice', 
    	values: ["agnominatio",
			"metaplasms",
			"polyptoton",
			"ploce",
			"anatanaclasis",
			"synonyms",
			"rhetorical conditional",
			"correctio",
			"emphasis"],
    	descriptitons: ["play on words - the ballot or the bullet; general Petraeus or genral Betray us?; a bad child is really a sad child",
    		"altering a single word - creates pairs of words that must appear near each other in the same text in order ot have an argumentative effect",
    		"change of case reusing the same word in different form; 'he dreamed a dream'; 'ages of ages'; 'they loved with great love'",
    		"repetition of a word either in a single sentence or throughout a passage",
    		"puns -	when a word is repeated but its meaning is different in each instance",
    		"conceptual drift -	words with similar meaning. sometimes through substituting words with their synonyms the connotaion is changed, for example from bad to good",
    		"if/then where the antecendent is absurd, or cannot be true. 'If pigs could fly'. Reductio ad absurdium",
    		"deliberately making a mistake and then immediatey correcting it. Allows the speaker to introduce alternative connotations or dubious interpretations ",
    		"significatio / innuendo - use of leading words that suggest more than is actually stated. Sometimes referred to as innuendo. Allows the speaker to benefit from an implication while allowing deniability."]  
    }
];

function replaceSpaces(str){
	return `${str.replace(/\s/g, '_')}`;
}

function renderValues(vals, desc){

	const zip = vals.reduce((acc, current, idx) => {
	  return [...acc, [current, desc[idx]]]
	}, [])

	return  `${zip.map(z => `
				  <li class="list-group-item">
				    <input class="form-check-input me-1" type="checkbox" value="${replaceSpaces(z[0])}" id="${replaceSpaces(z[0])}Checkbox">
				    <label class="form-check-label" for="${replaceSpaces(z[0])}Checkbox"><b>${z[0]}</b> — ${z[1]}</label>
				  </li>`).join('')}
			`;
}


const word_markup = `
<div class="row">
  <div class="col-4">
    <div class="list-group" id="list-tab" role="tablist">
    	${word_properties.map(property => `<a class="list-group-item list-group-item-action" onclick="get_gpt_response(this,'${property.key}'); updateTimer(); return false" id="list-${replaceSpaces(property.key)}-list" data-bs-toggle="list" href="#list-${replaceSpaces(property.key)}" role="tab" aria-controls="list-${replaceSpaces(property.key)}">${property.key}</a>`).join('')}
	</div>
  </div>
  <div class="col-8">
    <div class="tab-content" id="nav-tabContent">
    	${word_properties.map(property => `<div class="tab-pane fade" id="list-${replaceSpaces(property.key)}" role="tabpanel" aria-labelledby="list-${replaceSpaces(property.key)}-list">
	      		<p>ChatGPT response:</p>

	      		<div id="${replaceSpaces(property.key)}_GPT">
	      			<div class="GPT-response"></div>
	      			<div class="spinner-border visually-hidden" role="status">
								  <span class="visually-hidden">Loading...</span>
							</div>
	      		</div>
	      		
	      		<form name="${replaceSpaces(property.key)}" onsubmit="formSubmit(this); return false;">
		      		<ul class="list-group mb-3 mt-3">
		      			${renderValues(property.values,property.descriptitons)}
		      		</ul>	
	    			
							<input type="submit" value="Add Property" type="button" class="btn btn-primary"/>
							<input value="Next Property" type="button" class="btn btn-warning" onclick="return nextProperty(this)"/>
							<input id="removePropertyButton" value="Remove Property" type="button" class="btn btn-danger float-end" onclick="pushProperty(false,['${replaceSpaces(property.key)}',[]]); saveAnnotation(confirmSaved); return false;"/>
						
						</form>

						<p class="mt-3">
						INSTRUCTIONS:<br>
						1. Select a node in the parse tree above.<br> 
						2. Use the buttons below to add or remove the <em>${property.key}</em> property and all its values for the selected node.
						</p>

	    </div>`).join('')}
	  </div>
	</div>
</div>
`


document.getElementById("nav-word").innerHTML = word_markup;



      
