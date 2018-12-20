/**
This class is concerned with the interaction of the proxy form and the actual
form via queues. Sending the data to the server is also part of its
responsibilites.

@module addBooks.main
@namespace addBooks.main
@author Chad Estioco
*/

/**
@constructor
@param {addBooks.addBookDetails.AddBookDetailsCtrl} bookDetailsCtrl
    Expected to be initialized and all.
*/
function BookSenderCtrl(bookDetailsCtrl){
    this.bookDetailsCtrl = bookDetailsCtrl;
    /**
    The interval of time, in milliseconds, in which we process books.

    @const {number}
    @member
    */
    this.PROCESS_INTERVAL = 8888;

    /**
    The interval of time, in milliseconds, in which we reprocess books that
    failed and in reprocessable.

    @const {number}
    @member
    */
    this.REPROCESS_INTERVAL = this.PROCESS_INTERVAL + 1000;
    
    /**
    Where the books eligible for reprocessing go.

    TODO Make this all caps for standards! Or is this really supposed to be a
    constant?

    @const {Queue}
    @member
    */
    this.reprocessQueue = new Queue();
    
    /**
    This script will manipulate ids a lot. We derive certain converntions from the
    actual ids of the hidden form field. This hidden form field is the one that
    is mapped to the Flask form. These are the fields to be included in the request.

    TODO Make this all caps for standards!

    @const {Array.String}
    @member
    */
    this.realFormIds = ["isbn", "title", "genre", "authors", "illustrators",
      "editors", "translators", "year", "publisher", "printer"];
    
    /**
    @member
    */
    this.booksSaved = 0;
    /**
    @member
    */
    this.booksErrorNoRetry = 0;
    /**
    @member
    */
    this.booksReprocessable = 0;

    var me = this;
    this.statCounter = new StatCounter(() => me.unsavedUpdater(),
        () => me.savedUpdater(), () => me.errorUpdater(),
        () => me.reprocessUpdater());
    this.bookDetailsCtrl.setStatCounter(this.statCounter);
}

BookSenderCtrl.prototype.unsavedUpdater = function(){
    return this.bookDetailsCtrl.visualQueue.getLength();
}

BookSenderCtrl.prototype.savedUpdater = function(){
    return this.booksSaved;
}

BookSenderCtrl.prototype.errorUpdater = function(){
    return this.booksErrorNoRetry;
}

BookSenderCtrl.prototype.reprocessUpdater = function(){
    return this.booksReprocessable;
}

/**
@public
*/
BookSenderCtrl.prototype.updateStatCounts = function(){
    $("#unsaved-count").text("" + this.bookDetailsCtrl.visualQueue.getLength());
    $("#saved-count").text("" + this.booksSaved);
    $("#error-count").text("" + this.booksErrorNoRetry);
    $("#reprocessed-count").text("" + this.booksReprocessable);
}

/**
Generates the delete button to be added at the end of every row record.

@return {HTMLElement}
@private
*/
BookSenderCtrl.prototype.renderDeleteButton = function(){
    var container = document.createElement("input");
    container.onclick = removeRow;
    container.type = "button";
    container.className = "btn infrequent";
    container.value = "X";
    
    return container;
}

