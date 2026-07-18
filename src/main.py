from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import tempfile
import sys

# Insert the src directory at the front of sys.path so our local engine.py
# takes precedence over any pip package with the same name.
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from engine import RedactionEngine

app = FastAPI(title="PII Redaction Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 10 MB limit
MAX_FILE_SIZE = 10 * 1024 * 1024 

# Load engine globally so it stays in memory
print("Loading RedactionEngine...")
engine = RedactionEngine()
print("RedactionEngine loaded.")

def cleanup_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/redact")
async def redact_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
    
    # Read file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        
    # Save the uploaded file to a temporary file
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    temp_input.write(contents)
    temp_input.close()
    
    temp_output_path = temp_input.name.replace(".docx", "_redacted.docx")
    
    try:
        # Run redaction
        engine.process_document(temp_input.name, temp_output_path)
    except Exception as e:
        cleanup_file(temp_input.name)
        cleanup_file(temp_output_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
        
    # Schedule cleanup after the response is sent
    background_tasks.add_task(cleanup_file, temp_input.name)
    background_tasks.add_task(cleanup_file, temp_output_path)
    
    return FileResponse(
        temp_output_path, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"redacted_{file.filename}"
    )

# Mount the static directory to serve index.html
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
