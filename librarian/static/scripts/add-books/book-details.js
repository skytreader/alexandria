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
            console.log("Setting", targetId, "to ac", acSource);
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
