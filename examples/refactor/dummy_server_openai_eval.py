import difflib
import json
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

with open("/tmp/celeb_samples.jsonl", "r") as f:
    ALL_DATA = [json.loads(line.strip()) for line in f.readlines()]

app = FastAPI()


class InputData(BaseModel):
    input: str


@app.post("/completion/", response_class=PlainTextResponse)
def get_completion(data: InputData):
    available_inputs = [d["input"] for d in ALL_DATA]
    closest_input = difflib.get_close_matches(data.input, available_inputs)[0]
    for i, d in enumerate(ALL_DATA):
        if d["input"] == closest_input:
            return ALL_DATA[i]["output"]
    return "No match found"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
