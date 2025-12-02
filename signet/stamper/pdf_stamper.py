from signet.stamper.stamper import Stamper

class PDFStamper(Stamper):
    def __init__(self, userdata: dict):
        super().__init__(userdata)

    def watermark_text(self) -> str:
        return f"Licenciado para {self.userdata.get('fullname') or 'Sem dado'}\n{self.userdata.get('email') or 'Sem dado'} | Documento: {self.userdata.get('document') or 'Sem dado'} | Em: {self.userdata.get('generated_at') or 'Sem dado'}"
