/**
Javascript code related to the book details form.
*/

/**
@const
*/
var BOOK_PERSONS = [];
/**
@const
@type Array.String
*/
var BOOK_PERSONS_LASTNAME = [];
/**
@const
@type Array.String
*/
var BOOK_PERSONS_FIRSTNAME = [];
var BOOK_PERSONS_SET = new Set();

var COMPANIES = [];
var GENRES = [];

function fillNames(){
    $.ajax("/api/read/persons", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            var allNames = data["data"];
            BOOK_PERSONS = allNames;
            BOOK_PERSONS_SET.addAll(allNames);
            var allLastnames = _.map(allNames, function(x){return x["lastname"]});
            var allFirstnames = _.map(allNames, function(x){return x["firstname"]});

            var lastnameSet = new Set(allLastnames);
            var firstnameSet = new Set(allFirstnames);

            BOOK_PERSONS_LASTNAME = [...lastnameSet];
            BOOK_PERSONS_FIRSTNAME = [...firstnameSet];

            $(".auto-lastname").autocomplete({
                source: window.BOOK_PERSONS_LASTNAME
            });

            $(".auto-firstname").autocomplete({
                source: window.BOOK_PERSONS_FIRSTNAME
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(window.fillNames, 8000);
        }
    });
}

/**
I am not sure if this is a good idea.
*/
function fillGenres(){
    $.ajax("/api/read/genres", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            window.GENRES = data["data"];
            $("#genre-proxy").autocomplete({
                source: window.GENRES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(window.fillGenres, 8000);
        }
    });
}

function fillCompanies(){
    $.ajax("/api/read/companies", {
        "type": "GET",
        "success": function(data, textStatus, jqXHR){
            window.COMPANIES = data["data"]
            $("#publisher-proxy").autocomplete({
                source: window.COMPANIES
            });
            $("#printer-proxy").autocomplete({
                source: window.COMPANIES
            });
        },
        "error": function(jqXHR, textStatus, error){
            setTimeout(window.fillCompanies, 8000)
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
*/
function setAutoComplete(targetId, partnerId){
    "use strict";
    function mapAndSet(partner, target){
        var acSource = _.map(_.filter(BOOK_PERSONS, function(person){
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
Reset all name autocomplete based on the BOOK_PERSONS global variable.
*/
function resetAutocomplete(){
    "use strict";
    window.BOOK_PERSONS_FIRSTNAME = _.map(window.BOOK_PERSONS,
      function(x){return x["firstname"]});
    window.BOOK_PERSONS_LASTNAME = _.map(window.BOOK_PERSONS,
      function(x){return x["lastname"]});

    $(".auto-lastname").autocomplete({
        source: window.BOOK_PERSONS_LASTNAME
    });

    $(".auto-firstname").autocomplete({
        source: window.BOOK_PERSONS_FIRSTNAME
    });
}

/**
Clear all the user listings of their children li elements.
*/
function clearLists(){
    for(var i = 0; i < CREATORS.length; i++){
        $("#" + CREATORS[i] + "-list").empty();
    }
}

/**
Checks the proxy textboxes for content creators that may not have been entered.
*/
function isCreatorPending(){
    for(var i = 0; i < CREATORS.length; i++){
        if($("#" + CREATORS[i] + "-proxy-lastname").val() || $("#" + CREATORS[i] + "-proxy-firstname").val()){
            return true;
        }
    }
    return false;
}

$.validator.addMethod("isbnVal", function(value, element, param){
    var stripped = value.trim();
    return verifyISBN10(stripped) || verifyISBN13(stripped);
}, "Invalid ISBN input.");

/*
Just check if it is a 4-digit number.
*/
$.validator.addMethod("yearVal", function(value, element, param){
    return /^\d{4}$/.test(value);
}, "Please enter a valid year.");

$(document).ready(function() {
    /**
    Return a function that generates an input row for a given creatorType. The
    generated function was meant to be called for the click event on the add button.
    */
    function rendererFactory(creatorType){
        return function(){
            var name = document.createElement("li");
            var inputLine = renderContentCreatorListing(creatorType);
    
            document.getElementById(creatorType + "-list").appendChild(inputLine);
        }
    }

    // Event handlers
    $("#clear-proxy").click(clearProxyForm);
    $("#queue-book").click(function(){
        if(isCreatorPending()){
            alertify.alert("Forgot something?",
              "Did you forget to hit 'add' on a creator's name? Please add all creators first before proceeding.");
        } else if($("#proxy-form").valid()){
            var spine = renderSpine();
            internalizeBook(spine);
            window.visualQueue.prepend(spine);
            updateStatCounts();
            clearProxyForm();
            clearLists();
            resetAutocomplete();
        } else{
            alertify.alert("Oh no!",
              "There is a problem with this book's details. Check the fields for specifics.");
        }
    });

    fillGenres();
    fillCompanies();
    fillNames();

    $("#author-proxy-lastname").blur(function(){
        setAutoComplete("author-proxy-firstname", "author-proxy-lastname");
    });
    $("#author-proxy-firstname").blur(function(){
        setAutoComplete("author-proxy-lastname", "author-proxy-firstname");
    });
    $("#illustrator-proxy-lastname").blur(function(){
        setAutoComplete("illustrator-proxy-firstname", "illustrator-proxy-lastname");
    });
    $("#illustrator-proxy-firstname").blur(function(){
        setAutoComplete("illustrator-proxy-lastname", "illustrator-proxy-firstname");
    });
    $("#editor-proxy-lastname").blur(function(){
        setAutoComplete("editor-proxy-firstname", "editor-proxy-lastname");
    });
    $("#editor-proxy-firstname").blur(function(){
        setAutoComplete("editor-proxy-lastname", "editor-proxy-firstname");
    });
    $("#translator-proxy-lastname").blur(function(){
        setAutoComplete("translator-proxy-firstname", "translator-proxy-lastname");
    });
    $("#translator-proxy-firstname").blur(function(){
        setAutoComplete("translator-proxy-lastname", "translator-proxy-firstname");
    });

    CREATORS.forEach(function(creatorTitle){
        CREATOR_ADD_HANDLERS[creatorTitle] = rendererFactory(creatorTitle);
        $("#" + creatorTitle + "-add").click(CREATOR_ADD_HANDLERS[creatorTitle]);
        $("#" + creatorTitle + "-proxy-firstname")
          .keypress(function(e){
              if(e.keyCode == 13){
                  CREATOR_ADD_HANDLERS[creatorTitle]();
                  $("#" + creatorTitle + "-proxy-lastname").focus();
              }
          });
    });
})
