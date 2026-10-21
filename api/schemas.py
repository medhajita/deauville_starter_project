
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ArtistCreate(StrictBody):
    name: str
    bio: str = ""
    photo_url: str = ""


class ParticipantCreate(StrictBody):
    name: str


class PerformanceBase(StrictBody):
    title: str
    venue: str
    start: datetime
    duration_minutes: int = Field(ge=1, le=360)
    description: str = ""

    @field_validator("start")
    @classmethod
    def check_local_start(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("L'heure doit être locale, sans fuseau horaire.")
        if value.second or value.microsecond:
            raise ValueError("L'heure doit être précise à la minute.")
        return value


class SoloCreate(PerformanceBase):
    kind: Literal["solo"]
    artist: str
    min_age: int = Field(ge=0, le=18)


class LineupCreate(PerformanceBase):
    kind: Literal["lineup"]
    host: str
    acts: list[str] = Field(min_length=2)


class WorkshopCreate(PerformanceBase):
    kind: Literal["workshop"]
    teacher: str
    max_participants: int = Field(ge=1)
    participants: list[str] = Field(default_factory=list)


PerformanceCreate = Annotated[
    SoloCreate | LineupCreate | WorkshopCreate,
    Field(discriminator="kind"),
]
