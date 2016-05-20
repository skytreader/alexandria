/**
Javascript code related to the book details form.
*/

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
