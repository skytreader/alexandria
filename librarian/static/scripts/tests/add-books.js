test("content creator render test", function(assert){
    var renderedNameField = renderNameInput("developer", "lastname");
    equal(renderedNameField.className, "form-control");
    equal(renderedNameField.type, "text");
    equal(renderedNameField.name, "developer-proxy-lastname");
    equal(renderedNameField.placeholder, "Lastname");

    var developerInput = renderContentCreatorInput("developer");
    var nameInputs = $(developerInput).find(".form-control");
    var delButton = $(developerInput).find(".fa-minus-circle");
    
    // There should be at least two items with a class of form-control
    ok(nameInputs.length >= 2);
    ok(delButton.length == 1);
});

test("realFormIds is populated", function(assert){
    console.log("B");
    ok(window.realFormIds.length > 0);
});
