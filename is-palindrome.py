def is_palindrome(s: str) -> bool:
    # Приводим к нижнему регистру и убираем пробелы/знаки препинания
    cleaned = ''.join(ch.lower() for ch in s if ch.isalnum())
    # Сравниваем с обратной версией
    return cleaned == cleaned[::-1]

# Примеры использования
if __name__ == "__main__":
	
    str0 = "А роза упала на лапу Азора"
    str1 = "12321"
    str2 = "Hello"

    print(str0, is_palindrome(str0)) # True
    print(str1, is_palindrome(str1)) # True
    print(str2, is_palindrome(str2)) # False