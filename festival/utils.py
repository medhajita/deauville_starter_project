import re
import unicodedata

name = "  Élodie Marchal !  @ "


def create_slug(name):

    find_no_alpha = re.findall(r"[^\w\s]", name)
    del_no_alpha = re.sub(r"[^\w\s]", "", name)

    #print(f"The no Alpha we found : {find_no_alpha}")
    #print(f"The result after delete the no Alpha : {del_no_alpha}")

    normalized = unicodedata.normalize("NFD", del_no_alpha)

    no_accents = "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )

    #print(f"The name without accents : {no_accents}")

    no_accents = no_accents.strip()
    no_accents = re.sub(r"\s+", "-", no_accents)
    no_accents = no_accents.lower()

    #print(no_accents)

    return no_accents


"""slug = create_slug(name)
print(slug)"""