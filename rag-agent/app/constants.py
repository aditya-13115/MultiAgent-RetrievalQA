import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory for storing data
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_DIR = os.path.join(DATA_DIR, "index")  # THIS IS THE MISSING VARIABLE

# Ensure directories exist
os.makedirs(INDEX_DIR, exist_ok=True)

# Chunking Configuration
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150