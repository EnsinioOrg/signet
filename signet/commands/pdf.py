import fitz
import os
import sys

from signet.util.json import respond_json
from signet.stamper.stamper import Stamper

# Largura inicial da faixa da marca d'água, em pontos
WATERMARK_WIDTH = 22
# Quanto a faixa cresce a cada tentativa quando o texto não cabe nem na menor fonte
WATERMARK_WIDTH_STEP = 8
# Largura máxima da faixa, em proporção da largura da página
WATERMARK_MAX_WIDTH_RATIO = 0.2
# Fontes testadas, da maior para a menor, até o texto caber na faixa
WATERMARK_FONT_SIZES = (7, 6, 5)

class FitzCannotOpenFileException(Exception):
    pass

class WatermarkDoesNotFitException(Exception):
    pass

class PDFWatermarker:
    def __init__(self, input_path: str, output_path: str, stamper: Stamper):
        self.input_path = input_path
        self.output_path = output_path
        self.stamper = stamper
        self.doc = None

    def process_watermark(self):
        # 1. validate userdata
        if not self.stamper.userdata:
            respond_json({"error": "User data is required for watermarking."}, pretty=True)
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
        
        # 5. apply watermark
        watermark_text = self.stamper.watermark_text()
        try:
            self.apply_watermark(watermark_text)
        except WatermarkDoesNotFitException as e:
            respond_json({"error": str(e)}, pretty=True)
            sys.exit(1)

        # 6. save file
        output_path = self.save_file(self.output_path)

        # 7. respond with location of saved file
        respond_json({"status": "OK", "output_path": output_path, "metadata": metadata}, pretty=True)

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


    def apply_watermark(self, watermark_text: str):
        # Páginas do mesmo tamanho usam a mesma área e fonte; calcula uma vez por tamanho
        layouts = {}

        for page in self.doc:
            # Em página com /Rotate o texto inserido cai fora da área visível; remover a rotação
            # mantém a aparência da página e deixa as coordenadas iguais às que o leitor vê
            if page.rotation:
                page.remove_rotation()

            # Determina qual o tamanho da página
            rect = page.rect

            # Determina onde na página deve ser inserido e com qual fonte
            size = (rect.width, rect.height)
            if size not in layouts:
                layouts[size] = self.fit_watermark(rect, watermark_text)
            text_rect, fontsize = layouts[size]

            # Desenha o retangulo com opacidade na área do texto
            shape = page.new_shape()
            shape.draw_rect(text_rect)
            shape.finish(
                fill=(1, 1, 1),             # fundo branco
                color=(0.5, 0.5, 0.5),      # borda cinza claro
                width=0,                    # largura da borda
                fill_opacity=0.75,          # 80% opaco (20% transparente)
                stroke_opacity=0.5,         # opacidade da borda
            )
            shape.commit()

            # Adiciona o texto no retângulo
            spare_height = page.insert_textbox(
                text_rect,
                watermark_text,
                fontsize=fontsize,
                color=(0.3, 0.3, 0.3),
                align=fitz.TEXT_ALIGN_CENTER,
                overlay=True,
                rotate=90
            )

            # Quando o texto não cabe o PyMuPDF não escreve nada e devolve um valor negativo
            if spare_height < 0:
                raise WatermarkDoesNotFitException(
                    f"Marca d'água não coube na página {page.number + 1}"
                )

    def fit_watermark(self, rect: fitz.Rect, watermark_text: str) -> tuple:
        # O teste é feito numa página auxiliar do mesmo tamanho, porque na página real o
        # retângulo de fundo precisa ser desenhado antes do texto
        scratch = fitz.open()
        try:
            page = scratch.new_page(width=rect.width, height=rect.height)

            # Primeiro diminui a fonte; se nem a menor couber, alarga a faixa para a esquerda
            width = WATERMARK_WIDTH
            max_width = max(WATERMARK_WIDTH, rect.width * WATERMARK_MAX_WIDTH_RATIO)
            while width <= max_width:
                text_rect = fitz.Rect(
                    rect.width - 3 - width,                 # borda direita menos espaço do texto
                    rect.height * 0.30,                     # posição de inicio a partir do topo
                    rect.width - 3,                         # borda direita
                    rect.height - (rect.height * 0.30)      # posição final
                )

                for fontsize in WATERMARK_FONT_SIZES:
                    spare_height = page.insert_textbox(
                        text_rect,
                        watermark_text,
                        fontsize=fontsize,
                        align=fitz.TEXT_ALIGN_CENTER,
                        rotate=90
                    )
                    if spare_height >= 0:
                        return text_rect, fontsize

                width += WATERMARK_WIDTH_STEP
        finally:
            scratch.close()

        raise WatermarkDoesNotFitException(
            f"Marca d'água não cabe em página de {rect.width:.0f}x{rect.height:.0f}pt"
        )

    def save_file(self, output_path: str) -> str:
        self.doc.save(output_path, garbage=4, deflate=True)
        self.doc.close()
        return output_path
