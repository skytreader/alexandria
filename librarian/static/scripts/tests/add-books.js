test("content creator render test", function(assert){
    var renderedNameField = renderNameInput("developer", "lastname");
    equals(renderedNameField.className, "form-control");
    equals(renderedNameField.type, "text");
    equals(renderedNameField.name, "developer-proxy-lastname");

    var developerInput = renderContentCreatorInput("developer");
    var nameInputs = $(developerInput).find(".form-control");
    
    // There should be at least two items with a class of form-control
    ok(nameInputs.length >= 2);
});
