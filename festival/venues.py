from festival.utils import create_slug

class Venue :
    def __init__(self,name,capacity,address):

        name = name.strip()

        if name == "" :
            raise ValueError("Venue name cannot be empty")

        if capacity < 1 :
            raise ValueError("Capacity should be in the minimum 1")

        address = address.strip()

        self.name = name
        self.slug = create_slug(name)
        self.capacity = capacity
        self.address = address


"""venue = Venue(
    "  Théâtre des Planches  ",
    320,
    "  Town centre  "
)

venue = Venue("Le Kiosque", 0, "Beach promenade")

print(venue.name)
print(venue.slug)
print(venue.capacity)
print(venue.address)"""
