from datetime import datetime , timedelta

class Performance :
    def __init__(self,kind,title,venue,start,duration_minutes,description):

        title = title.strip()

        if title == "" :
            raise ValueError("Title should not be empty")

        description = description.strip()

        if duration_minutes < 1 or duration_minutes > 360 :
            raise ValueError("The duration between 1 and 360")

        start = datetime.fromisoformat(start)

        end = start + timedelta(minutes = duration_minutes)

        start_for_id = start.strftime("%Y-%m-%d-%H%M")

        #id = "-".join[venue,start]

        id = venue + "-" + start_for_id

        festival_day = start - timedelta(days = 1)

        if start.hour < 6 :
            festival_day = festival_day.strftime("%Y-%m-%d")
        else :
             festival_day =  start.strftime("%Y-%m-%d")

        self.kind = kind
        self.title = title
        self.venue = venue
        self.start = start
        self.duration_minutes = duration_minutes
        self.description = description
        self.end = end
        self.id = id
        self.festival_day = festival_day

class SoloPerformance(Performance):
    def __init__(self,kind,title,venue,start,duration_minutes,description,artist,min_age):
        super().__init__(kind,title,venue,start,duration_minutes,description)

        if min_age < 0 or min_age > 18:
            raise ValueError("Your age should between 0 and 18")

        self.artist = artist
        self.min_age = min_age

class LineupPerformance(Performance):
    def __init__(self,kind,title,venue,start,duration_minutes,description,host,acts):
        super().__init__(kind,title,venue,start,duration_minutes,description)
        if len(acts) < 2 :
            raise ValueError("Acts should contain at least 2 artists")

        if len(acts) != len(set(acts)):
            raise ValueError("Each act can appear only once.")

        if host in acts :
            raise ValueError("Host should not be with acts")

        self.min_duration_minutes = len(acts) * 10 + (len(acts) - 1) * 3

        if duration_minutes < self.min_duration_minutes:
            raise ValueError("The lineup duration is too short.")

        self.host = host
        self.acts = acts

class WorkshopPerformance(Performance) :
    def __init__(self, kind, title, venue, start, duration_minutes, description, teacher, max_participants, participants):
        super().__init__(kind, title, venue, start, duration_minutes, description)

        if max_participants < 1 :
            raise ValueError("max_participants should be 1 at least")

        clean_participants = []

        for participant in participants:
            participant = participant.strip()

            if participant == "":
                raise ValueError("Participant name cannot be empty.")

            for existing_participant in clean_participants:
                if participant.lower() == existing_participant.lower():
                    raise ValueError("Participant is already registered.")

            clean_participants.append(participant)

        self.teacher = teacher
        self.max_participants = max_participants
        self.participants = clean_participants






















