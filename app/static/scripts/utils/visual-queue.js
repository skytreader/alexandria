/**
Visual queue is a DOM object that visualizes a queue. Allows for the enqueueing
and removal of other dom objects.

Depends on jQuery.

@author Chad Estioco
*/

function VisualQueue(domContainer, defaultDisplay){
    this.domContainer = domContainer;
    this.domContainer.appendChild(defaultDisplay);
    this.queueCounter = 0;
}

/**
To facilitate the removal of objects, it is recommended that the domElement
enqueued have an id attribute.
*/
VisualQueue.prototype.enqueue = function(domElement){
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
