/**
Javascript code related to the book details form.

@module types.bookDetails
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
TODO Mark this class as "abstract" and make subclasses implement this method.

@public
*/
BookDetailsCtrl.prototype.clearProxyForm = function(){
}

/**
@private
*/
BookDetailsCtrl.prototype.setUp = function(){
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

    // Event handlers
    $("#clear-proxy").click(this.clearProxyForm);
    $("#queue-book").click(function(){
        if(this.isCreatorPending()){
            alertify.alert("Forgot something?",
              "Did you forget to hit 'add' on a creator's name? Please add all creators first before proceeding.");
        } else if($("#proxy-form").valid()){
            var spine = renderSpine();
            this.internalizeBook(spine);
            window.visualQueue.prepend(spine);
            this.updateStatCounts();
            this.clearProxyForm();
            this.clearLists();
            this.resetAutocomplete();
        } else{
            alertify.alert("Oh no!",
              "There is a problem with this book's details. Check the fields for specifics.");
        }
    });

    this.fillGenres();
    this.fillCompanies();
    this.fillNames();

    $("#author-proxy-lastname").blur(function(){
        this.setAutoComplete("author-proxy-firstname", "author-proxy-lastname");
    });
    $("#author-proxy-firstname").blur(function(){
        this.setAutoComplete("author-proxy-lastname", "author-proxy-firstname");
    });
    $("#illustrator-proxy-lastname").blur(function(){
        this.setAutoComplete("illustrator-proxy-firstname", "illustrator-proxy-lastname");
    });
    $("#illustrator-proxy-firstname").blur(function(){
        this.setAutoComplete("illustrator-proxy-lastname", "illustrator-proxy-firstname");
    });
    $("#editor-proxy-lastname").blur(function(){
        this.setAutoComplete("editor-proxy-firstname", "editor-proxy-lastname");
    });
    $("#editor-proxy-firstname").blur(function(){
        this.setAutoComplete("editor-proxy-lastname", "editor-proxy-firstname");
    });
    $("#translator-proxy-lastname").blur(function(){
        this.setAutoComplete("translator-proxy-firstname", "translator-proxy-lastname");
    });
    $("#translator-proxy-firstname").blur(function(){
        this.setAutoComplete("translator-proxy-lastname", "translator-proxy-firstname");
    });

    var me = this;
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
            BOOK_PERSONS = allNames;
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
@private
*/
BookDetailsCtrl.prototype.fillGenres = function(){
    $.ajax("/api/read/genres", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            window.GENRES = data["data"];
            $("#genre-proxy").autocomplete({
                source: this.GENRES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(this.fillGenres, 8000);
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
    function mapAndSet(partner, target){
        var acSource = _.map(_.filter(this.BOOK_PERSONS, function(person){
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
    this.BOOK_PERSONS_FIRSTNAME = _.map(this.BOOK_PERSONS,
      function(x){return x["firstname"]});
    this.BOOK_PERSONS_LASTNAME = _.map(this.BOOK_PERSONS,
      function(x){return x["lastname"]});

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

$(document).ready(function() {
    var bookDetailsCtrl = new BookDetailsCtrl();
})
