/**
@module addBooks.addBookDetails
@namespace addBooks.addBookDetails
@inheritdoc types.bookDetails
@author Chad Estioco
*/

function AddBookDetailsCtrl(){
    BookDetailsCtrl.call(this)
}

AddBookDetailsCtrl.prototype = Object.create(BookDetailsCtrl.prototype);

AddBookDetailsCtrl.prototype.validBookAction = function(){
    var spine = this.renderSpine();
    this.internalizeBook(spine);
    window.visualQueue.prepend(spine);
    this.updateStatCounts();
    this.clearProxyForm();
    this.clearLists();
    this.resetAutocomplete();
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
    authorsText.innerHTML = this.listNames(getCreatorNames("author"));

    spine.appendChild(isbnText);
    spine.appendChild(titleText);
    spine.appendChild(authorsText);

    return spine;
}
