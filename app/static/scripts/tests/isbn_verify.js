QUnit.test("stripExtraneousTest", function(assert){
    assert.equal(stripExtraneous("3.1  4 1 5 92-653"), "3141592653");
});
