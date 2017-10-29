/**
@module addBooks.statCounter
@namespace addBooks.statCounter
@author Chad Estioco
*/

/**
StatCounter encapsulates the stats counts presented in the UI which are actually
just derived from other variables.

All parameters are functions which should return an integer representing the
count of the specified statistic.

@param unsavedUpdater
@param savedUpdater
@param errorUpdater
@param reprocessedUpdater
*/
function StatCounter(unsavedUpdater, savedUpdater, errorUpdater, reprocessedUpdater){
    this.unsavedUpdater = unsavedUpdater;
    this.savedUpdater = savedUpdater;
    this.errorUpdater = errorUpdater;
    this.reprocessedUpdater = reprocessedUpdater;
}

StatCounter.prototype.updateUnsaved = function(){
    $("#unsaved-count").text("" + this.unsavedUpdater());
}

StatCounter.prototype.updateSaved = function(){
    $("#saved-count").text("" + this.savedUpdater());
}

StatCounter.prototype.updateError = function(){
    $("#error-count").text("" + this.errorUpdater());
}

StatCounter.prototype.updateReprocessed = function(){
    $("#reprocessed-count").text("" + this.reprocessedUpdater());
}

StatCounter.prototype.updateAll = function(){
    this.updateUnsaved();
    this.updateSaved();
    this.updateError();
    this.updateReprocessed();
}
