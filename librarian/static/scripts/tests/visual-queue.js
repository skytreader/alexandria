QUnit.module("Q Tests", {
    "beforeEach":function(){
        var qContainer = document.createElement("div");
        this.q =  new VisualQueue(qContainer, null);
    }
});
QUnit.test("simple count test", function(assert){
    var item1 = document.createElement("div");
    item1.id = "item1";
    this.q.enqueue(item1);
    assert.equal(this.q.queueCounter, 1);
    this.q.remove(item1.id);
    assert.equal(this.q.queueCounter, 0);
});
