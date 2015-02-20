/**
Visual queue is a DOM object that visualizes a queue. Allows for the enqueueing
and removal of other dom objects.

Depends on jQuery.

@author Chad Estioco
*/

/**
Constructor for a visual queue.

@param domContainer
    The container for the queue in the DOM. Typically a span or a div element.
@param defs
    Default parameters object such as
        defaultDisplay - What to display when the queue is empty. Defaults to
          null.
        defautLocation - An existing node in the DOM that will hold the
          domContainer. Defaults to the document body.
*/
function VisualQueue(domContainer, defs){
    defs = defs ? defs : {};
    this.domContainer = domContainer;
    if(defs["defaultDisplay"]){
        this.domContainer.appendChild(defs["defaultDisplay"]);
    }
    this.superContainer = defs["defaultDisplay"] ? defs["defaultDisplay"] : document.body;
    this.queueCounter = 0;
}

/**
To facilitate the removal of objects, it is recommended that the domElement
enqueued have an id attribute.
*/
VisualQueue.prototype.enqueue = function(domElement){
    if(this.queueCounter == 0){
        // Remove the default display first, if any
        $(this.domContainer).empty();
    }
    $(this.domContainer).append(domElement);
    this.queueCounter++;
}

/**
Remove the specified element from the queue.

@param elementId
  The id of the DOM element to be removed, specified as a string.
*/
VisualQueue.prototype.remove = function(elementId){
    $(this.domContainer).remove("#" + elementId);
    this.queueCounter--;
}

/**
Render the queue to the defaultLocation specified in the constructor.
*/
VisualQueue.prototype.render = function(){
    $(this.superContainer).append(this.domContainer);
}
