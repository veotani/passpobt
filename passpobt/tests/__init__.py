from dotenv import load_dotenv


try:
    load_dotenv()
except IOError:
    print("No .env file found.")
