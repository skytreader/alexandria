/**
@module editBooks.controller
@namespace editBooks.controller
@author Chad Estioco
*/

/**
@constructor
@param {addBooks.types} editBook
*/
function EditBookCtrl(editBook){
    this.editBook = editBook;
    this.initialize();
}

/**
@private
*/
EditBookCtrl.prototype.initialize = function(){
    $("#isbn-proxy").val(editBook.isbn);
    $("#title-proxy").val(editBook.title);
    $("#publisher-proxy").val(editBook.publisher);
    $("#printer-proxy").val(editBook.printer);
    $("#genre-proxy").val(editBook.genre);
    $("#year-proxy").val(editBook.year);
}
