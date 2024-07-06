import argparse
import datetime
import functools
import json
import pprint
from importlib import resources
from pathlib import Path
from string import Template
from typing import TypedDict

import polars as pl
import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, PlainTextResponse

pl.Config.set_tbl_hide_dataframe_shape(active=True)
pl.Config.set_tbl_cols(255)
pl.Config.set_tbl_rows(255)
pl.Config.set_fmt_str_lengths(65535)


class Config(TypedDict):
    url: str
    list: Path
    outdir: Path


config: Config = {
    "url": "http://localhost",
    "list": Path(),
    "outdir": Path(),
}
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
    if config["list"].exists():
        tbl = pl.read_csv(config["list"], separator="\t")
        tbl = tbl.join(responses, on="id", how="outer", coalesce=True)
    else:
        tbl = responses
    with resources.files("sice").joinpath("view.html").open() as fin:
        view_html = Template(fin.read())
    body = tbl._repr_html_()  # type: ignore[reportPrivateUsage]
    body = body.replace("&quot;", "")
    content = view_html.safe_substitute(body=body)
    return HTMLResponse(content)


def read_responses() -> pl.DataFrame:
    rows = [pl.read_ndjson(p) for p in config["outdir"].glob("*.json")]
    return pl.concat(rows, how="diagonal")


def save(report: dict[str, str]) -> None:
    report["time"] = datetime.datetime.now().isoformat(timespec="seconds")
    outfile = config["outdir"] / (report["id"] + ".json")
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
    return template.safe_substitute(SICE_URL=config["outdir"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default=config["url"])
    parser.add_argument("-l", "--list", type=Path, default=config["list"])
    parser.add_argument("-o", "--outdir", type=Path, default=config["outdir"])
    parser.add_argument("-p", "--port", type=int, default=8000)
    args = parser.parse_args()
    config["url"] = args.url
    config["list"] = args.list
    config["outdir"] = args.outdir
    config["outdir"].mkdir(0o755, exist_ok=True)
    uvicorn.run(app, port=args.port, log_level="info")
