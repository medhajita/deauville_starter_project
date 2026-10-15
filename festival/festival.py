from datetime import datetime, timedelta
from festival.performances import (
    SoloPerformance,
    LineupPerformance,
    WorkshopPerformance,
)
from festival.errors import FestivalError, ValidationError,  NotFoundError, ConflictError

class Festival :
    def __init__(self,name,first_day,last_day,venues,artists,performances):

        name = name.strip()

        if name == "" :
            raise ValidationError("The name shouldn't be empty")

        self.name = name
        self.first_day = first_day
        self.last_day = last_day
        self.venues = venues
        self.artists = artists
        self.performances = performances

    def get_artist_by_slug(self, slug):
        for artist in self.artists:
            if artist.slug == slug:
                return artist

        raise NotFoundError("Artist not Found")

    def get_venue_by_slug(self, slug):
        for venue in self.venues:
            if venue.slug == slug:
                return venue

        raise NotFoundError("Venue not Found")

    # check after :

    def check_festival_day(self, performance):

        festival_day = datetime.fromisoformat(performance.festival_day)
        first_day = datetime.fromisoformat(self.first_day)
        last_day = datetime.fromisoformat(self.last_day)

        if festival_day < first_day:
            raise ConflictError("Performance is before the festival.")

        if festival_day > last_day:
            raise ConflictError("Performance is after the festival.")

    def check_performance_venue(self, performance):
        venue_slug = performance.venue
        return self.get_venue_by_slug(venue_slug)

    def check_performance_artists(self, performance):

        if isinstance(performance, SoloPerformance):
            self.get_artist_by_slug(performance.artist)

        elif isinstance(performance, LineupPerformance):
            self.get_artist_by_slug(performance.host)

            for act in performance.acts:
                self.get_artist_by_slug(act)

        elif isinstance(performance, WorkshopPerformance):
            self.get_artist_by_slug(performance.teacher)

    def check_venue_conflict(self, performance):

        for existing_performance in self.performances:

            if existing_performance is performance:
                continue

            if existing_performance.venue != performance.venue:
                continue

            gap_after_existing = existing_performance.end + timedelta(minutes=30)
            gap_after_new = performance.end + timedelta(minutes=30)

            if not (
                    performance.start >= gap_after_existing
                    or existing_performance.start >= gap_after_new
            ):
                raise ConflictError(
                    f"{performance.venue} is busy with "
                    f"{existing_performance.title}. "
                    f"Leave 30 minutes between two shows."
                )

    def get_performance_artists(self, performance):

        if isinstance(performance, SoloPerformance):
            return [performance.artist]

        elif isinstance(performance, LineupPerformance):
            return [performance.host] + performance.acts

        elif isinstance(performance, WorkshopPerformance):
            return [performance.teacher]

        return []

    def check_artist_conflict(self, performance):

        new_artists = self.get_performance_artists(performance)

        for existing_performance in self.performances:

            if existing_performance is performance:
                continue

            existing_artists = self.get_performance_artists(existing_performance)

            common_artists = set(new_artists) & set(existing_artists)

            if not common_artists:
                continue

            gap_after_existing = existing_performance.end + timedelta(minutes=30)
            gap_after_new = performance.end + timedelta(minutes=30)

            if not (
                    performance.start >= gap_after_existing
                    or existing_performance.start >= gap_after_new
            ):
                raise ConflictError(
                    "An artist needs 30 minutes between two performances."
                )

    def add_performance(self, performance):

        for existing_performance in self.performances:
            if existing_performance.id == performance.id:
                raise ConflictError("Performance already exists.")

        self.check_festival_day(performance)

        self.check_performance_venue(performance)

        self.check_performance_artists(performance)

        self.check_venue_conflict(performance)

        self.check_artist_conflict(performance)

        self.performances.append(performance)

    def add_artist(self, artist):
        for existing_artist in self.artists:
            if existing_artist.slug == artist.slug:
                raise ConflictError("Artist already exists.")

        self.artists.append(artist)

    def add_venue(self, venue):
        for existing_venue in self.venues:
            if existing_venue.slug == venue.slug:
                raise ConflictError("Venue already exists.")

        self.venues.append(venue)

    def get_performance_by_id(self, performance_id):
        for performance in self.performances:
            if performance.id == performance_id:
                return performance

        raise NotFoundError("Performance not found.")

    def get_performance_capacity(self, performance):

        venue = self.get_venue_by_slug(performance.venue)

        if isinstance(performance, SoloPerformance):
            return venue.capacity

        elif isinstance(performance, LineupPerformance):
            return venue.capacity

        elif isinstance(performance, WorkshopPerformance):
            return min(performance.max_participants, venue.capacity)

    def add_participant(self, performance_id, name):
        performance = self.get_performance_by_id(performance_id)

        if not isinstance(performance, WorkshopPerformance):
            raise ValidationError("This performance is not a workshop.")

        name = name.strip()

        if name == "":
            raise ValidationError("Participant name cannot be empty.")

        for participant in performance.participants:
            if participant.lower() == name.lower():
                raise ConflictError("Participant is already registered.")

        capacity = self.get_performance_capacity(performance)

        if len(performance.participants) >= capacity:
            raise ConflictError("Workshop is full.")

        performance.participants.append(name)

        return performance

    def get_places_left(self, performance):
        if not isinstance(performance, WorkshopPerformance):
            raise ValidationError("This performance is not a workshop.")

        capacity = self.get_performance_capacity(performance)

        return capacity - len(performance.participants)

    def delete_performance(self, performance_id):
        performance = self.get_performance_by_id(performance_id)

        self.performances.remove(performance)

    def update_performance(self, performance_id, new_performance):
        old_performance = self.get_performance_by_id(performance_id)

        index = self.performances.index(old_performance)

        self.performances.remove(old_performance)

        try:
            self.check_festival_day(new_performance)
            self.check_performance_venue(new_performance)
            self.check_performance_artists(new_performance)
            self.check_venue_conflict(new_performance)
            self.check_artist_conflict(new_performance)

            for performance in self.performances:
                if performance.id == new_performance.id:
                    raise ConflictError("Performance already exists.")

        except (ValueError, FestivalError):
            self.performances.insert(index, old_performance)
            raise

        self.performances.insert(index, new_performance)

        return new_performance

    def get_programme(self):
        return sorted(
            self.performances,
            key=lambda performance: (
                performance.start,
                self.get_venue_by_slug(performance.venue).name,
            ),
        )

    def get_programme_by_day(self, day):
        return [
            performance
            for performance in self.get_programme()
            if performance.festival_day == day
        ]

    def get_programme_by_venue(self, venue_slug):
        self.get_venue_by_slug(venue_slug)

        return [
            performance
            for performance in self.get_programme()
            if performance.venue == venue_slug
        ]

    def get_artist_performances(self, artist_slug):
        self.get_artist_by_slug(artist_slug)

        performances = []

        for performance in self.get_programme():
            artists = self.get_performance_artists(performance)

            if artist_slug in artists:
                performances.append(performance)

        return performances

    def get_artist_show_count(self, artist_slug):
        return len(self.get_artist_performances(artist_slug))

    def get_now_playing(self, moment):
        if isinstance(moment, str):
            moment = datetime.fromisoformat(moment)

        now_playing = []

        for performance in self.get_programme():
            if performance.start <= moment < performance.end:
                now_playing.append(performance)

        return now_playing

    def get_up_next(self, moment):
        if isinstance(moment, str):
            moment = datetime.fromisoformat(moment)

        future_performances = [
            performance
            for performance in self.get_programme()
            if performance.start > moment
        ]

        return future_performances[:3]

    def get_artists_sorted(self):
        return sorted(
            self.artists,
            key=lambda artist: artist.slug,
        )

    def get_venues(self):
        return self.venues

    def get_performance_details(self, performance):
        venue = self.get_venue_by_slug(performance.venue)

        artists = []

        for artist_slug in self.get_performance_artists(performance):
            artist = self.get_artist_by_slug(artist_slug)

            artists.append(
                {
                    "slug": artist.slug,
                    "name": artist.name,
                }
            )

        data = {
            "id": performance.id,
            "kind": performance.kind,
            "title": performance.title,
            "venue": performance.venue,
            "venue_name": venue.name,
            "start": performance.start.isoformat(timespec="minutes"),
            "end": performance.end.isoformat(timespec="minutes"),
            "duration_minutes": performance.duration_minutes,
            "festival_day": performance.festival_day,
            "description": performance.description,
            "capacity": self.get_performance_capacity(performance),
            "artists": artists,
        }

        if isinstance(performance, SoloPerformance):
            data["artist"] = performance.artist
            data["min_age"] = performance.min_age
            data["summary"] = (
                f"Solo show by "
                f"{self.get_artist_by_slug(performance.artist).name}"
            )

        elif isinstance(performance, LineupPerformance):
            data["host"] = performance.host
            data["acts"] = performance.acts

            host = self.get_artist_by_slug(performance.host)

            act_names = [
                self.get_artist_by_slug(act).name
                for act in performance.acts
            ]

            data["summary"] = (
                    f"Hosted by {host.name}, with "
                    + ", ".join(act_names)
            )

        elif isinstance(performance, WorkshopPerformance):
            data["teacher"] = performance.teacher
            data["max_participants"] = performance.max_participants
            data["participants"] = performance.participants
            data["places_left"] = self.get_places_left(performance)

            teacher = self.get_artist_by_slug(performance.teacher)

            data["summary"] = f"Workshop with {teacher.name}"

        return data
