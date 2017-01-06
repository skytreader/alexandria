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
    console.log("the edit book is", this.editBook);
    this.bookDetailsCtrl.loadToForm(this.editBook);
    //$("#isbn-proxy").val(this.editBook.isbn);
    //$("#title-proxy").val(this.editBook.title);
    //$("#publisher-proxy").val(this.editBook.publisher);
    //$("#printer-proxy").val(this.editBook.printer);
    //$("#genre-proxy").val(this.editBook.genre);
    //$("#year-proxy").val(this.editBook.year);
}
