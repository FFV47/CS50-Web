from re import search


def is_html(string):
    print(string, end=" - ")
    if search("<(\"[^\"]*\"|'[^']*'|[^'\">])*>", string):
        return True
    return False


# Driver code

html = "<h1>Hello World!</h1>"
print(is_html(html))

# Test Case 1:
str1 = "<input value = '>'>"
print(is_html(str1))

# Test Case 2:
str2 = "<br/>"
print(is_html(str2))

# Test Case 3:
str3 = "br/>"
print(is_html(str3))

# Test Case 4:
str4 = "<'br/>"
print(is_html(str4))
