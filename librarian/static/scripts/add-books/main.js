var PROCESS_INTERVAL = 8888;
var REPROCESS_INTERVAL = PROCESS_INTERVAL + 1000;
var CREATORS = ["author", "illustrator", "editor", "translator"];

/**
THE BOOK QUEUE. This is the internal representation of the book queue.
*/
var bookQueue = new Queue();

/**
Where the books eligible for reprocessing go.
*/
var reprocessQueue = new Queue();

/**
This script will manipulate ids a lot. We derive certain converntions from the
actual ids of the hidden form field. This hidden form field is the one that
is mapped to the Flask form. These are the fields to be included in the request.
*/
var realFormIds = ["isbn", "title", "genre", "authors", "illustrators",
  "editors", "translators", "year", "publisher", "printer"];

var visualQueue;

var booksSaved = 0;
var booksErrorNoRetry = 0;
var booksReprocessable = 0;

var BOOK_PERSONS_LASTNAME = [];
var BOOK_PERSONS_FIRSTNAME = [];
var COMPANIES = [];
var GENRES = [];
/**
This is needed by the loadToForm method.

Maps the creator type to the event handler used to add an entry to the creator list.
*/
var CREATOR_ADD_HANDLERS = {};

function updateStatCounts(){
    $("#unsaved-count").text("" + visualQueue.getLength());
    $("#saved-count").text("" + booksSaved);
    $("#error-count").text("" + booksErrorNoRetry);
    $("#reprocessed-count").text("" + booksReprocessable);
}

/**
I am not sure if this is a good idea.
*/
function fillGenres(){
    $.ajax("/api/list/genres", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            window.GENRES = data["data"];
            $("#genre-proxy").autocomplete({
                source: window.GENRES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(window.fillGenres, 8000);
        }
    });
}

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

    var isbnText = document.createElement("h3");
    isbnText.innerHTML = isbn.val();

    var titleText = document.createElement("h2");
    titleText.innerHTML = title.val();

    var authorsText = document.createElement("h3");
    authorsText.innerHTML = listNames(getCreatorNames("author"));

    spine.appendChild(isbnText);
    spine.appendChild(titleText);
    spine.appendChild(authorsText);

    return spine;
}

/**
Get a ;ist of persons and return a string to display them..
*/
function listNames(nameList){
    var names = [];
    for(var i = 0; i < nameList.length; i++){
        names.push(nameList[i].lastname + ", " + nameList[i].firstname);
    }

    return  names.join("; ");
}

/**
Get all the names entered for the given creator.

This relies _a lot_ on the guaranteed return order of jQuery selectors. At least,
it must be guaranteed that the order of lastnames and firstnames returned is the
same.

Returns a list of Person objects.
*/
function getCreatorNames(creator){
    console.info("looking for", creator);
    var creatorsLastname = $("[name='" + creator + "-proxy-lastname']");
    var creatorsFirstname = $("[name='" + creator + "-proxy-firstname']");
    var persons = [];

    for(var i = 0; i < creatorsLastname.length; i++){
        var firstname = creatorsFirstname[i].value.trim();
        var lastname = creatorsLastname[i].value.trim();
        if(firstname != "" && lastname != ""){
            persons.push(new Person(lastname, firstname));
        }
    }

    return persons;
}

