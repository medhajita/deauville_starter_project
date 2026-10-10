from festival.utils import create_slug

class Artist:
    def __init__(self, name, bio, photo_url):

        name = name.strip()

        if name == "":
            raise ValueError("Artist name cannot be empty.")

        self.name = name
        self.slug = create_slug(name)
        self.bio = bio
        self.photo_url = photo_url

"""artist = Artist(
    "  Élodie Marchal  ",
    "Stand-up about sport, failure and trying again.",
    ""
)

artist = Artist("   ", "", "")

print("Name :", artist.name)
print("Slug :", artist.slug)
print("Bio :", artist.bio)
print("URL :", artist.photo_url)"""
