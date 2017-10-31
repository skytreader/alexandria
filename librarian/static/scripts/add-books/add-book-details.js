/**
@module addBooks.addBookDetails
@namespace addBooks.addBookDetails
@ineritdoc
@author Chad Estioco
*/

/**
@constructor
@param {utils.visualQueue} visualQueue
*/
function AddBookDetailsCtrl(visualQueue){
    BookDetailsCtrl.call(this)
    
    /**
    This is the internal representation of the book queue.

    TODO Make this all caps for standards! Or is this really supposed to be a
    constant?

    @const {Queue}
    @member
    */
    this.bookQueue = new Queue();
    this.visualQueue = visualQueue;
    this.statCounter = null;
}

AddBookDetailsCtrl.prototype = Object.create(BookDetailsCtrl.prototype);

AddBookDetailsCtrl.prototype.setStatCounter = function(statCounter){
    this.statCounter = statCounter;
}

AddBookDetailsCtrl.prototype.validBookAction = function(){
    var spine = this.renderSpine();
    this.internalizeBook(spine);
    this.visualQueue.prepend(spine);
    if(this.statCounter){
        this.statCounter.updateAll();
    }
    $("#proxy-form input").val("");
    this.clearLists();
    this.resetAutocomplete();
}

/**
Append the book described in #proxy-form to the internal queue.

The DOM element representing the book is a required parameter since we use it to
map the Book object to its visual representation.

@param {HTMLElement} spineDom
  The DOM element representing the book spine. This is just necessary for mapping,
  which in turn is necessary for the reprocess function.
@public
*/
AddBookDetailsCtrl.prototype.internalizeBook = function(spineDom){
    var allInputs = $("#proxy-form input");
    var isbn = $(allInputs).filter("#isbn-proxy").val();
    var title = $(allInputs).filter("#title-proxy").val();
    var genre = $(allInputs).filter("#genre-proxy").val();
    var authors = JSON.stringify(this.getCreatorNames("author"));
    var illustrators = JSON.stringify(this.getCreatorNames("illustrator"));
    var editors = JSON.stringify(this.getCreatorNames("editor"));
    var translators = JSON.stringify(this.getCreatorNames("translator"));
    var publisher = $(allInputs).filter("#publisher-proxy").val();
    var printer = $(allInputs).filter("#printer-proxy").val();
    var year = $(allInputs).filter("#year-proxy").val();

    var bookObj = new Book(isbn, title, genre, authors, illustrators, editors,
      translators, publisher, printer, year, spineDom);

    this.bookQueue.enqueue(bookObj);
}

/**
Renders the "spine" display of the book list. Takes data from the proxy form
directly.

@return {HTMLElement} A div element which displays like a spine of a book. The
div element has the isbn for its id.
@private
*/
AddBookDetailsCtrl.prototype.renderSpine = function(){
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
    authorsText.innerHTML = this.listNames(this.getCreatorNames("author"));

    spine.appendChild(isbnText);
    spine.appendChild(titleText);
    spine.appendChild(authorsText);

    return spine;
}

/**
Get a list of persons and return a string to display them..

@param {Array.Person} nameList
@return {string} the names listed, separated by semi-colons.
@private
*/
AddBookDetailsCtrl.prototype.listNames = function(nameList){
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

@param {string} creator
    The name given to the creator type.
@return {Array.Person} An array of persons.
@private
*/
AddBookDetailsCtrl.prototype.getCreatorNames = function(creator){
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
