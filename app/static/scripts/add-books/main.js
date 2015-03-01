var PROCESS_INTERVAL = 8888;
var REPROCESS_INTERVAL = PROCESS_INTERVAL + 1000;

/**
THE BOOK QUEUE. This is the internal representation of the book queue.
*/
var bookQueue = new Queue();

/**
Where the books eligible for reprocessing go.
*/
var reprocessQueue = [];

/**
This script will manipulate ids a lot. We derive certain converntions from the
actual ids of the hidden form field. This hidden form field is the one that
is mapped to the Flask form.

This variable is filled on document ready.
*/
var realFormIds = [];

/**
Problem: We don't have a way to determine if we should display the "Ooops..."
message from script status quickly. So, we add a visualQueue count.

Each time we add to the visual book queue, increment this. Each time we remove
(clear), decrement.
*/
var visualQueueCount = 0;

var visualQueue;

/**
Renders the "spine" display of the book list. Takes data from the proxy form
directly.

@return A div element which displays like a spine of a book. The div
element has the isbn for its id.
*/
function renderSpine(){
    var spine = document.createElement("div");
    spine.className = "unsaved_book queued_block";
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy");
    spine.id = isbn.val();
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

The DOM element representing the book is a required parameter since we use it to
map the Book object to its visual representation.
*/
function internalizeBook(spineDom){
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy").val();
    var title = $(allInputs).filter("#title-proxy").val();
    var genre = $(allInputs).filter("#genre-proxy").val();
    var authors = $(allInputs).filter("#authors-proxy").val();
    var illustrators = $(allInputs).filter("#illustrators-proxy").val();
    var editors = $(allInputs).filter("#editors-proxy").val();
    var translators = $(allInputs).filter("#translators-proxy").val();
    var publisher = $(allInputs).filter("#publisher-proxy").val();
    var printer = $(allInputs).filter("#printer-proxy").val();
    var year = $(allInputs).filter("#year-proxy").val();

    var bookObj = new Book(isbn, title, genre, authors, illustrators, editors,
      translators, publisher, printer, year, spineDom);

    window.bookQueue.enqueue(bookObj);
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
    var spine = renderSpine();
    internalizeBook(spine);
    window.visualQueue.enqueue(spine);
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
    var allInputs = $("#main-form input").not("#csrf_token");
    var limit = allInputs.length;

    for(var i = 0; i < limit; i++){
        var iid = allInputs[i].id;
        window.realFormIds.push(iid);
    }
}

/**
Send the actual, hidden form to the server via AJAX so that the data may be
saved.

@param domElement
    The book spine representing the book to be sent, as a DOM element.
*/
function sendSaveForm(domElement){

    function success(){
        $(domElement).removeClass("unsaved_book").addClass("saved_book");
    }

    function fail(){
        $(domElement).removeClass("unsaved_book").addClass("error_book");
    }

    function failRecover(){
        $(domElement).removeClass("unsaved_book").addClass("reprocess_book");
        reprocessQueue.push(domElement);
    }

    var data = {
        "csrf_token": document.getElementById("csrf_token").value,
        "isbn": document.getElementById("isbn").value,
        "title": document.getElementById("title").value,
        "genre": document.getElementById("genre").value,
        "authors": document.getElementById("authors").value,
        "illustrators": document.getElementById("illustrators").value,
        "editors": document.getElementById("editors").value,
        "translators": document.getElementById("translators").value,
        "publisher": document.getElementById("publisher").value,
        "printer": document.getElementById("printer").value,
        "year": document.getElementById("year").value
    }
    $.ajax("/book_adder", {
        "type": "POST",
        "data": data,
        "success": success,
        "statusCode":{
            400: fail,
            409: fail,
            500: failRecover
        }
    });
}

/**
Load from the given queue to the actual form. The queue object is expected to be
from Queue.js.

@param queue
    The queue object from which we fetch a book.
@return
    True if a book record was loaded successfuly into the actual form.
*/
function loadFromQueueToForm(queue){
    var fromQ = queue.dequeue();
    if(fromQ){
        var limit = window.realFormIds.length;

        for(var i = 0; i < limit; i++){
            document.getElementById(window.realFormIds[i]).value = fromQ[window.realFormIds[i]];
        }

        return fromQ;
    }

    return false;
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
    // TODO update!!!
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

    // Initialize the visualQueue
    var qContainer = document.createElement("span");
    qContainer.id = "bookq";
    var defItem = document.createElement("div");
    defItem.className = "queued_block empty_set";
    var defText = document.createElement("h3");
    defText.innerHTML = "Ooops. Nothing yet.";
    defItem.appendChild(defText);
    // Special styles to override from queued_block rule.
    defItem.style.padding = "5% inherit";
    var defs = {"defaultDisplay":defItem,
      "defaultLocation": document.getElementById("qContainer")};
    window.visualQueue = new VisualQueue(qContainer, defs);
    //document.getElementById("qContainer").appendChild(window.visualQueue.domContainer);
    window.visualQueue.render();

    // Event handlers
    $("#clear-proxy").click(clearProxyForm);
    $("#queue-book").click(queueBook);

    $("#autosave_label").click(function(){
        document.getElementById("auto-save-toggle").checked = !document.getElementById("auto-save-toggle").checked;
    });

    // Start the polling interval timers.
    setInterval(function(){
        if(document.getElementById("auto-save-toggle").checked){
            var foo = loadFromQueueToForm(window.bookQueue);
            if(foo){
                sendSaveForm(foo.domElement);
            }
        }
    }, PROCESS_INTERVAL);
    
    setInterval(function(){
        if(document.getElementById("auto-save-toggle").checked){
        }
    }, REPROCESS_INTERVAL);
});
