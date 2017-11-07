/**
Javascript code related to the book details form.

@module types.bookDetails
@requires utils.isbnVerify
@requires alertify
@namespace types.bookDetails
@author Chad Estioco
*/

/**
Concerned with handling the book data in the proxy form.

@constructor
*/
function BookDetailsCtrl(){
    /**
    @member 
    @const
    @type Array.Person
    */
    this.BOOK_PERSONS = [];
    
    /**
    @member
    @const
    @type Array.String
    */
    this.BOOK_PERSONS_FIRSTNAME = [];

    /**
    @member
    @const
    @type Array.String
    */
    this.BOOK_PERSONS_LASTNAME = [];

    /**
    @member
    @const
    @type Set.Person
    */
    this.BOOK_PERSONS_SET = new Set();

    /**
    @member
    @const
    @type Array.String
    */
    this.COMPANIES = [];

    /**
    @member
    @const
    @type Array.String
    */
    this.GENRES = [];

    /**
    @member
    @const
    @type Array.String
    */
    this.CREATORS = ["author", "illustrator", "editor", "translator"]
    
    /**
    This is needed by the loadToForm method.
    
    Maps the creator type to the event handler used to add an entry to the
    creator list.

    @member
    */
    this.CREATOR_ADD_HANDLERS = {};

    this.setUp();
}

/**
TODO I thought of this method to automate my testing but I realized this could
also be useful for a "reprocess" feature. If saving a book fails, you can reload
the book's record into the form and redo what you think failed.
*/
BookDetailsCtrl.prototype.loadToForm = function(reqData){
    
    function insertAllCreators(me, all, type){
        if(all != null){
            for(var i = 0; i < all.length; i++){
                $("#" + type + "-proxy-firstname").val(all[i].firstname);
                $("#" + type + "-proxy-lastname").val(all[i].lastname);
                me.CREATOR_ADD_HANDLERS[type]();
            }
        }
    }

    $("#isbn-proxy").val(reqData.isbn);
    $("#title-proxy").val(reqData.title);
    $("#genre-proxy").val(reqData.genre);
    $("#publisher-proxy").val(reqData.publisher);
    $("#printer-proxy").val(reqData.printer);
    $("#year-proxy").val(reqData.year);
    insertAllCreators(this, reqData.author, "author");
    insertAllCreators(this, reqData.illustrator, "illustrator");
    insertAllCreators(this, reqData.editor, "editor");
    insertAllCreators(this, reqData.translator, "translator");
}

/**
@public
*/
BookDetailsCtrl.prototype.clearProxyForm = function(){
    alertify.confirm(
        "Are you sure you want to clear the form?",
        function() {
            $("#proxy-form input").val("");
            alertify.message("Form cleared.");
        },
        function() {
        }
    );
}

