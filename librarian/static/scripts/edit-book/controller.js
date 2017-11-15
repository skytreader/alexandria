/**
@module editBooks.controller
@namespace editBooks.controller
@author Chad Estioco
*/

/**
@constructor
@param {addBooks.types} editBook
@param {types.bookDetails.BookDetailsCtrl} bookDetailsCtrl
*/
function EditBookCtrl(editBook, bookDetailsCtrl){
    this.editBook = editBook;
    this.bookDetailsCtrl = bookDetailsCtrl;
    this.initialize();
}

/**
@private
*/
EditBookCtrl.prototype.initialize = function(){
    this.bookDetailsCtrl.loadToForm(this.editBook);
}

/**
Get-things-done: This is a stripped-down version of the one in BookSenderCtrl.sendSaveForm.
*/
EditBookCtrl.prototype.validBookAction = function(){
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
        // Maybe redirect to a search page for the isbn
        alertify.success("Updated book record successfully.");
        window.location.replace("/search?q=" + document.getElementById("isbn").value);
    }

    function fail(jqxhr){
        alertify.error(jqxhr.responseText);
    }

    function failRecover(jqxhr){
        alertify.warning("Failed to save a book. You may retry but if issues persist, check server logs.");
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
