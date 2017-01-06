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
    $("#isbn-proxy").val(this.editBook.isbn);
    $("#title-proxy").val(this.editBook.title);
    $("#publisher-proxy").val(this.editBook.publisher);
    $("#printer-proxy").val(this.editBook.printer);
    $("#genre-proxy").val(this.editBook.genre);
    $("#year-proxy").val(this.editBook.year);
}
