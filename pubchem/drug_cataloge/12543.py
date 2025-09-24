def get_clean_name_advanced(full_name):
    """
    Removes content after a comma only if the comma is outside of all parentheses
    and is not between two digits.
    """
    if not isinstance(full_name, str):
        return full_name

    paren_count = 0

    for i in range(len(full_name)):
        char = full_name[i]

        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1

        if char == ',':
            # Check if the comma is outside of all parentheses
            if paren_count == 0:
                # Look at the characters on either side of the comma
                # Ensure we're not at the beginning or end of the string
                is_between_digits = False
                if i > 0 and i < len(full_name) - 1:
                    # Check if the characters are digits
                    if full_name[i-1].isdigit() and full_name[i+1].isdigit():
                        is_between_digits = True

                # If the comma is NOT between two digits, then we've found our separator
                if not is_between_digits:
                    return full_name[:i].strip()

    # If no valid separator comma is found, return the original string
    return full_name.strip()

input1 = "Etodolac, (+-)-Isomer"
input2 = "5-((1,8-diethyl-1,3,4,9-tetrahydropyrano(3,4-b)indole-1-yl)methyl)-4-methyl-2,4-dihydro-3H-1,2,4-triazole-3-thione"
input3 = "Etodolac,(1,2+-)-Isomer,555"
print(get_clean_name_advanced(input3))
