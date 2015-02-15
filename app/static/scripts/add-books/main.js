/**
THE BOOK QUEUE. This is the internal representation of the book queue.
*/
var bookQueue = [];

/**
This script will manipulate ids a lot. We derive certain converntions from the
actual ids of the hidden form field. This hidden form field is the one that
is mapped to the Flask form.

This variable is filled on document ready.
*/
var realFormIds = [];

/**
Renders the "spine" display of the book list. Takes data from global
variables directly.

The global variables are expected to have the following attributes:
  spineDisplay
    A function returning a string. This string will be the one displayed
    on the "spine". Include line breaks (as <br> tags).

@return A div element which displays like a spine of a book.
*/
function renderSpine(){
    var spine = document.createElement("div");
    spine.className = "unsaved_book queued_block";
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy");
    var title = $(allInputs).filter("#title-proxy");
    var authors = $(allInputs).filter("#authors-proxy");

    var isbnText = document.createElement("h3");
    isbnText.innerHTML = isbn.val();

    var titleText = document.createElement("h2");
    titleText.innerHTML = title.val();

    var authorsText = document.createElement("h3");
    authorsText.innerHTML = authors.val();

    spine.appendChild(isbnText);
    spine.appendChild(titleText);
    spine.appendChild(authorsText);

    return spine;
}

/**
Append the book described in #proxy-form to the internal queue.
*/
function internalizeBook(){
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy");
    var title = $(allInputs).filter("#title-proxy");
    var genre = $(allInputs).filter("#genre-proxy");
    var authors = $(allInputs).filter("#authors-proxy");
    var illustrators = $(allInputs).filter("#illustrators-proxy");
    var editors = $(allInputs).filter("#editors-proxy");
    var translators = $(allInputs).filter("#translators-proxy");
    var publisher = $(allInputs).filter("#publisher-proxy");
    var printer = $(allInputs).filter("#printer-proxy");
    var year = $(allInputs).filter("#year-proxy");

    var bookObj = new Book(isbn, title, genre, authors, illustrators, editors,
      translators, publisher, printer, year);

    window.bookQueue.push(bookObj);
}

/**
Generates the delete button to be added at the end
of every row record.
*/
function renderDeleteButton(){
    var container = document.createElement("input");
    container.onclick = removeRow;
    container.type = "button";
    container.className = "btn infrequent";
    container.value = "X";
    
    return container;
}

/**
Clears the proxy form.
*/
function clearProxyForm(){
    $("#proxy-form input").val("")
}

/**
Event handler for clicking "Save Book" button in the proxy form.
*/
function queueBook(){
    if(window.bookQueue.length == 0){
        $("#bookq").empty();
    }
    internalizeBook();
    var spine = renderSpine();
    $("#bookq").append(spine);
    clearProxyForm();
}

/**
Remove the book spine that triggered the event.

If the block is already saved to DB, delete the pertaining record as well. (UI
Note: ask user to verify first). If block is not yet saved to DB, just delete.

@param e
  The event object.
*/
function removeBlock(e){
    // TODO
}

/**
Clear the actual form.

It is important to clear the actual form after every send to server. Else,
we might get mixed data! (Consider the scenario where a record with an illustrator
follows a record with no illustrator.)
*/
function clearActualForm(){
    $("#main-form input").not("csrf_token").val("");
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

/**
Fill up the realFormIds variable. No guarantee is made as to the order of the
elements inserted into realFormIds.
*/
function getFormIds(){
    var allInputs = $("#main-form input").not("csrf_token");
    var limit = allInputs.length;

    for(var i = 0; i < limit; i++){
        var iid = allInputs[i].id;
        window.realFormIds.push(iid);
    }
}

/**
Send the actual, hidden form to the server via AJAX so that the data may be
saved.

Note: Uses goody jquery form plugin. Don't look surprised.
*/
function sendSaveForm(){
    // TODO
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
    getFormIds();
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

    $("#main-form").ajaxForm(sendSaveForm);

    // Event handlers
    $("#clear-proxy").click(clearProxyForm);
    $("#queue-book").click(queueBook);
    // TODO Start the polling timer.
})
