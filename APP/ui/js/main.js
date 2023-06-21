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


_j(function() {
	const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
	const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
	
	const toastElList = document.querySelectorAll('.toast')
	const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl))

	// const myModal = document.getElementById('myModal')
	// const myInput = document.getElementById('myInput')

	// myModal.addEventListener('shown.bs.modal', () => {
	//   myInput.focus()
	// })
})




