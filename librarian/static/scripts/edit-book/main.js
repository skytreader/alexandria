/**
JS for editing a book. The module is similar to add books only in appearance.
This is considerably less complex since this will only edit a _single_ book at
any given time.

@module editBooks.main
@namespace editBooks.main
@author Chad Estioco
*/

/**
Assumes that the book to be edited is in a global variable `editBook`.
*/
$(document).ready(function(){
    $("#isbn-proxy").val(editBook.isbn);
    $("#title-proxy").val(editBook.title);
    $("#publisher-proxy").val(editBook.publisher);
    $("#printer-proxy").val(editBook.printer);
    $("#genre-proxy").val(editBook.genre);
});
