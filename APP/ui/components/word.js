// https://wesbos.com/template-strings-html
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals




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
_j(document).on("click", ".list-group-item-action i .more-info-modal", function (e) {
     var title = _j(this).attr('data-bs-title');
     var body = _j(this).attr('data-bs-body');
     _j(".modal .modal-title").text( title );
     _j(".modal .modal-body").text( body );
});

_j.ajax({

    url : '/api/v1/get_word_properties',
    type : 'POST',
    dataType:'json',
    contentType:'application/json',
    complete : function(response){
        
        const word_properties = JSON.parse(response.responseText)

        const word_markup = `
					<div class="row">
					  <div class="col-4">
					    <div class="list-group" id="list-tab" role="tablist">
					    	${word_properties.map(property => `<a class="list-group-item list-group-item-action" 
					    										onclick="set_curr_feature(this,'${property.key}'); updateTimer(); return false" 
					    										id="list-${replaceSpaces(property.key)}-list" 
					    										data-bs-toggle="list" href="#list-${replaceSpaces(property.key)}" 
					    										role="tab" aria-controls="list-${replaceSpaces(property.key)}">
					    										<span>
			    												<i class="bi bi-info-circle" 
			    													data-bs-toggle="modal" 
			    													data-bs-target="#wordModal"
			    													data-bs-title="${property.key}"
			    													data-bs-body="${property.moreinfo}">
			    												</i></span>&nbsp;&nbsp;${property.key}</a>`).join('')}
						</div>
					  </div>
					  <div class="col-8">
					    <div class="tab-content" id="nav-tabContent">
					    	${word_properties.map(property => `<div class="tab-pane fade" id="list-${replaceSpaces(property.key)}" role="tabpanel" aria-labelledby="list-${replaceSpaces(property.key)}-list">
						      		<p><a class="btn btn-primary" onclick="get_gpt_response(this,'${property.key}'); return false;">
						      			Ask ChatGPT</a>

						      			<a class="btn btn-primary more-info-modal"
						      					data-bs-toggle="modal" 
												data-bs-target="#wordModal"
												data-bs-title="${property.key}"
												data-bs-body="${property.moreinfo}">
							      			<i class="bi bi-info-circle"></i> 
							      			More info
										</a>

						      		</p>

						      		<div id="${replaceSpaces(property.key)}_GPT">
						      			<div class="GPT-response" id="GPT_response_word"></div>
						      			<div class="spinner-border visually-hidden" role="status">
											  <span class="visually-hidden">Loading...</span>
										</div>
						      		</div>
						      		
						      		<form name="${replaceSpaces(property.key)}" onsubmit="formSubmit(this,'${replaceSpaces(property.key)}','word'); return false;">
							      		

							      		<ul class="list-group mb-3 mt-3">
							      			${renderValues(property.values,property.descriptions)}
							      		</ul>	
						    			<div class="sticky-bottom p-3 bg-opacity-50 bg-dark">
											<input type="submit" value="Add Property" type="button" class="btn btn-primary"/>
											<input value="Next Property" type="button" class="btn btn-warning" onclick="return nextProperty(this)"/>
											<input id="removePropertyButton" value="Remove Property" type="button" class="btn btn-danger float-end" 
												onclick="pushProperty(false,['${replaceSpaces(property.key)}',[]]); saveAnnotation(confirmSaved,'${replaceSpaces(property.key)}','word'); return false;"/>
										</div>
									</form>
						    </div>`).join('')}
						  </div>
						</div>
					</div>
					<!-- Modal -->
					<div class="modal fade" id="wordModal" tabindex="-1" aria-labelledby="wordModalLabel" aria-hidden="true" data-bs-theme="dark">
					  <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
					    <div class="modal-content">
					      <div class="modal-header">
					        <h1 class="modal-title fs-5" id="wordModalLabel">...</h1>
					        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
					      </div>
					      <div class="modal-body">
					        ...
					      </div>
					      
					    </div>
					  </div>
					</div>
					`


					document.getElementById("nav-word").innerHTML = word_markup;

       
    },
    success : function(request) {     
    		//console.log('Succes!!!');       
    },
    error : function(request,error)
    {
        console.log("error: "+JSON.stringify(request));
    }
})







      