/**
Append the book described in #proxy-form to the internal queue.

The DOM element representing the book is a required parameter since we use it to
map the Book object to its visual representation.

@param spineDom
    The DOM element representing the book spine. This is just necessary for
    mapping.
*/
function internalizeBook(spineDom){
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy").val();
    var title = $(allInputs).filter("#title-proxy").val();
    var genre = $(allInputs).filter("#genre-proxy").val();
    var authors = JSON.stringify(getCreatorNames("author"));
    var illustrators = JSON.stringify(getCreatorNames("illustrator"));
    var editors = JSON.stringify(getCreatorNames("editor"));
    var translators = JSON.stringify(getCreatorNames("translator"));
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
Create a list element for displaying a creator's name. The name displayed is
dependent on what is currently entered in the procy fields for this creator.

TODO Test me
*/
function renderContentCreatorListing(creatorType){
    var hiddenLastnameProxy = document.createElement("input");
    hiddenLastnameProxy.type = "hidden";
    hiddenLastnameProxy.name = creatorType + "-proxy-lastname";

    var hiddenFirstnameProxy = document.createElement("input");
    hiddenFirstnameProxy.type = "hidden";
    hiddenFirstnameProxy.name = creatorType + "-proxy-firstname";

    var divRow = document.createElement("div");
    $(divRow).addClass("row");

    var delCol = document.createElement("div");
    $(delCol).addClass("col-xs-1 del-col");

    var nameCol = document.createElement("div");
    $(nameCol).addClass("col-xs-11");

    divRow.appendChild(delCol);
    divRow.appendChild(nameCol);

    var lastName = $("#" + creatorType + "-proxy-lastname").val().trim();
    var firstName = $("#" + creatorType + "-proxy-firstname").val().trim();
    hiddenLastnameProxy.value = lastName;
    hiddenFirstnameProxy.value = firstName;
    clearCreatorInput(creatorType);
    var nameElement = document.createElement("span");
    nameElement.innerHTML = lastName + ", " + firstName;

    nameCol.appendChild(nameElement);

    var deleteButton = document.createElement("i");
    $(deleteButton).addClass("fa fa-times-circle")
      .click(recordDeleterFactory(creatorType));

    delCol.appendChild(deleteButton);

    var listing = document.createElement("li");
    listing.appendChild(divRow);
    listing.appendChild(hiddenLastnameProxy);
    listing.appendChild(hiddenFirstnameProxy);

    return listing;
}

function clearCreatorInput(creatorType){
    $("#" + creatorType + "-proxy-lastname").val("");
    $("#" + creatorType + "-proxy-firstname").val("");
}

function recordDeleterFactory(creatorType){
    return function() {
        $(this.parentNode.parentNode).remove();
    }
};

/**
Clears the proxy form.
*/
function clearProxyForm(){
    $("#proxy-form input").val("")
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
Send the actual, hidden form to the server via AJAX so that the data may be
saved.

@param domElement
    The book spine representing the book to be sent, as a DOM element.
*/
function sendSaveForm(domElement){

    function success(){
        $(domElement).removeClass("unsaved_book").addClass("saved_book");
        window.booksSaved++;
    }

    function fail(){
        $(domElement).removeClass("unsaved_book").addClass("error_book");
        window.booksErrorNoRetry++;
    }

    function failRecover(){
        $(domElement).removeClass("unsaved_book").addClass("reprocess_book");
        reprocessQueue.enqueue(domElement);
        window.booksReprocessable++;
    }

    var data = {
        "csrf_token": document.getElementById("csrf_token").value,
        "isbn": stripExtraneous(document.getElementById("isbn").value),
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
    $.ajax("/api/book_adder", {
        "type": "POST",
        "data": data,
        "success": success,
        "statusCode":{
            400: fail,
            409: fail,
            500: failRecover
        },
        "complete": updateStatCounts
    });
}

/**
TODO I thought of this method to automate my testing but I realized this could
also be useful for a "reprocess" feature. If saving a book fails, you can reload
the book's record into the form and redo what you think failed.
*/
function loadToForm(reqData){
    
    function insertAllCreators(all, type){
        for(var i = 0; i < all.length; i++){
            $("#" + type + "-proxy-firstname").val(all[i].firstname);
            $("#" + type + "-proxy-lastname").val(all[i].lastname);
            CREATOR_ADD_HANDLERS[type]();
        }
    }

    $("#isbn-proxy").val(reqData.isbn);
    $("#title-proxy").val(reqData.title);
    $("#genre-proxy").val(reqData.genre);
    $("#publisher-proxy").val(reqData.publisher);
    $("#printer-proxy").val(reqData.printer);
    $("#year-proxy").val(reqData.year);
    insertAllCreators(reqData.authors, "author");
    insertAllCreators(reqData.illustrators, "illustrator");
    insertAllCreators(reqData.editors, "editor");
    insertAllCreators(reqData.translators, "translator");
}

/**
Clear all the user listings of their children li elements.
*/
function clearLists(){
    for(var i = 0; i < CREATORS.length; i++){
        $("#" + CREATORS[i] + "-list").empty();
    }
}

$.validator.addMethod("isbnVal", function(value, element, param){
    var stripped = stripExtraneous(value);
    return verifyISBN10(stripped) || verifyISBN13(stripped);
}, "Invalid ISBN input.");

/*
Just check if it is a 4-digit number.
*/
$.validator.addMethod("yearVal", function(value, element, param){
    return /^\d{4}$/.test(value);
}, "Please enter a valid year.");

$(document).ready(function(){
    /**
    Return a function that generates an input row for a given creatorType. The
    generated function was meant to be called for the click event on the add button.
    */
    function rendererFactory(creatorType){
        return function(){
            var name = document.createElement("li");
            var inputLine = renderContentCreatorListing(creatorType);
    
            document.getElementById(creatorType + "-list").appendChild(inputLine);
        }
    }

    /**
    Load from the given queue to the actual form. The queue object is expected to 
    be from Queue.js.
    
    @param queue
        The queue object from which we fetch a book.
    @return
        True if a book record was loaded successfuly into the actual form.
    */
    function loadFromQueueToForm(queue){
        var fromQ = queue.dequeue();
    
        if(fromQ){
            var limit = window.realFormIds.length;
            console.log("fromQ is", fromQ);
    
            for(var i = 0; i < limit; i++){
                document.getElementById(window.realFormIds[i]).value = fromQ[window.realFormIds[i]];
                console.log("got this", fromQ[window.realFormIds[i]]);
            }
    
            return fromQ;
        }
    
        return false;
    }

    $("#proxy-form").validate({
        rules:{
            "isbn-rule":{
                isbnVal: true,
                required: true,
                maxlength: 13
            },
            "year-rule":{
                yearVal: true,
                required: true
            },
            "genre-rule":{
                required: true,
                maxlength: 40
            },
            "title-rule":{
                required: true
            },
            "publisher-rule":{
                required: true
            }
        }
    });

    fillGenres();

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
    window.visualQueue.render();
    updateStatCounts();

    // Event handlers
    $("#clear-proxy").click(clearProxyForm);
    $("#queue-book").click(function(){
        if($("#proxy-form").valid()){
            var spine = renderSpine();
            internalizeBook(spine);
            window.visualQueue.prepend(spine);
            updateStatCounts();
            clearProxyForm();
            clearLists();
        }
    });

    $("#autosave_label").click(function(){
        document.getElementById("auto-save-toggle").checked = !document.getElementById("auto-save-toggle").checked;
    });

    // Start the polling interval timers.
    setInterval(function(){
        console.debug("Polling main")
        if(document.getElementById("auto-save-toggle").checked){
            var foo = loadFromQueueToForm(window.bookQueue);
            if(foo){
                sendSaveForm(foo.domElement);
            }
        }
    }, PROCESS_INTERVAL);
    
    setInterval(function(){
        console.debug("Polling reprocess");
        if(document.getElementById("auto-save-toggle").checked){
            var foo = loadFromQueueToForm(window.reprocessQueue);
            if(foo){
                sendSaveForm(foo.domElement);
            }
        }
    }, REPROCESS_INTERVAL);

    CREATORS.forEach(function(creatorTitle){
        CREATOR_ADD_HANDLERS[creatorTitle] = rendererFactory(creatorTitle);
        $("#" + creatorTitle + "-add").click(CREATOR_ADD_HANDLERS[creatorTitle]);
    }); });
