/**
Renders the "spine" display of the book list. Takes data from global
variables directly.

The global variables are expected to have the following attributes:
  spineDisplay
    A function returning a string. This string will be the one displayed
    on the "spine". Include line breaks (as <br> tags).

@return The text formatted like a spine of a book.
*/
function renderSpine(){
    window.spine = ["title", "authors", "illustrators", "translators", "editors", "publisher", "printer", "year"];
    var spineText = "";
    var limit = window.spine.length;
    
    for(var i = 0; i < limit; i++){
        spineText += window.bookDetailsForm[spine[i]].spineDisplay();
    }
    
    return spineText;
}

/**
Clears the details form.
*/
function clear(){
    var fields = getDetailFormFields();
    var fieldLimit = fields.length;
    
    for(var i = 0; i < fieldLimit; i++){
        fields[i].value = "";
    }
}

/**
Returns a function that returns a by line, labeled with
argument _by_. The names displayed with the by line is
specified through argument _lineVal_.

@param by
@param lineVal
*/
function getLabeledByLine(by, lineVal){
    return function(){
        if(lineVal == ""){
            return "";
        } else{
            return "<strong>" + by + " by:</strong> " + lineVal;
        }
    }
}

$.validator.addMethod("isbn", function(value, element, param){
    var stripped = stripExtraneous(value);
    return verifyISBN10(stripped) || verifyISBN13(stripped);
}, "Invalid ISBN input.");

/*
Just check if it is a 4-digit number.
*/
$.validator.addMethod("year", function(value, element, param){
    return /^\d{4}$/.test(value);
}, "Please enter a valid year.");

$(document).ready(function(){
    $("#detailsForm").validate({
        rules:{
            isbn1:{
                isbn: true
            },
            year1:{
                year: true
            }
        }
    });
    
    $("[name='add']").click(function(){
        if($("#detailsForm").valid()){
            addRecord();
            clear();
        }
    });
})
