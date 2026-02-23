from typing import Literal

from pydantic import BaseModel


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnimalResult(BaseModel):
    species: str
    endangerment: str


class SpeciesIdentificationResponse(BaseModel):
    name: str
    sci: str
    confidence: float


class ScanResultResponse(BaseModel):
    name: str
    sci: str
    status: Literal["CR", "EN", "VU", "NT", "LC"]
    endangermentLabel: str
    confidence: float
    population: str
    trend: Literal["Increasing", "Stable", "Decreasing", "Unknown"]
    threatScore: int
    habitat: str
    threats: list[str]
    nearbySightings: int
    isEndangered: bool
    description: str = ""
    savedToMap: bool = False
    openaiQuotaExceeded: bool = False


class SightingResponse(BaseModel):
    id: int
    name: str
    sci: str
    status: Literal["CR", "EN", "VU", "NT", "LC"]
    lat: float
    lng: float
    timestamp: int
    threat_score: int
    reporter: str


class LeaderboardEntryResponse(BaseModel):
    rank: int
    name: str
    score: int
    species: int
    endangered_species: int
    avg_threat_score: float
    joined: str


class UserStatsResponse(BaseModel):
    endangered_species: int
    total_sightings: int
    avg_threat_score: float


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
