import logging
logging.basicConfig(level=logging.INFO)
try:
    import easyocr
    logging.info("easyocr import successful")
    reader = easyocr.Reader(['de'], gpu=False)
    logging.info("EasyOCR Reader initialized")
except Exception as e:
    logging.error(f"Exception: {e}", exc_info=True)
input("Press Enter to exit...")