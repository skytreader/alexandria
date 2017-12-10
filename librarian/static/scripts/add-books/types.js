/**
Contains the types needed for adding books.

@module addBooks.types
*/

/**
FIXME Such a long arglist! Is there a pattern to prevent this?

All args are strings except for domElement which is the corresponding
visual representation of the Book in the DOM.

@constructor
@param {string} isbn
@param {string} title
@param {string} genre
@param {string} authors
@param {string} illustrators
@param {string} editors
@param {string} translators
@param {string} publisher
@param {string} printer
@param {string} year
@param {HTMLElement} domElement
*/
function Book(isbn, title, genre, authors, illustrators, editors, translators,
  publisher, printer, year, domElement){
    this.isbn = isbn;
    this.title = title;
    this.genre = genre;
    this.authors = authors;
    this.illustrators = illustrators;
    this.editors = editors;
    this.translators = translators;
    this.publisher = publisher;
    this.printer = printer;
    this.year = year;
    this.domElement = domElement;
}
