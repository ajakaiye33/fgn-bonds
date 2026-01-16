import os
import sys

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Streamlit app
from streamlit_app import main

if __name__ == "__main__":
    main() 