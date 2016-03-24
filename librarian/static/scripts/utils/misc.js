/**
A collection of miscellaneous JavaScript functions that can be (potentially)
used anywhere.

@author Chad Estioco
*/

/**
Add a function like Python's capitalize to JavaScript strings.
*/
String.prototype.capitalize = function(){
    return this.charAt(0).toUpperCase() + this.slice(1);
}

/**
Add _every_ element in the given array to the set.

@param {Array} l - the list of items to add to the set.
*/
Set.prototype.addAll = function(l){
    var limit = l.length;
    for(var i = 0; i < limit; i++){
        this.add(l[i]);
    }
}
