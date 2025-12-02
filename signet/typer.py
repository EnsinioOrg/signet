import typer
import requests

from signet.util.json import respond_json
from signet.commands.pdf import PDFWatermarker
from signet.stamper.pdf_stamper import PDFStamper

app = typer.Typer(
    add_completion=False,
    help="Signet — A simple CLI application to watermark PDF files."
)

@app.command()
def pdf(
        input_path: str,
        output_path: str,
        fullname: str = typer.Option(..., prompt=True),
        email: str = typer.Option(..., prompt=True),
        document: str = typer.Option(..., prompt=True),
        datetime: str = typer.Option(..., prompt=True),
        title: str = typer.Option(..., prompt=True),
        producer: str = typer.Option(..., prompt=True),
        keywords: str = typer.Option(..., prompt=True),
    ):

    stamper = PDFStamper(userdata={
        "fullname": fullname,
        "email": email,
        "document": document,
        "generated_at": datetime,
        "title": title,
        "producer": producer,
        "keywords": keywords,
    })
    watermarker = PDFWatermarker(input_path, output_path, stamper=stamper)
    watermarker.process_watermark()


@app.command()
def epub(input: str):
    respond_json({"error": "EPUB is not yet supported."}, pretty=True)

@app.command()
def download(url: str, output: str = typer.Option(..., prompt=True)):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        respond_json({"error": f"Failed to download file: {e}"}, pretty=True)
        return

    with open(output, 'wb') as f:
        f.write(response.content)

    respond_json({"message": f"File downloaded successfully to {output}", "output_path": output}, pretty=True)
