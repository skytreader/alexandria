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

/**
Problem: We don't have a way to determine if we should display the "Ooops..."
message from script status quickly. So, we add a visualQueue count.

Each time we add to the visual book queue, increment this. Each time we remove
(clear), decrement.
*/
var visualQueueCount = 0;

var visualQueue;

var booksSaved = 0;
var booksErrorNoRetry = 0;
var booksReprocessable = 0;

var BOOK_PERSONS_LASTNAME = [];
var BOOK_PERSONS_FIRSTNAME = [];
var COMPANIES = [];
var GENRES = [];

function updateStatCounts(){
    $("#unsaved-count").text("" + visualQueueCount);
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
    var authors = $(allInputs).filter("#authors-proxy");

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
it must be uuaranteed that the order of lastnames and firstnames returned is the
same.

Returns a list of Person objects.
*/
function getCreatorNames(creator){
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

function renderNameInput(creatorType, namePart){
    var placeholder = namePart.capitalize();
    var textbox = document.createElement("input");
    textbox.type = "text";
    textbox.placeholder = placeholder;
    $(textbox).addClass("form-control");
    textbox.name = creatorType + "-proxy-" + namePart;

    return textbox;
}

/**
Create an "input line" for content creators.
*/
function renderContentCreatorInput(creatorType){
    var rowContainer = document.createElement("div");
    $(rowContainer).addClass("row");
    
    var lastnameCol = document.createElement("div");
    $(lastnameCol).addClass("col-md-5");
    
    var lastnameInput = renderNameInput(creatorType, "lastname");
    lastnameCol.appendChild(lastnameInput);

    var firstnameCol = document.createElement("div");
    $(firstnameCol).addClass("col-md-5");

    var firstnameInput = renderNameInput(creatorType, "firstname");
    firstnameCol.appendChild(firstnameInput);

    var deleteCol = document.createElement("div");
    $(deleteCol).addClass("col-md-2");

    var deleteButton = document.createElement("i");
    $(deleteButton).addClass("fa fa-minus-circle fa-2x clickable");
    $(deleteButton).click(recordDeleterFactory(creatorType));
    
    deleteCol.appendChild(deleteButton);

    rowContainer.appendChild(lastnameCol);
    rowContainer.appendChild(firstnameCol);
    rowContainer.appendChild(deleteCol);

    return rowContainer;
}

function recordDeleterFactory(creatorType){
    return function() {
        if(document.getElementById(creatorType + "-list").children.length != 1){
            $(this.parentNode.parentNode).remove();
        }

        // Check if after removing a row, we should disable deletions for
        // the time being.
        if(document.getElementById(creatorType + "-list").children.length == 1){
            $("#" + creatorType + "-list .fa-minus-circle").addClass("disabled");
        }
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
            if(i != 0){
                var creatorInput = renderContentCreatorInput(type);
                $(creatorInput).find("[name='" + type + "-proxy-lastname']")
                  .val(all[i].lastname);
                $(creatorInput).find("[name='" + type + "-proxy-firstname']")
                  .val(all[i].firstname);
                document.getElementById(type + "-list").appendChild(creatorInput);
            } else{
                $("[name='" + type + "-proxy-lastname']").val(all[i].lastname);
                $("[name='" + type + "-proxy-firstname']").val(all[i].firstname);
            }
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
            var inputLine = renderContentCreatorInput(creatorType);
    
            // Since we are adding something, we are sure that the list should now
            // have deletable rows.
            $("#" + creatorType + "-list .fa-minus-circle").removeClass("disabled");
    
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

    updateStatCounts();

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
    $("#queue-book").click(function(){
        if($("#proxy-form").valid()){
            var spine = renderSpine();
            internalizeBook(spine);
            window.visualQueue.enqueue(spine);
            window.visualQueueCount++;
            updateStatCounts();
            clearProxyForm();
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
        $("#" + creatorTitle + "-add").click(rendererFactory(creatorTitle));
        $("#" + creatorTitle + "-list .fa-minus-circle").click(recordDeleterFactory(creatorTitle));
    });
});
