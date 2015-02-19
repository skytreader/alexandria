QUnit.test("stripExtraneousTest", function(assert){
    assert.equal(stripExtraneous("3.1  4 1 5 92-653"), "3141592653");
});

QUnit.test("isbn13Test", function(assert){
    assert.ok(verifyISBN13("9780981467306"), "Positive test");
    assert.ok(!verifyISBN13("0156453800"), "Negative test, wrong length");
    assert.ok(!verifyISBN13("3141592653589"), "Negative test, ok length");
});

QUnit.test("isbn10Test", function(assert){
    assert.ok(verifyISBN10("0156453800"));
    assert.ok(verifyISBN10("1553650808"));
    assert.ok(!verifyISBN10("9780981467306"), "Negative test, wrong length");
    assert.ok(!verifyISBN10("3141592653"), "Negative test, ok length");
});
