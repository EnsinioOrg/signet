class Stamper:
    def __init__(self, userdata: dict):
        self.userdata = userdata

    def watermark_text(self) -> str:
        return f"This is a licensed file."