import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")      
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")  
SMTP_SERVER = "smtp.gmail.com"                
SMTP_PORT = 465

INPUT_FILE = "ranking.xlsx"
OUTPUT_FILE = "Keyword_Ranking_Results_Final10.xlsx"


TARGET_DOMAIN = "omorganickitchen.com"
BUSINESS_NAME_SNIPPET = "OMKITCHEN | Homestyle Organic Meals Delivery"
MAX_ORG_PAGES = 5