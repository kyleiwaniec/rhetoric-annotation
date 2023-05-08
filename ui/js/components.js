function loadComponents(){

	var components = ["word",
					  "sentence",
					  "rhetoric",
					  "semcat"]

	for (let i = 0; i < components.length; i++){
		$.ajax({
		  url: "../components/"+components[i]+".html",
		  cache: false
		})
		  .done(function( html ) {
		    $( "#nav-"+components[i] ).append( html );
		  });
	}
	
}