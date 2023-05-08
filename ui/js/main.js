var jsonData;
var sentence_id;
var curr_feature = null;
const annotator_id = 1;



//////////////////////////////////////////////////////////////////
// Remember the last sentence visited

if (Cookies.get('sentence_id')){
	sentence_id = Cookies.get('sentence_id')
}else{
	sentence_id = 1
	Cookies.set('sentence_id',sentence_id)
}
//////////////////////////////////////////////////////////////////


function initTree(DBdata) {

	sentence_id = DBdata[0].sentence_id
	Cookies.set('sentence_id',sentence_id)


	let parse_string = DBdata[0].parse_string
	// Escape backslashes and Parse the string into JSON (defined in parser.js)
	parse_string = parse_string.replace(/\\/g, "\\\\");
 
	let article_id = DBdata[0].article_id
	let techniques = DBdata[0].technique
	let text 			 = DBdata[0].text
	let annotation = DBdata[0].annotation
	let annotation_id = DBdata[0].annotation_id



	if (annotation.length > 1){
		jsonData = JSON.parse(annotation)
		jsonData['annotation_id'] = annotation_id // (because this would have been set to 0 on initial insert. yup, it's ugly.)
	}
	else {
		jsonData = parse(parse_string, article_id, sentence_id, annotation_id, annotator_id, techniques);
	}
	document.getElementById("sentence_container").innerHTML = "<p>"+text+"</p>";
	
	d3Tree(jsonData);

	// parents are removed to get rid of circular dependencies
	removeParents(jsonData);

	// render the JSON
	displayJson = removeProperties(JSON.stringify(jsonData, null, 2))

	document.getElementById("jsonContainer").value = displayJson;
	
	// reload the GPT response
	if (curr_feature){
			$(curr_feature).click();
		}

	return false;
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
		renderJSON()
		return;

    }
    
    if (parent.children) {
        var count = parent.children.length;
        for (var i = 0; i < count; i++) {
            pushProperty(parent.children[i],newData);
        }
    }

}



function renderJSON(){

	// d3 adds circular parent dependecies which we don't need (or want)
	removeParents(jsonData);
	
	// push the new JSON data to the screen
	
	displayJson = removeProperties(JSON.stringify(jsonData, null, 2))
	document.getElementById("jsonContainer").value = displayJson

	// Scroll to position of the current node in the textarea
	example = document.getElementById("jsonContainer")
	example.selectionStart = example.selectionEnd = example.value.indexOf('isCurrNode": 1')
	example.blur()
	example.focus()
}


function formSubmit(element){
	// e.stopPropagation();
	// e.preventDefault();
	let that = $(element);
	let hasCurrNode = searchTree(jsonData)

	if (hasCurrNode == true){
	    let values = [];
	    const BreakError = {}; // because we can't use the 'break' keyword in a foreach loop
			try{
			    $.each(that.find(".form-check-input:checked"), function(){
			    		if ($(this).val() == "na"){
				    		values = []
				    		throw BreakError;
				    	}
			      values.push($(this).val());
			    });
	    } catch (err) {
				  if (err !== BreakError) throw err;
			};
	    // find the current node and add the property/values
	    pushProperty(jsonData,[that.attr("name"), values]);

	    // save to DB
	    saveAnnotation(confirmSaved)

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
	    $("#timer").html(pad(parseInt(sec/60,10)) +":"+ pad(++sec%60));
	}, 1000);
}


function getData(callBack,sentence_id,direction){
	
	$.ajax({

	    url : 'http://127.0.0.1:5000/api/v1/get_sentences_from_table',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data:JSON.stringify({ "sentence_id" : sentence_id,
	    											"direction"   : direction,
	    											"annotator_id": annotator_id
	    										}), // annotator_id is a global constant
	    success : function(res) {              
	        callBack(res)
	    },
	    error : function(request,error)
	    {
	        console.log("Request: "+JSON.stringify(request));
	    }
	});

	
}

function get_stats(){
	$.ajax({

	    url : 'http://127.0.0.1:5000/api/v1/get_stats',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data:JSON.stringify({"annotator_id": annotator_id}), // annotator_id is a global constant
	    complete : function(res){
	    	  console.log("complete stats", res)
	    },
	    success : function(res) {              
	        console.log("success stats", res)
	        $("#inprogress").text(res[0][0])
	    	  $("#completed").text(res[0][1])
	    },
	    error : function(request,error){
	        console.log("error: "+JSON.stringify(request));
	    }
	});
}

function getNextSentence(){
		getData(initTree,sentence_id,"next")
}
function getPrevSentence(){
		getData(initTree,sentence_id,"prev")
}

function nextProperty(element){

	if ($(curr_feature).next().length){
		$(curr_feature).next()[0].click()

	}else{
		// proceed to next tab
		let curr_tab = $(document).find(".nav-link.active")
		curr_tab.next()[0].click()

		let _id = $(curr_tab.next()[0]).attr("id").split("-")[1]
		let curr_feature = $("#nav-"+_id).find(".list-group .list-group-item")[0]
		curr_feature.click()

	}
}


function confirmSaved(res){
	// this is the callback function to the saveAnnotation ajax.

    let myAlert = document.querySelector('.toast');
	  let bsAlert = new  bootstrap.Toast(myAlert);
	  bsAlert.show();
}

function saveAnnotation(callBack){
	
	//date = new Date().toISOString().slice(0, 19).replace('T', ' ');

	$.ajax({

	    url : 'http://127.0.0.1:5000/api/v1/save_annotation',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data: JSON.stringify(jsonData), //  global variable holding the current json annotation tree
	    complete : function(request)
	    {
	        console.log('Completed!!!');
	        get_stats()
	        callBack(request)
	    },
	    success : function(request) {     
	    		console.log('Succes!!!');       
	    },
	    error : function(request,error)
	    {
	        console.log("error: "+JSON.stringify(request));
	    }
	});

	
}

function markCompleted(){
	
	$.ajax({

	    url : 'http://127.0.0.1:5000/api/v1/mark_completed',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data: JSON.stringify({"annotation_id": jsonData["annotation_id"]}), 
	    complete : function(request)
	    {
	        console.log('Completed!!!');
	        get_stats()
	        confirmSaved(request)
	    },
	    success : function(request) {     
	    		console.log('Succes!!!');       
	    },
	    error : function(request,error)
	    {
	        console.log("error: "+JSON.stringify(request));
	    }
	});
}


function get_gpt_response(element,feature){
	sentence = $("#sentence_container").text()
	curr_feature = element

  $(".spinner-border").removeClass("visually-hidden")
  $(".GPT-response").addClass("visually-hidden")

	$.ajax({

	    url : 'http://127.0.0.1:5000/api/v1/get_gpt_response',
	    type : 'POST',
	    dataType:'json',
	    contentType:'application/json',
	    data: JSON.stringify({'sentence':sentence,'feature':feature}),
	    complete : function(response){

	        // callBack(request)
	    		$(".GPT-response").text(response.responseText)
	    		$(".GPT-response").removeClass("visually-hidden")
	    		$(".spinner-border").addClass("visually-hidden")
	    },
	    success : function(request) {     
	    		console.log('Succes!!!');       
	    },
	    error : function(request,error){
	        console.log("Request: "+JSON.stringify(request));
	    }
	});
}



window.onload = function() {
	const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
	const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
	
	const toastElList = document.querySelectorAll('.toast')
	const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl))


	getData(initTree,sentence_id)
	loadComponents()
	get_stats()

}
