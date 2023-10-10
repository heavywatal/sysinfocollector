import datetime
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
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

os.environ["POLARS_FMT_MAX_COLS"] = "255"
os.environ["POLARS_FMT_MAX_ROWS"] = "255"
os.environ["POLARS_FMT_STR_LEN"] = "65535"

response_dir = Path(os.getenv("SICE_RESPONSE_DIR", "."))
response_dir.mkdir(0o755, exist_ok=True)
reportr = response_dir / "report.R"
reportr_src = resources.files("sice").joinpath("report.R")
with reportr_src.open() as fin:
    template = Template(fin.read())
with reportr.open("w") as fout:
    fout.write(template.safe_substitute(SICE_URL=os.getenv("SICE_URL")))

app = FastAPI()
pl.Config.set_tbl_hide_dataframe_shape(active=True)


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/report.R")
async def r():
    return FileResponse(reportr)


@app.post("/report")
async def create_report(report: dict[str, str]):
    save(report)
    return PlainTextResponse(message(report))


@app.get("/view/")
async def create_view():
    responses = read_responses()
    if list_file := os.getenv("SICE_STUDENTS_LIST"):
        tbl = pl.read_csv(list_file, separator="\t")
        tbl = tbl.join(responses, on="id", how="outer")
    else:
        tbl = responses
    content = """<html>
<head>
<style>
html {
  font-family: sans-serif;
}

table,
thead,
tbody,
tfoot,
tr,
th,
td {
  border: none;
}

table {
  white-space: nowrap;
}

tr {
  vertical-align: ;
}

th {
  vertical-align: middle;
  font-weight: normal;
}

td {
  vertical-align: middle;
  padding: 2px 4px;
}

tr:nth-child(even) {
  background-color: #eeeeee;
}
</style>
<body>
"""
    content += tbl._repr_html_().replace("&quot;", "")  # noqa: SLF001
    content += "</body></html>"
    return HTMLResponse(content)


def read_responses():
    rows = [pl.read_ndjson(p) for p in response_dir.glob("*.json")]
    return pl.concat(rows, how="diagonal")


def save(report: dict[str, str]):
    report["time"] = datetime.datetime.now().isoformat(timespec="seconds")
    outfile = response_dir / (report["id"] + ".json")
    with outfile.open("w") as fout:
        json.dump(jsonable_encoder(report), fout)


def message(res: dict[str, str]):
    return f"""
Hello, {res["id"]}. Thank you for submitting your system information.

{pprint.pformat(res)}
"""


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
