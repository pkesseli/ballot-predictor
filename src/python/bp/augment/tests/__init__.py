import jsonpickle
from dotenv import load_dotenv

load_dotenv()
jsonpickle.set_decoder_options("json", strict=False)
