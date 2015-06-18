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
