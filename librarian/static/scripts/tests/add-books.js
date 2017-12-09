test("realFormIds is populated", function(assert){
    var visuaQueue = new VisualQueue(document.createElement("div"), null);

    var addBookDetailsCtrl = new AddBookDetailsCtrl(visualQueue);
    var bookSenderCtrl = new BookSenderCtrl(addBookDetailsCtrl);
    ok(bookSenderCtrl.realFormIds.length > 0);
});
