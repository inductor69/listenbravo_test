import pandas as pd
import google.generativeai as genai
import os
from sqlalchemy import Column, String, Table
from sqlalchemy.types import Boolean
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini Pro API
genai.configure(api_key=os.getenv("LLM_API_KEY"))

def parse_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def classify_technology_company(description: str) -> str:
    # Use the Gemini model for classification
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Is this a technology company? {description}")
    return "Yes" if "yes" in response.text.lower() else "No"

from sqlalchemy import Table

def create_table_from_csv(metadata: MetaData, table_name: str, df: pd.DataFrame) -> Table:
    # Check if table already exists
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
    else:
        columns = [
            Column(col_name, String) for col_name in df.columns if col_name != "Technology Company"
        ]
        columns.append(Column("Technology Company", Boolean))
        
        table = Table(table_name, metadata, *columns, extend_existing=True)

    return table
