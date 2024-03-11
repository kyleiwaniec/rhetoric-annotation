var zoomfactor = [1,1];
const pageWidth = _j(document).width();


function initTree(DBdata) {

	sentence_id = DBdata[0].sentence_id
	Cookies.set('sentence_id',sentence_id)


	let parse_string = DBdata[0].parse_string
	// Escape backslashes and Parse the string into JSON (defined in parser.js)
	parse_string = parse_string.replace(/\\/g, "\\\\");
 
	let article_id    = DBdata[0].article_id
	let techniques    = DBdata[0].technique
	let text 	      = DBdata[0].text
	let annotation    = DBdata[0].annotation
	let annotation_id = DBdata[0].annotation_id
	let review_flag   = DBdata[0].review_flag

	if (annotation.length > 1){
		jsonData = JSON.parse(annotation)
		jsonData.annotation_id = annotation_id
	}
	else {
		jsonData = parse(parse_string, article_id, sentence_id, annotation_id, annotator_id, techniques);
	}
	_j("#sentence_container").html("<p>"+text+"</p>");

	
	// render the Parse Tree
	d3Tree(jsonData);
	
	// render the JSON
	// renderJSON()
	// render the annotations as list text
	renderTEXT()

	// Add the review flag class
	if (review_flag==1){_j("#flag_for_review i").removeClass("bi-bookmark").addClass("bi-bookmark-fill")}
	else {_j("#flag_for_review i").removeClass("bi-bookmark-fill").addClass("bi-bookmark")}
	
	// reload the GPT response
	if (curr_feature){_j(curr_feature).click();}

	return false;
}
function zoomTree(direction){
	if (direction == 'out'){
		zoomfactor[0] *= 0.8
		zoomfactor[1] *= 0.8
	}else if (direction == 'in'){
		zoomfactor[0] *= 1.2
		zoomfactor[1] *= 1.2
	}else{
		new_pageWidth = _j(document).width();
		zoomfactor[0] = pageWidth/new_pageWidth
		zoomfactor[1] = 1
	}
	console.log(zoomfactor)
	d3Tree(jsonData,zoomfactor);
	
}

function pushProperty(parent,newData) {

	if (!parent){parent = jsonData}
	// newData ['property_name', [values]]
	// recursively find the current node in jsonData
    if (parent.isCurrNode) {
    	// check if key exits. If yes, replace value. If no, append new object
    	var found = false
    	for (var i=0; i < parent.properties.length; i++){
    		if (parent.properties[i].hasOwnProperty(newData[0])){
				if (newData[1].length){
					parent.properties[i][newData[0]] = newData[1]
				} else {
					// remove object if the newData array is empty (n/a was selected)
					parent.properties.splice(i, 1);
				}
    			found = true;
    		}
    	}
    	if (!found) {
    		if (newData[1].length){
	    		const newObj = new Object();
	    		newObj[newData[0]] = newData[1]
	    		parent.properties.push(newObj);
	    	}
    	}
    	// display the new JSON
		//renderJSON()
		renderTEXT()
		return false;
    }
    if (parent.children) {
        var count = parent.children.length;
        for (var i = 0; i < count; i++) {
            pushProperty(parent.children[i],newData);
        }
    }
}

function renderTEXT(){
	// d3 adds circular parent dependecies which we don't need (or want)
	removeParents(jsonData);
	// push the new list of annotations to the screen
	displayText = extractAnnotations(jsonData,"");
	_j("#jsonContainer").html(displayText);
	// document.getElementById("jsonContainer").innerHTML = displayText;
}

function renderJSON(){

	// d3 adds circular parent dependecies which we don't need (or want)
	removeParents(jsonData);
	
	// push the new JSON data to the screen
	displayJson = removeProperties(JSON.stringify(jsonData, null, 2))
	document.getElementById("jsonContainer").innerHTML = displayJson

	// Scroll to position of the current node in the textarea
	example = document.getElementById("jsonContainer")
	example.selectionStart = example.selectionEnd = example.innerHTML.indexOf('isCurrNode": 1')
	example.blur()
	example.focus()
}


function formSubmit(element,feature,category){
	// e.stopPropagation();
	// e.preventDefault();
	let that = _j(element);
	let hasCurrNode = searchTree(jsonData)

	if (hasCurrNode == true){
	    let values = [];
	    const BreakError = {}; // because we can't use the 'break' keyword in a foreach loop
			try{
			    _j.each(that.find(".form-check-input:checked"), function(){
			    		if (_j(this).val() == "na"){
				    		values = []
				    		throw BreakError;
				    	}
			      values.push(_j(this).val());
			    });
	    } catch (err) {
				  if (err !== BreakError) throw err;
			};
	    // find the current node and add the property/values
	    pushProperty(jsonData,[that.attr("name"), values]);

	    // save to DB
	    saveAnnotation(confirmSaved,feature,category)

	}else{
		alert("You must select a node in the parse tree before you can add a property.")
	}
};



var timer; // this is out here so that the clearInterval has access to it.
function updateTimer(){
	clearInterval(timer);
  var sec = 0;

	function pad(val) {
	    return val > 9 ? val : "0" + val;
	}
	timer = setInterval(function () {
	    _j("#timer").html(pad(parseInt(sec/60,10)) +":"+ pad(++sec%60));
	}, 1000);
}