/**
Send the actual, hidden form to the server via AJAX so that the data may be
saved.

@param {HTMLElement} domElement - the book spine representing the book to be
  sent, as a DOM element.
*/
BookSenderCtrl.prototype.sendSaveForm = function(domElement){
    var authors = JSON.parse(document.getElementById("authors").value);
    var illustrators = JSON.parse(document.getElementById("illustrators").value);
    var editors = JSON.parse(document.getElementById("editors").value);
    var translators = JSON.parse(document.getElementById("translators").value);
    var possibleNewNames = [authors, illustrators, editors, translators];

    var publisher = document.getElementById("publisher").value;
    var printer = document.getElementById("printer").value;
    var possibleNewCompanies = [publisher, printer];

    var possibleNewGenre = document.getElementById("genre").value;
    var me = this;

    function success(){
        $(domElement).removeClass("unsaved_book").addClass("saved_book");

        _.forEach(possibleNewNames, function(newNames){
            _.forEach(newNames, function(person){
                if(!me.bookDetailsCtrl.BOOK_PERSONS_SET.has(person)){
                    me.bookDetailsCtrl.BOOK_PERSONS_SET.add(person);
                    if(me.bookDetailsCtrl.BOOK_PERSONS_FIRSTNAME.indexOf(person["firstname"]) < 0){
                        me.bookDetailsCtrl.BOOK_PERSONS_FIRSTNAME.push(person["firstname"]);
                    }
                    if(me.bookDetailsCtrl.BOOK_PERSONS_LASTNAME.indexOf(person["lastname"]) < 0){
                        me.bookDetailsCtrl.BOOK_PERSONS_LASTNAME.push(person["lastname"]);
                    }
                }
            });
        });
        me.bookDetailsCtrl.BOOK_PERSONS = [...me.bookDetailsCtrl.BOOK_PERSONS_SET]
        me.bookDetailsCtrl.resetAutocomplete();

        _.forEach(possibleNewCompanies, function(company){
            if(me.bookDetailsCtrl.COMPANIES.indexOf(company) < 0){
                me.bookDetailsCtrl.COMPANIES.push(company);
            }
        });

        _.forEach(possibleNewGenre, function(genre){
            if(me.bookDetailsCtrl.GENRES.indexOf(genre) < 0){
                me.bookDetailsCtrl.GENRES.push(genre);
            }
        });
        me.booksSaved++;
    }

    function fail(jqxhr){
        alertify.error(jqxhr.responseText);
        $(domElement).removeClass("unsaved_book").addClass("error_book");
        me.booksErrorNoRetry++;
    }

    function failRecover(jqxhr){
        alertify.warning("Failed to save a book. Please wait as we automatically retry.");
        $(domElement).removeClass("unsaved_book").addClass("reprocess_book");
        me.reprocessQueue.enqueue(domElement);
        me.booksReprocessable++;
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
    $.ajax("/api/add/books", {
        "type": "POST",
        "data": data,
        "success": success,
        "statusCode":{
            400: fail,
            409: fail,
            500: failRecover
        },
        "complete": function(){me.updateStatCounts()}
    });
}

/**
@param {string} creatorType
*/
function clearCreatorInput(creatorType){
    $("#" + creatorType + "-proxy-lastname").val("");
    $("#" + creatorType + "-proxy-firstname").val("");
}

/**
@param {string} creatorType
*/
function recordDeleterFactory(creatorType){
    return function() {
        $(this.parentNode.parentNode).remove();
    }
};

/**
@return {boolean} Returns true if the proxy form is all blank and if there is
nothing left in both queues.
*/
BookSenderCtrl.prototype.isWorkDone = function(){
    // TODO Check the condition where there is a _pending_ HTTP request. Should
    // this even handle that?
    function isProxyFormEmpty(){
        var proxyInputs = $("#proxy-form input");
        var isEmpty = true;
        _.forEach(proxyInputs, function(input){
            isEmpty = _.isEmpty(input.value);
            return isEmpty;
        });
        return isEmpty;
    }
    return this.bookDetailsCtrl.bookQueue.getLength() == 0 && this.reprocessQueue.getLength() == 0 &&
      isProxyFormEmpty();
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
TODO Move everything above elsewhere (maybe book-submit-queue.js?) so that
main.js will only contain this $(document).ready.
*/
$(document).ready(function(){
    /**
    Clear the actual form.
    
    It is important to clear the actual form after every send to server. Else,
    we might get mixed data! (Consider the scenario where a record with an
    illustrator follows a record with no illustrator.)
    */
    function clearActualForm(){
        $("#main-form input").not("#csrf_token").val("");
    }

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
    var visualQueue = new VisualQueue(qContainer, defs);
    visualQueue.render();

    var addBookDetailsCtrl = new AddBookDetailsCtrl(visualQueue);
    var bookSenderCtrl = new BookSenderCtrl(addBookDetailsCtrl);

    $(window).bind("beforeunload", function(){
        if(!bookSenderCtrl.isWorkDone()){
            return "You are leaving the page with unsaved work.";
        }
    });

    /**
    Load from the given queue to the actual form. The queue object is expected to 
    be from Queue.js.
    
    @param queue
        The queue object from which we fetch a book.
    @return
        The dequeued record if a book record was loaded successfuly into the
        actual form, false otherwise.
    */
    function loadFromQueueToForm(queue){
        clearActualForm();
        var fromQ = queue.dequeue();
    
        if(fromQ){
            var limit = bookSenderCtrl.realFormIds.length;
    
            for(var i = 0; i < limit; i++){
                document.getElementById(bookSenderCtrl.realFormIds[i]).value = fromQ[bookSenderCtrl.realFormIds[i]];
            }
    
            return fromQ;
        }
    
        return false;
    }

    // Start the polling interval timers.
    setInterval(function(){
        var foo = loadFromQueueToForm(addBookDetailsCtrl.bookQueue);
        if(foo){
            bookSenderCtrl.sendSaveForm(foo.domElement);
        }
    }, bookSenderCtrl.PROCESS_INTERVAL);
    
    setInterval(function(){
        var foo = loadFromQueueToForm(bookSenderCtrl.reprocessQueue);
        if(foo){
            bookSenderCtrl.sendSaveForm(foo.domElement);
        }
    }, bookSenderCtrl.REPROCESS_INTERVAL);
});