/**
@private
*/
BookDetailsCtrl.prototype.setUp = function(){
    var me = this;

    /**
    Create a list element for displaying a creator's name. The name displayed is
    dependent on what is currently entered in the procy fields for this creator.
    
    TODO Test me
    
    @param {string} creatorType
    */
    function renderContentCreatorListing(creatorType){
        var hiddenLastnameProxy = document.createElement("input");
        hiddenLastnameProxy.type = "hidden";
        hiddenLastnameProxy.name = creatorType + "-proxy-lastname";
    
        var hiddenFirstnameProxy = document.createElement("input");
        hiddenFirstnameProxy.type = "hidden";
        hiddenFirstnameProxy.name = creatorType + "-proxy-firstname";
    
        var divRow = document.createElement("div");
        $(divRow).addClass("row");
    
        var delCol = document.createElement("div");
        $(delCol).addClass("col-xs-1 del-col");
    
        var nameCol = document.createElement("div");
        $(nameCol).addClass("col-xs-11");
    
        divRow.appendChild(delCol);
        divRow.appendChild(nameCol);
    
        var lastName = $("#" + creatorType + "-proxy-lastname").val().trim();
        var firstName = $("#" + creatorType + "-proxy-firstname").val().trim();
        hiddenLastnameProxy.value = lastName;
        hiddenFirstnameProxy.value = firstName;
        clearCreatorInput(creatorType);
        var nameElement = document.createElement("span");
        nameElement.innerHTML = lastName + ", " + firstName;
    
        nameCol.appendChild(nameElement);
    
        var deleteButton = document.createElement("i");
        $(deleteButton).addClass("fa fa-times-circle")
          .click(recordDeleterFactory(creatorType));
    
        delCol.appendChild(deleteButton);
    
        var listing = document.createElement("li");
        listing.appendChild(divRow);
        listing.appendChild(hiddenLastnameProxy);
        listing.appendChild(hiddenFirstnameProxy);
    
        return listing;
    }

    /**
    @param {string} creatorType
    */
    function clearCreatorInput(creatorType){
        $("#" + creatorType + "-proxy-lastname").val("");
        $("#" + creatorType + "-proxy-firstname").val("");
    }

    /**
    @param {string} creatorType
    */
    function recordDeleterFactory(creatorType){
        return function() {
            $(this.parentNode.parentNode).remove();
        }
    };

    /**
    Return a function that generates an input row for a given creatorType. The
    generated function was meant to be called for the click event on the add
    button.
    */
    function rendererFactory(creatorType){
        return function(){
            var name = document.createElement("li");
            var inputLine = renderContentCreatorListing(creatorType);
    
            document.getElementById(creatorType + "-list").appendChild(inputLine);
        }
    }

    var me = this;
    // Event handlers
    $("#clear-proxy").click(function(){me.clearProxyForm()});
    // TODO rename the ID to something more generic for editing books.
    $("#queue-book").click(function(){me.saveBook()});

    this.fillGenres();
    this.fillCompanies();
    this.fillNames();
    this.addValidationMethods();

    $("#author-proxy-lastname").blur(function(){
        me.setAutoComplete("author-proxy-firstname", "author-proxy-lastname");
    });
    $("#author-proxy-firstname").blur(function(){
        me.setAutoComplete("author-proxy-lastname", "author-proxy-firstname");
    });
    $("#illustrator-proxy-lastname").blur(function(){
        me.setAutoComplete("illustrator-proxy-firstname", "illustrator-proxy-lastname");
    });
    $("#illustrator-proxy-firstname").blur(function(){
        me.setAutoComplete("illustrator-proxy-lastname", "illustrator-proxy-firstname");
    });
    $("#editor-proxy-lastname").blur(function(){
        me.setAutoComplete("editor-proxy-firstname", "editor-proxy-lastname");
    });
    $("#editor-proxy-firstname").blur(function(){
        me.setAutoComplete("editor-proxy-lastname", "editor-proxy-firstname");
    });
    $("#translator-proxy-lastname").blur(function(){
        me.setAutoComplete("translator-proxy-firstname", "translator-proxy-lastname");
    });
    $("#translator-proxy-firstname").blur(function(){
        me.setAutoComplete("translator-proxy-lastname", "translator-proxy-firstname");
    });

    this.CREATORS.forEach(function(creatorTitle){
        me.CREATOR_ADD_HANDLERS[creatorTitle] = rendererFactory(creatorTitle);
        $("#" + creatorTitle + "-add").click(me.CREATOR_ADD_HANDLERS[creatorTitle]);
        $("#" + creatorTitle + "-proxy-firstname")
          .keypress(function(e){
              if(e.keyCode == 13){
                  me.CREATOR_ADD_HANDLERS[creatorTitle]();
                  $("#" + creatorTitle + "-proxy-lastname").focus();
              }
          });
    });
}

/**
Initialize the autocomplete for names.

@private
*/
BookDetailsCtrl.prototype.fillNames = function(){
    var me = this;
    $.ajax("/api/read/persons", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            var allNames = data["data"];
            me.BOOK_PERSONS = allNames;
            me.BOOK_PERSONS_SET.addAll(allNames);
            var allLastnames = _.map(allNames, function(x){return x["lastname"]});
            var allFirstnames = _.map(allNames, function(x){return x["firstname"]});

            var lastnameSet = new Set(allLastnames);
            var firstnameSet = new Set(allFirstnames);

            me.BOOK_PERSONS_LASTNAME = [...lastnameSet];
            me.BOOK_PERSONS_FIRSTNAME = [...firstnameSet];

            $(".auto-lastname").autocomplete({
                source: me.BOOK_PERSONS_LASTNAME
            });

            $(".auto-firstname").autocomplete({
                source: me.BOOK_PERSONS_FIRSTNAME
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(me.fillNames, 8000);
        }
    });
}

/**
Event handler for clicking on the "Save Book" button.

@private
*/
BookDetailsCtrl.prototype.saveBook = function(){
    if(this.isCreatorPending()){
        alertify.alert("Forgot something?",
          "Did you forget to hit 'add' on a creator's name? Please add all creators first before proceeding.");
    } else if($("#proxy-form").valid()){
        this.validBookAction();
    } else{
        alertify.alert("Oh no!",
          "There is a problem with this book's details. Check the fields for specifics.");
    }
}

