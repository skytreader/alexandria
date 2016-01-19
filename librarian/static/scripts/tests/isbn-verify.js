test("stripExtraneousTest", function(assert){
    equals(stripExtraneous("3.1  4 1 5 92-653"), "3141592653", "test");
});

test("isbn13Test", function(assert){
    ok(verifyISBN13("9780981467306"), "Positive test");
    ok(!verifyISBN13("0156453800"), "Negative test, wrong length");
    ok(!verifyISBN13("3141592653589"), "Negative test, ok length");
});

test("isbn10Test", function(assert){
    ok(verifyISBN10("0156453800"));
    ok(verifyISBN10("1553650808"));
    ok(verifyISBN10("156389016X"), "Positive test, with X checksum");
    ok(!verifyISBN10("9780981467306"), "Negative test, wrong length");
    ok(!verifyISBN10("3141592653"), "Negative test, ok length");
});
