# Gemini Context: Smart City Traffic API

This document provides an overview of the Smart City Traffic API project, a FastAPI-based application designed to serve as a backend for traffic management.

## 1. Project Overview

The project is a Python-based API built with the FastAPI framework. Its primary purpose is to provide a secure interface for traffic-related data and operations. The core functionality currently implemented is a robust authentication system using JSON Web Tokens (JWT).

The application is structured to be modular and scalable, with a clear separation of concerns between routing, business logic (services), data models, and core functionalities like configuration and security.

## 2. Key Technologies

- **Framework:** FastAPI
- **Web Server:** Uvicorn
- **Authentication:** JWT (pyjwt), OAuth2 Password Flow
- **Password Hashing:** bcrypt
- **Configuration:** pydantic-settings, python-dotenv
- **Data Validation:** Pydantic

## 3. Project Structure

The source code is located in the `src/` directory and follows a logical organization:

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app instantiation and main router setup.
│   ├── auth/               # Authentication module.
│   │   ├── models/         # Pydantic models for User and Token.
│   │   ├── routes/         # API endpoints for authentication (/login, /me).
│   │   └── services/       # Business logic for user authentication.
│   └── core/               # Core application components.
│       ├── encryption_service.py # Handles password hashing and verification.
│       ├── jwt_service.py    # Manages JWT creation and decoding.
│       └── settings.py       # Manages application configuration.
└── run.py                  # Application entry point for running with Uvicorn.
```

## 4. Core Functionality

### 4.1. Application Startup

- The application is launched via `src/run.py`.
- This script imports the main FastAPI `app` instance from `src/app/main.py` and the configuration from `src/app/core/settings.py`.
- It uses `uvicorn` to run the application, with settings like host, port, and reload-on-change determined by environment variables.

### 4.2. Configuration

- The `core/settings.py` file uses `pydantic-settings` to load configuration from environment variables (`.env` file).
- Key settings include application host/port, environment (`development`/`production`), and JWT parameters (secret key, algorithm, expiration time).

### 4.3. Authentication Flow

The API implements OAuth2 "Password Flow" for authentication.

1.  **Login (`/api/auth/login`):**
    - The user submits their `username` and `password` to this endpoint.
    - The `auth/routes/auth.py` router receives the request.
    - It calls `AuthService.authenticate_user` to validate the credentials.
    - `AuthService` retrieves the user (currently, a hardcoded user "jesus" for demonstration) and uses `encryption_service.verify` to check the password against the stored bcrypt hash.
    - If authentication is successful, `jwt_service.create_access_token` generates a JWT containing the user's identifier (`sub`) and an expiration date.
    - The JWT is returned to the client.

2.  **Accessing Protected Routes (e.g., `/api/auth/me`):**
    - The client must include the JWT in the `Authorization` header as a "Bearer" token.
    - FastAPI's dependency injection system uses the `get_current_active_user` function from `jwt_service.py`.
    - This function decodes the token, validates its signature and expiration, and retrieves the corresponding user from `AuthService`.
    - If the token is valid and the user is active, the user object is injected into the route handler, and the request is processed. Otherwise, a 401 Unauthorized error is returned.

### 4.4. Security

- **Password Storage:** Passwords are not stored in plaintext. The `encryption_service.py` uses `bcrypt` to create a strong, salted hash of the user's password.
- **Token-Based Security:** JWTs are used to secure endpoints, ensuring that only authenticated users can access protected resources.
