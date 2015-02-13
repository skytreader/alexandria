/**
Functions in this file will deal with the book queue system add-book
attempts.

@author Chad Estioco
*/

/**
Remove the block that triggered the event.

If the block is already saved to DB, delete the pertaining record as well
(UI Note: ask user to verify first). If block is not yet saved to DB, just
delete.

@param e
  The event object.
*/
function removeBlock(e){
	//Get the button
	var button = e.target;
	//Get the cell
	var cell = button.parentNode;
	//Get the row
	var row = cell.parentNode;
	
	window.booklistTableBody.removeChild(row);
	
	// Check if table body became empty
	if(window.booklistTableBody.children.length == 0){
		var soleCell = document.createElement("td");
		soleCell.innerHTML = "No records yet.";
		window.booklistTableBody.appendChild(soleCell);
	}
}

/**
Generates the delete button to be added at the end
of every row record.
*/
function deleteButton(){
	var container = document.createElement("input");
	container.onclick = removeRow;
	container.type = "button";
	container.className = "btn infrequent";
	container.value = "X";
	
	return container;
}

/**
Returns all the form fields in the detailsForm as an array.
No order is guaranteed on the return array.
*/
function getDetailFormFields(){
	var fields = new Array();
	var blockDivs = $("#detailsForm").children(".block");
	var divLimit = blockDivs.length;
	
	for(var i = 0; i < divLimit; i++){
		var inputs = $(blockDivs[i]).children("input");
		var inputLimit = inputs.length;
		
		for(var j = 0; j < inputLimit; j++){
			fields.push(inputs[j]);
		}
	}
	
	return fields;
}
