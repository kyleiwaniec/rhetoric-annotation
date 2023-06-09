function settime(){
	let date = new Date(); 
  let hh = date.getHours();
  let mm = date.getMinutes();
  let ss = date.getSeconds();
  let session = "AM";

  if(hh == 0){
      hh = 12;
  }
  if(hh > 12){
      hh = hh - 12;
      session = "PM";
   }

   hh = (hh < 10) ? "0" + hh : hh;
   mm = (mm < 10) ? "0" + mm : mm;
   ss = (ss < 10) ? "0" + ss : ss;
    
   let time = hh + ":" + mm + ":" + ss;
   
		$("#timer").text(time)
		let t = setTimeout(function(){ settime() }, 1000);
}


function removeProperties(s){
  pattern = /\s*("depth"|"x"|"y"|"id"|"x0"|"y0").*/g
  return s.replace(pattern,'')
}

// Removes circular dependencies
function removeParents(obj) {
  for(prop in obj) {
    if (prop === 'parent')
      delete obj[prop];
    else if (typeof obj[prop] === 'object')
      removeParents(obj[prop]);
  }
}

// extracts the annotations to display as list
function extractAnnotations(node,textData){
  if (node.properties.length > 0){
    let fragment = getYield(node,"") //": "+fragment+ 
    textData = textData.concat(node.name +": "+JSON.stringify(node.properties) +"\n");
  }
  if (node.children != null){
    for(var i=0; i < node.children.length; i++){
         textData = extractAnnotations(node.children[i],textData);
    }
  }
  return textData;
}


function searchTree(element){
    if(element.isCurrNode){
          return true;
    }else if (element.children != null){
          var i;
          var result = null;
          for(i=0; result == null && i < element.children.length; i++){
               result = searchTree(element.children[i]);
          }
          return result;
    }
    return null;
}

// reconstructs the string from the json (with extra spaces for puntuation :( )
function getYield(node, string){
  if (node.children == null) string = string.concat(node.name, " ");
  else {
    for (var i in node.children) {
      var child = node.children[i];
      string = getYield(child, string);
    }
  }
  return string.trim();
}


function getObjectLocation(obj,names){
  if (obj.parent){
    names.push(obj.parent.name)
    getObjectLocation(obj.parent,names)
  }
  return names;
}