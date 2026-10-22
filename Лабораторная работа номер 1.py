import math

def calculate(text):
    text = text.replace(" ", "")
    pos = 0

    def number():
        nonlocal pos
        start = pos

        while pos < len(text) and (
            text[pos].isdigit() or text[pos] == "."
        ):
            pos += 1

        if start == pos:
            raise ValueError("Ошибка " + str(pos))

        try:
            return float(text[start:pos])
        except ValueError:
            raise ValueError("Неправильное число")

    def primary():
        nonlocal pos

        if pos >= len(text):
            raise ValueError("Ошибка")

        if text[pos] == "-":
            pos += 1
            return -primary()

        if text[pos] == "+":
            pos += 1
            return primary()

        if text.startswith("log(", pos):
            pos += 4
            value = expr()

            if pos >= len(text) or text[pos] != ")":
                raise ValueError("Не хватает закрывающей скобки")

            pos += 1

            if value <= 0:
                raise ValueError(
                    "Логарифм определён только для x > 0"
                )

            return math.log(value)

        if text[pos] == "(":
            pos += 1
            value = expr()

            if pos >= len(text) or text[pos] != ")":
                raise ValueError("Не хватает закрывающей скобки")

            pos += 1
            return value

        return number()

    def term():
        nonlocal pos
        value = primary()

        while pos < len(text) and text[pos] in "*/":
            op = text[pos]
            pos += 1
            right = primary()

            if op == "*":
                value = value * right
            else:
                if right == 0:
                    raise ValueError("Деление на ноль")
                value = value / right

        return value

    def arith_expr():
        nonlocal pos
        value = term()

        while pos < len(text) and text[pos] in "+-":
            op = text[pos]
            pos += 1
            right = term()

            if op == "+":
                value = value + right
            else:
                value = value - right

        return value

    def expr():
        nonlocal pos
        value = arith_expr()

        while text.startswith("and", pos):
            pos += 3
            right = arith_expr()
            value = bool(value) and bool(right)

        return value

    result = expr()

    if pos != len(text):
        raise ValueError("Лишний символ " + str(pos))

    return result


s = input("Введите выражение: ")

try:
    print(calculate(s))
except (ValueError, OverflowError) as e:
    print("Ошибка:", e)
