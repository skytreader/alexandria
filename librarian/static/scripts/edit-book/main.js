/**
JS for editing a book. The module is similar to add books only in appearance.
This is considerably less complex since this will only edit a _single_ book at
any given time.

@module editBooks.main
@namespace editBooks.main
@author Chad Estioco
*/

/**
@constructor
*/
function EditBookDetailsCtrl(){
    BookDetailsCtrl.call(this);
}

EditBookDetailsCtrl.prototype = Object.create(BookDetailsCtrl.prototype);

EditBookDetailsCtrl.prototype.clearProxyForm = function(){
    // WARNING: This may not be very standard behavior. Observed in Chrome and
    // firefox Ubuntu.
    if (window.history.length > 1){
        window.history.back();
    } else{
        window.close();
    }
}

/**
Move the data in the proxy form to the actual form, reformatting them as necessary.

@private
*/
EditBookDetailsCtrl.prototype.moveFormData = function(){
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

    document.getElementById("isbn").value = isbn;
    document.getElementById("title").value = title;
    document.getElementById("genre").value = genre;
    document.getElementById("authors").value = authors;
    document.getElementById("illustrators").value = illustrators;
    document.getElementById("editors").value = editors;
    document.getElementById("translators").value = translators;
    document.getElementById("publisher").value = publisher;
    document.getElementById("printer").value = printer;
    document.getElementById("year").value = year;
}

/**
Get-things-done: This is a stripped-down version of the one in BookSenderCtrl.sendSaveForm.
*/
EditBookDetailsCtrl.prototype.validBookAction = function(){
    this.moveFormData();
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
    $.ajax("/api/edit/books", {
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
Assumes that the book to be edited is in a global variable `bookForEditing`.
*/
$(document).ready(function(){
    var editBookCtrl = new EditBookCtrl(bookForEditing, new EditBookDetailsCtrl());
});
