from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

print("Mongo URI:", MONGO_URI)
print("Database Name:", DB_NAME)
