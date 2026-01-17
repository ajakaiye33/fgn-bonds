"""Number to words conversion for Naira currency."""


def number_to_words(number: int | float) -> str:
    """
    Convert a number to its English word representation.

    Args:
        number: The number to convert.

    Returns:
        The number in words (e.g., "Fifty Million").
    """

    def get_number(n: str) -> str:
        units = [
            "",
            "One",
            "Two",
            "Three",
            "Four",
            "Five",
            "Six",
            "Seven",
            "Eight",
            "Nine",
        ]
        teens = [
            "Ten",
            "Eleven",
            "Twelve",
            "Thirteen",
            "Fourteen",
            "Fifteen",
            "Sixteen",
            "Seventeen",
            "Eighteen",
            "Nineteen",
        ]
        tens = [
            "",
            "",
            "Twenty",
            "Thirty",
            "Forty",
            "Fifty",
            "Sixty",
            "Seventy",
            "Eighty",
            "Ninety",
        ]

        if n == "0":
            return ""
        elif len(n) == 1:
            return units[int(n)]
        elif len(n) == 2:
            if n[0] == "1":
                return teens[int(n[1])]
            else:
                return tens[int(n[0])] + (
                    " " + units[int(n[1])] if int(n[1]) != 0 else ""
                )
        elif len(n) == 3:
            if n[0] == "0":
                return get_number(n[1:])
            else:
                return (
                    units[int(n[0])]
                    + " Hundred"
                    + (" and " + get_number(n[1:]) if int(n[1:]) != 0 else "")
                )
        return ""

    def get_groups(n: str) -> list[str]:
        groups = []
        if n == "0":
            return ["0"]
        while n:
            groups.append(n[-3:] if len(n) >= 3 else n)
            n = n[:-3]
        return groups[::-1]

    number_str = str(int(number))
    groups = get_groups(number_str)
    suffixes = ["", "Thousand", "Million", "Billion"]

    words = []
    for i, group in enumerate(groups):
        if int(group) != 0:
            words.append(get_number(group) + " " + suffixes[len(groups) - i - 1])

    return " ".join(words).strip()


def format_money_in_words(amount: float) -> str:
    """
    Convert a monetary amount to words in Naira and Kobo.

    Args:
        amount: The amount in Naira (e.g., 50000000.25).

    Returns:
        The amount in words (e.g., "Fifty Million Naira and Twenty-Five Kobo").
    """
    naira = int(amount)
    kobo = int(round((amount - naira) * 100))

    result = number_to_words(naira) + " Naira"
    if kobo > 0:
        result += " and " + number_to_words(kobo) + " Kobo"

    return result
