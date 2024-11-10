import os 
import openai
import dotenv

dotenv.load_dotenv()

api_key = os.environ["WEAVIATE-API-KEY"] 
print(api_key)
# print(WEAVIATE-API-KEY)

