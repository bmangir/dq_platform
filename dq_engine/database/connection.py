import os

from dotenv import load_dotenv


load_dotenv()


def get_postgres_connection_string() -> str:

    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DATABASE")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    required = {
        "POSTGRES_HOST": host,
        "POSTGRES_PORT": port,
        "POSTGRES_DATABASE": database,
        "POSTGRES_USER": user,
        "POSTGRES_PASSWORD": password,
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing PostgreSQL environment variables: "
            + ", ".join(missing)
        )

    return (
        f"postgresql://{user}:{password}"
        f"@{host}:{port}/{database}"
    )