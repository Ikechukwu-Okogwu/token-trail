"""Schemas for auth endpoints."""
from pydantic import BaseModel


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    accessToken: str


class MeResponse(BaseModel):
    id: str
    name: str
    email: str
