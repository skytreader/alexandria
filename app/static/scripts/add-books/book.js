/**
The book class.
*/

/**
FIXME Such a long arglist! Is there a pattern to prevent this?

All args are strings.
*/
function Book(isbn, title, genre, authors, illustrators, editors, translators,
  publisher, printer, year){
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
}
