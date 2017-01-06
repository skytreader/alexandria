/**
JS for editing a book. The module is similar to add books only in appearance.
This is considerably less complex since this will only edit a _single_ book at
any given time.

@module editBooks.main
@namespace editBooks.main
@author Chad Estioco
*/

/**
Assumes that the book to be edited is in a global variable `bookForEditing`.
*/
$(document).ready(function(){
    var editBookCtrl = new EditBookCtrl(bookForEditing, new BookDetailsCtrl());
});
