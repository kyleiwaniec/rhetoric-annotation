var jsonData;

var sentence_id;
var curr_feature = null;


// Check if sentence id is in the url

if (GetURLParameter('sentence_id')){
	sentence_id = GetURLParameter('sentence_id')
	// remove query string
	window.history.replaceState(null, null, window.location.pathname);
} else {
	if (Cookies.get('sentence_id')){
		sentence_id = Cookies.get('sentence_id')
	}else{
		sentence_id = 1
		Cookies.set('sentence_id',sentence_id)
	}
}
function flagForReview(elem,annotation_id){
	
	var that = _j(elem)
	var aid;
	
	if(jsonData){
		aid = jsonData["annotation_id"]
	}else{
		aid = annotation_id
	}

	_j.ajax({
		url : 'api/v1/flag_for_review',
		type : 'POST',
		dataType:'json',
		contentType:'application/json',
		data: JSON.stringify({"annotation_id": aid}), 
		complete : function(response)
		{
			review_flag = response.responseJSON.review_flag

			// Add the review flag class
			if (review_flag==1){that.find("i").removeClass("bi-bookmark").addClass("bi-bookmark-fill")}
			else {that.find("i").removeClass("bi-bookmark-fill").addClass("bi-bookmark")}

			//confirmSaved(response)
			
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

_j(function() {
	const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
	const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
	
	const toastElList = document.querySelectorAll('.toast')
	const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl))


})




