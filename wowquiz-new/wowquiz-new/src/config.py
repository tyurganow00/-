from pydantic import BaseSettings

class Settings(BaseSettings):
    imap_user: str
    imap_password: str
    imap_server: str
    google_credentials_file: str
    spreadsheet_id: str

    class Config:
        env_file = '.env'

settings = Settings()