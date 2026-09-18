import re

def regex_check(word):
    pattern = r"^(abc)*d(e)*$"
    return re.fullmatch(pattern, word) is not None


word = input("Введите слово: ")

if regex_check(word):
    print("Слово принадлежит языку.")
else:
    print("Слово не принадлежит языку.")