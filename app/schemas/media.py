from pydantic import BaseModel


class UploadOut(BaseModel):
    filename: str
    relative_path: str
    public_url: str
    size_bytes: int
    content_type: str