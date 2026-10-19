from datetime import datetime, date

from storage.json_storage import load_festival

from festival.errors import FestivalError

from cli.commands import (
    show_day_programme,
    show_artists,
    show_now_playing,
    show_up_next,
    show_now_and_next,
)


def display_menu():
    """
    Affiche le menu principal de l'application.
    """

    print("\n" + "=" * 50)
    print("         DEAUVILLE FESTIVAL DU RIRE 2027")
    print("=" * 50)

    print("1. Consulter le programme d'une journée")
    print("2. Afficher la liste des artistes")
    print("3. Afficher les spectacles en cours")
    print("4. Afficher les 3 prochaines performances")
    print("5. Afficher les spectacles en cours et à venir")
    print("0. Quitter")

    print("=" * 50)


def ask_day():
    """
    Demande une date au format YYYY-MM-DD.
    """

    day = input(
        "\nEntrez une date (YYYY-MM-DD) : "
    ).strip()

    try:
        date.fromisoformat(day)

        return day

    except ValueError:
        print("Erreur : format de date invalide.")
        print("Exemple : 2027-06-10")

        return None


def ask_moment():
    """
    Demande une date et une heure.
    """

    moment_input = input(
        "\nEntrez une date et une heure "
        "(YYYY-MM-DD HH:MM) : "
    ).strip()

    try:
        moment = datetime.fromisoformat(moment_input)

        if moment.tzinfo is not None:
            print("Erreur : ne précisez pas de fuseau horaire.")
            return None

        return moment

    except ValueError:
        print("Erreur : format de date ou d'heure invalide.")
        print("Exemple : 2027-06-10 20:30")

        return None


def main():
    """
    Fonction principale de la CLI.
    """

    print("\nChargement du festival...")

    try:
        festival = load_festival()

    except (FestivalError, ValueError, KeyError, TypeError) as error:
        print(f"Erreur de chargement : {error}")
        return

    print("Festival chargé avec succès !")

    print(f"\nBienvenue au {festival.name}")
    print(
        f"Du {festival.first_day} "
        f"au {festival.last_day}"
    )

    while True:

        display_menu()

        choice = input("\nVotre choix : ").strip()

        try:

            if choice == "1":

                day = ask_day()

                if day is not None:
                    show_day_programme(festival, day)

            elif choice == "2":

                show_artists(festival)

            elif choice == "3":

                moment = ask_moment()

                if moment is not None:
                    show_now_playing(festival, moment)

            elif choice == "4":

                moment = ask_moment()

                if moment is not None:
                    show_up_next(festival, moment)

            elif choice == "5":

                moment = ask_moment()

                if moment is not None:
                    show_now_and_next(festival, moment)

            elif choice == "0":

                print("\nMerci d'avoir utilisé notre application !")
                print("À bientôt au Festival du Rire !")

                break

            else:

                print("\nChoix invalide. Veuillez réessayer.")

        except FestivalError as error:

            print(f"\nErreur : {error}")


if __name__ == "__main__":

    try:
        main()

    except (KeyboardInterrupt, EOFError):
        print("\nApplication fermée.")