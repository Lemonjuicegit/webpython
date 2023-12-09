from pydantic_settings import BaseSettings

class Store(BaseSettings):
    app_name: list[str] = []
    

store = Store()