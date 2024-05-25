import datetime
import functools
import json
import os
import pprint
from importlib import resources
from pathlib import Path
from string import Template

import polars as pl
import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, PlainTextResponse

pl.Config.set_tbl_hide_dataframe_shape(active=True)
pl.Config.set_tbl_cols(255)
pl.Config.set_tbl_rows(255)
pl.Config.set_fmt_str_lengths(65535)

response_dir = Path(os.getenv("SICE_RESPONSE_DIR", "."))
response_dir.mkdir(0o755, exist_ok=True)

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello, world!"}


@app.get("/report.R")
async def r() -> PlainTextResponse:
    return PlainTextResponse(_report_r())


@app.post("/report")
async def create_report(report: dict[str, str]) -> PlainTextResponse:
    save(report)
    return PlainTextResponse(message(report))


@app.get("/view/")
async def create_view() -> HTMLResponse:
    responses = read_responses()
    if list_file := os.getenv("SICE_STUDENTS_LIST"):
        tbl = pl.read_csv(list_file, separator="\t")
        tbl = tbl.join(responses, on="id", how="outer_coalesce")
    else:
        tbl = responses
    with resources.files("sice").joinpath("view.html").open() as fin:
        view_html = Template(fin.read())
    body = tbl._repr_html_()  # noqa: SLF001 # type: ignore[reportPrivateUsage]
    body = body.replace("&quot;", "")
    content = view_html.safe_substitute(body=body)
    return HTMLResponse(content)


def read_responses() -> pl.DataFrame:
    rows = [pl.read_ndjson(p) for p in response_dir.glob("*.json")]
    return pl.concat(rows, how="diagonal")


def save(report: dict[str, str]) -> None:
    report["time"] = datetime.datetime.now().isoformat(timespec="seconds")
    outfile = response_dir / (report["id"] + ".json")
    with outfile.open("w") as fout:
        json.dump(jsonable_encoder(report), fout)


def message(res: dict[str, str]) -> str:
    return f"""
Hello, {res["id"]}. Thank you for submitting your system information.

{pprint.pformat(res)}
"""


@functools.cache
def _report_r() -> str:
    src = resources.files("sice").joinpath("report.R")
    with src.open() as fin:
        template = Template(fin.read())
    return template.safe_substitute(SICE_URL=os.getenv("SICE_URL"))


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
