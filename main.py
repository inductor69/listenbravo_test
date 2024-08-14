from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import MetaData, Table
from db import engine, Base, SessionLocal
from utils import parse_csv, classify_technology_company, create_table_from_csv
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os

app = FastAPI()

metadata = MetaData()
table_name = "companies"

@app.get("/")
async def get_upload_form():
    with open("upload.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    df = parse_csv(file.file)

    if "Description" not in df.columns:
        raise HTTPException(status_code=400, detail="'Description' column not found in CSV")

    df["Technology Company"] = df["Description"].apply(classify_technology_company)

    table = create_table_from_csv(metadata, table_name, df)
    
    metadata.create_all(engine)

    # Save the DataFrame to a CSV file to serve later
    df.to_csv("latest_table.csv", index=False)

    preview_html = df.head().to_html(classes="table table-striped")
    
    html_content = f"""
    <h1>Table '{table_name}' created successfully!</h1>
    <h2>Preview:</h2>
    {preview_html}
    <br>
    <a href="/download-table/" download>
        <button>Download Complete Table</button>
    </a>
    """

    return HTMLResponse(content=html_content)

@app.get("/download-table/")
async def download_table():
    file_path = "latest_table.csv"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="table.csv", media_type='text/csv')
    else:
        raise HTTPException(status_code=404, detail="Table not found. Please upload a CSV first.")
