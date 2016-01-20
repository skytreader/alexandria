module("Q Tests", {
    "setup":function(){
        var qContainer = document.createElement("div");
        this.q =  new VisualQueue(qContainer, null);
    }
});
test("simple count test", function(assert){
    var item1 = document.createElement("div");
    item1.id = "item1";
    this.q.enqueue(item1);
    equal(this.q.queueCounter, 1, "one item");
    this.q.remove(item1.id);
    equal(this.q.queueCounter, 0, "no more items");
});
