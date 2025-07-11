import os
import aiofiles
import aiofiles.os
from pathlib import Path
from typing import Optional, List, BinaryIO
import hashlib
from datetime import datetime

class LocalFileStorage:
    """Local file system storage for PDFs and other ETL artifacts"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.raw_pdfs_path = self.base_path / "raw_pdfs"
        self.processed_path = self.base_path / "processed"
        self.temp_path = self.base_path / "temp"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for path in [self.raw_pdfs_path, self.processed_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def save_pdf(self, content: bytes, filename: str, company: str, year: int) -> str:
        """Save PDF content to local storage"""
        # Create company/year directory structure
        company_path = self.raw_pdfs_path / company / str(year)
        company_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename if needed
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        file_path = company_path / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return str(file_path)
    
    async def get_pdf_path(self, company: str, year: int, filename: str) -> Optional[str]:
        """Get path to stored PDF"""
        file_path = self.raw_pdfs_path / company / str(year) / filename
        if file_path.exists():
            return str(file_path)
        return None
    
    async def list_company_pdfs(self, company: str, year: Optional[int] = None) -> List[str]:
        """List all PDFs for a company"""
        company_path = self.raw_pdfs_path / company
        if not company_path.exists():
            return []
        
        pdfs = []
        if year:
            year_path = company_path / str(year)
            if year_path.exists():
                pdfs.extend([str(f) for f in year_path.glob("*.pdf")])
        else:
            for year_dir in company_path.iterdir():
                if year_dir.is_dir():
                    pdfs.extend([str(f) for f in year_dir.glob("*.pdf")])
        
        return pdfs
    
    async def delete_pdf(self, company: str, year: int, filename: str) -> bool:
        """Delete a PDF file"""
        file_path = self.raw_pdfs_path / company / str(year) / filename
        if file_path.exists():
            await aiofiles.os.remove(file_path)
            return True
        return False
    
    async def save_processed_data(self, data: dict, filename: str) -> str:
        """Save processed data as JSON"""
        file_path = self.processed_path / filename
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(str(data))
        return str(file_path)
    
    async def get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(4096)
                if not chunk:
                    break
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = await aiofiles.os.stat(file_path)
        return {
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "hash": await self.get_file_hash(file_path)
        }
    
    def get_temp_path(self, filename: str) -> str:
        """Get temporary file path"""
        return str(self.temp_path / filename)
    
    async def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        current_time = datetime.now()
        for file_path in self.temp_path.glob("*"):
            if file_path.is_file():
                stat = await aiofiles.os.stat(file_path)
                file_age = current_time - datetime.fromtimestamp(stat.st_mtime)
                if file_age.total_seconds() > older_than_hours * 3600:
                    await aiofiles.os.remove(str(file_path)) 