import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Cấu hình đường dẫn cơ sở
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    FAISS_INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")
    
    # Cấu hình cụ thể cho từng Index
    LAW_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, "law_index")
    TEMPLATE_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, "template_index")
    CONTRACT_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, "contract_index")
    
    # Model config
    EMBEDDING_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
