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








