import fitz
import os

from signet.util.json import respond_json
from signet.stamper.stamper import Stamper

class FitzCannotOpenFileException(Exception):
    pass

class PDFTracker:
    def __init__(self, input_path: str, output_path: str, stamper: Stamper):
        self.input_path = input_path
        self.output_path = output_path
        self.stamper = stamper
        self.doc = None

    def process_metadata_only(self):
        # 1. validate userdata
        if not self.stamper.userdata:
            respond_json({"error": "User data is required for metadata."}, pretty=True)
            return

        # 2. check file exists
        if self.file_exists(self.input_path) is False:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_path}")
        
        # 3. open file
        try:
            self.open_file(self.input_path)
        except FitzCannotOpenFileException as e:
            respond_json({"error": str(e)}, pretty=True)
            return
        
        # 4. set metadata
        metadata = self.set_pdf_metadata()

        # 6. save file
        output_path = self.save_file(self.output_path)

        # 7. respond with location of saved file
        respond_json({"status": "OK", "output_path": output_path, "metadata": metadata}, pretty=True)


    def file_exists(self, input_path: str) -> bool:
        return os.path.isfile(input_path)


    def open_file(self, input_path: str):
        try:
            self.doc = fitz.open(input_path)
        except Exception as e:
            raise FitzCannotOpenFileException(f"Erro ao abrir PDF: {e}")
    

    def set_pdf_metadata(self) -> dict:
        metadata = self.doc.metadata
        metadata['author'] = self.stamper.userdata.get('fullname', "Sem dado")
        metadata['producer'] = self.stamper.userdata.get('producer', "Sem dado")

        if (self.stamper.userdata.get('title')):
            metadata['title'] = self.stamper.userdata.get('title')

        if (self.stamper.userdata.get('keywords')):
            metadata['keywords'] = self.stamper.userdata.get('keywords')

        self.doc.set_metadata(metadata)
        return metadata

    def save_file(self, output_path: str) -> str:
        self.doc.save(output_path, garbage=4, deflate=True)
        self.doc.close()
        return output_path
