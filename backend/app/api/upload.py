from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    # TODO: save file, store metadata, trigger parsing pipeline
    return {"filename": file.filename, "status": "received"}