/**
Encapsulates what happens when the entered book data is valid.

@public
*/
BookDetailsCtrl.prototype.validBookAction = function(){
    console.error("BookDetailsCtrl.validBookAction must be implemented!");
    alert("BookDetailsCtrl.validBookAction must be implemented!");
}

/**
@private
*/
BookDetailsCtrl.prototype.fillGenres = function(){
    var me = this;
    $.ajax("/api/read/genres", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            me.GENRES = data["data"];
            $("#genre-proxy").autocomplete({
                source: me.GENRES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(me.fillGenres, 8000);
        }
    });
}

/**
@private
*/
BookDetailsCtrl.prototype.fillCompanies = function(){
    $.ajax("/api/read/companies", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            this.COMPANIES = data["data"]
            $("#publisher-proxy").autocomplete({
                source: this.COMPANIES
            });
            $("#printer-proxy").autocomplete({
                source: this.COMPANIES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(this.fillCompanies, 8000)
        }
    });
}

/**
Sets the autocomplete of the element with identifier `targetId` based on the
value held by the element with identifier `partnerId`.

This function expects certain elements from the page. In particular, this needs
that the elements described by `targetId` and `partnerId` also have the class
`auto-lastname` xor `auto-firstname`, depending on their actual purpose.

@param {string} targetId
@param {string} partnerId
@throws If the page where this method is used does not conform to the expected
stucture.
@public
*/
BookDetailsCtrl.prototype.setAutoComplete = function(targetId, partnerId){
    "use strict";
    var me = this;
    function mapAndSet(partner, target){
        var acSource = _.map(_.filter(me.BOOK_PERSONS, function(person){
            return person[partner] == partnerElement.val();
          }), function(person){
            return person[target];
          });

        if(acSource.length > 0){
            $("#" + targetId).autocomplete({
                source: acSource
            });
        }
    }

    var partnerElement = $("#" + partnerId);
    var acSource;

    if(partnerElement.hasClass("auto-lastname")){
        mapAndSet("lastname", "firstname");
    } else if(partnerElement.hasClass("auto-firstname")){
        mapAndSet("firstname", "lastname");
    } else{
        throw "Missing expected elements."
    }
}

/**
Reset all name autocomplete based on the BOOK_PERSONS field.

@public
*/
BookDetailsCtrl.prototype.resetAutocomplete = function(){
    "use strict";
    var firstnameSet = new Set(_.map(this.BOOK_PERSONS,
      function(x){return x["firstname"]}));
    var lastnameSet = new Set(_.map(this.BOOK_PERSONS,
      function(x){return x["lastname"]}));

    /*
    At this point we are sure that the autocomplete entries are unique.
    **However**, actual behavior shows that the firstnames are still repeated. :(
    */
    this.BOOK_PERSONS_FIRSTNAME = [...firstnameSet];
    this.BOOK_PERSONS_LASTNAME = [...lastnameSet];

    $(".auto-lastname").autocomplete({
        source: this.BOOK_PERSONS_LASTNAME
    });

    $(".auto-firstname").autocomplete({
        source: this.BOOK_PERSONS_FIRSTNAME
    });
}

/**
Clear all the user listings of their children li elements.

@public
*/
BookDetailsCtrl.prototype.clearLists = function(){
    for(var i = 0; i < this.CREATORS.length; i++){
        $("#" + this.CREATORS[i] + "-list").empty();
    }
}

/**
Checks the proxy textboxes for content creators that may not have been entered.

@public
*/
BookDetailsCtrl.prototype.isCreatorPending = function(){
    for(var i = 0; i < this.CREATORS.length; i++){
        if($("#" + this.CREATORS[i] + "-proxy-lastname").val() || $("#" + this.CREATORS[i] + "-proxy-firstname").val()){
            return true;
        }
    }
    return false;
}

/**
@private
*/
BookDetailsCtrl.prototype.addValidationMethods = function(){
    $.validator.addMethod("isbnVal", function(value, element, param){
        var stripped = value.trim();
        return verifyISBN10(stripped) || verifyISBN13(stripped);
    }, "Invalid ISBN input.");

    $.validator.addMethod("yearVal", function(value, element, param){
        return /^\d{4}$/.test(value);
    }, "Please enter a valid year.");

    $("#proxy-form").validate({
        rules:{
            "isbn-rule":{
                isbnVal: true,
                required: true,
                maxlength: 13
            },
            "year-rule":{
                yearVal: true,
                required: true
            },
            "genre-rule":{
                required: true,
                maxlength: 40
            },
            "title-rule":{
                required: true
            },
            "publisher-rule":{
                required: true
            }
        }
    });
}
