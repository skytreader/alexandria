Some project-specific conventions:

- **Use of plural/singular in contributor label nouns.** When _creating_ objects
that refer to contributors in the _backend_, always use **singular** nouns. The
created object, however, may _store_ them in fields that use the **plural** form
since it may be used in the _frontend_ and frontend should always refer to it in
the plural form.
