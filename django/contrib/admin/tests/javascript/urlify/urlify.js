module("URLify Tests")

test("Testing the remove list", function() {
    var words = ["a", "an", "as", "at", "before", "but", "by", "for", "from",
                  "is", "in", "into", "like", "of", "off", "on", "onto", "per",
                  "since", "than", "the", "this", "that", "to", "up", "via",
                  "with"];
    equal(URLify("django " + words.join(" ") + " pony", 1000), "django-pony");
});

test("Removing unneeded characters", function() {
    equal(URLify("django!@#$%^&*()-pony1", 1000), "django-pony1");
});

test("Remove leading and trailing spaces", function() {
    equal(URLify("   django-pony   ", 1000), "django-pony");
});

test("Replace spaces with hyphens", function() {
    equal(URLify("django pony", 1000), "django-pony");
});

test("Converting uppercase to lowercase", function() {
    equal(URLify("DJANGO PONY", 1000), "django-pony");
});

test("truncating long strings", function() {
    equal(URLify("django pony", 6), "django");
})

test("Downcode, then URLify", function() {
    equal(URLify("ÿ", 1), "y");
    equal(URLify("©", 3), "c");
    equal(URLify("Ϋ", 1), "y");
    equal(URLify("ş", 1), "s");
    equal(URLify("Ğ", 1), "g");
    equal(URLify("Я", 2), "ya");
    equal(URLify("č", 1), "c");
    equal(URLify("ґ", 1), "g");
    equal(URLify("Ž", 1), "z");
})