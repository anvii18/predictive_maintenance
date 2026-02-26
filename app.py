import streamlit as st
import sys
import os

# Add project directories to Python path
sys.path.append(os.path.dirname(__file__))

# Import and run frontend
from frontend.dashboard import *