function getData(callBack,sentence_id,direction){
	
	_j.ajax({

	    url : 'api/v1/get_sentences_from_table',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data:JSON.stringify({ "sentence_id" : sentence_id,
	    					  "direction"   : direction,
	    					  "annotator_id": annotator_id
	    					}), // annotator_id is a global constant
	    success : function(res) {      
	    	console.log("getData",res)   
	    	if (res.length){
	    		_j("#prev_sentence, #next_sentence").removeClass("disabled")
	    		callBack(res)
	    	}else{
	    		_j("#"+direction+"_sentence").addClass("disabled")
	    	}
	        
	    },
	    error : function(request,error){
	        //console.log("Request: "+JSON.stringify(request));
	    }
	});

	
}

function get_stats(){
	_j.ajax({

	    url : 'api/v1/get_stats',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data:JSON.stringify({"annotator_id": annotator_id}), // annotator_id is a global constant
	    complete : function(res){
	    	  //console.log("complete stats", res)
	    },
	    success : function(res) {              
	       // console.log("success stats", res)
	        _j("#inprogress").text(res[0][0])
	    	_j("#completed").text(res[0][1])
	    },
	    error : function(request,error){
	       console.log("error: "+JSON.stringify(request));
	    }
	});
}

function getNextSentence(){
		// TODO: clear checkmarks
		getData(initTree,sentence_id,"next")
}
function getPrevSentence(){
		// TODO: clear checkmarks
		getData(initTree,sentence_id,"prev")
}

function nextProperty(element){

	if (_j(curr_feature).next().length){
		_j(curr_feature).next()[0].click()

	}else{
		// proceed to next tab
		let curr_tab = _j(document).find(".nav-link.active")
		curr_tab.next()[0].click()

		let _id = _j(curr_tab.next()[0]).attr("id").split("-")[1]
		let curr_feature = _j("#nav-"+_id).find(".list-group .list-group-item")[0]
		curr_feature.click()

	}

	_j(".GPT-response").text("")
	_j(".GPT-response").addClass("visually-hidden")

	d3Tree(resetNodeSelection(jsonData));

}




function confirmSaved(res){
	// this is the callback function to the saveAnnotation ajax.

    let myAlert = document.querySelector('.toast');
	  let bsAlert = new  bootstrap.Toast(myAlert);
	  bsAlert.show();
}

function saveAnnotation(callBack,feature,category){
	
	//date = new Date().toISOString().slice(0, 19).replace('T', ' ');

	console.log("feature,cat",feature,category)
	
	gpt_response = _j("#GPT_response_"+category).text()
	console.log("gpt_response",gpt_response)

	jsonData["gpt_response"] = gpt_response
	jsonData["feature_id"] = feature

	_j.ajax({

	    url : 'api/v1/save_annotation',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data: JSON.stringify(jsonData), //  global variable holding the current json annotation tree
	    complete : function(response)
	    {
	        console.log('Completed!!!',response.responseJSON);
	        jsonData["annotation_id"] = response.responseJSON
	        delete jsonData["gpt_response"]
	        delete jsonData["feature_id"]
	        // render the JSON
			// renderJSON()
	        renderTEXT()
	        get_stats()
	        callBack(response)
	    },
	    success : function(request) {     
	    		//console.log('Succes!!!');       
	    },
	    error : function(request,error)
	    {
	        console.log("error: "+JSON.stringify(request));
	    }
	});

	
}

function markCompleted(){
	
	_j.ajax({
		url : 'api/v1/mark_completed',
		type : 'POST',
		dataType:'json',
		contentType:'application/json',
		data: JSON.stringify({"annotation_id": jsonData["annotation_id"]}), 
		complete : function(request)
		{
			_j("#mark_completed i").removeClass("bi-lock").addClass("bi-lock-fill");

			get_stats()
			confirmSaved(request)
		},
		success : function(request) {     
			//console.log('Succes!!!');       
		},
		error : function(request,error)
		{
			console.log("error: "+JSON.stringify(request));
		}
	});
}


function set_curr_feature(element,feature){
	curr_feature = element
	_j(".GPT-response").text("")
	_j(".GPT-response").addClass("visually-hidden")
}
function get_curr_feature(){
	return curr_feature
	
}

function get_gpt_response(element,feature){
	sentence = _j("#sentence_container").text()
	// curr_feature = element

	_j(".GPT-response").text("")
	_j(".spinner-border").removeClass("visually-hidden")
	_j(".GPT-response").addClass("visually-hidden")

	_j.ajax({
		url : 'api/v1/get_gpt_response',
		type : 'POST',
		dataType:'json',
		contentType:'application/json',
		data: JSON.stringify({'sentence':sentence,'feature':feature}),
		complete : function(response){
			// _j(".GPT-response").append("---------completed--------")
		},
		success : function(response) {     
			console.log('GPT Succes!!!');    
			_j(".GPT-response").text(JSON.stringify(response))
			_j(".GPT-response").removeClass("visually-hidden").removeClass("text-danger")
			_j(".spinner-border").addClass("visually-hidden")   
		},
		error : function(request,error){
			console.log("Request: "+JSON.stringify(request));
			_j(".GPT-response").text("GPT encountered an error. Please try again later.")
			_j(".GPT-response").removeClass("visually-hidden").addClass("text-danger")
			_j(".spinner-border").addClass("visually-hidden")   
		}
	});
}

window.onload = function() {
	getData(initTree,sentence_id)
	get_stats()

}