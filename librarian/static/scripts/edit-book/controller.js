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
