
def display_performance(festival, performance):


    venue = festival.get_venue_by_slug(performance.venue)

    start = performance.start.strftime("%d/%m/%Y %H:%M")
    end = performance.end.strftime("%H:%M")

    print(f"\n{start} - {end}")
    print(f"Spectacle : {performance.title}")
    print(f"Salle     : {venue.name}")
    print(f"Type      : {performance.kind}")
    print("-" * 45)


def show_day_programme(festival, day):

    performances = festival.get_programme_by_day(day)

    print("\n" + "=" * 45)
    print(f"PROGRAMME DU {day}")
    print("=" * 45)

    if not performances:
        print("Aucun spectacle prévu pour cette journée.")
        return

    for performance in performances:
        display_performance(festival, performance)


def show_artists(festival):

    artists = festival.get_artists_sorted()

    print("\n" + "=" * 45)
    print("LISTE DES ARTISTES")
    print("=" * 45)

    if not artists:
        print("Aucun artiste disponible.")
        return

    for artist in artists:

        count = festival.get_artist_show_count(artist.slug)

        print(f"\nArtiste : {artist.name}")
        print(f"Slug    : {artist.slug}")
        print(f"Shows   : {count}")
        print("-" * 45)


def show_now_playing(festival, moment):

    performances = festival.get_now_playing(moment)

    print("\n" + "=" * 45)
    print("SPECTACLES EN COURS")
    print("=" * 45)

    print(f"Date : {moment.strftime('%d/%m/%Y %H:%M')}")

    if not performances:
        print("\nAucun spectacle en cours.")
        return

    for performance in performances:
        display_performance(festival, performance)


def show_up_next(festival, moment):

    performances = festival.get_up_next(moment)

    print("\n" + "=" * 45)
    print("LES 3 PROCHAINES PERFORMANCES")
    print("=" * 45)

    if not performances:
        print("Aucune performance à venir.")
        return

    for performance in performances:
        display_performance(festival, performance)


def show_now_and_next(festival, moment):

    show_now_playing(festival, moment)

    show_up_next(festival, moment)