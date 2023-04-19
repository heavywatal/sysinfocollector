# sice: System Information Collector for Education

Install sice and its dependencies:
```sh
python3 -m venv ~/.virtualenvs/fapi
source ~/.virtualenvs/fapi/bin/activate
git clone https://github.com/heavywatal/sysinfocollector.git
cd sysinfocollector/
pip3 install -v -e .[dev]
```

Run sice:
```sh
export SICE_STUDENTS_LIST="../list.tsv"
export SICE_URL="https://example.com/sice"
uvicorn sice.main:app
```

Students report their system information from R console:
```r
student_id = "C1SB0000"
source("https://example.com/sice/report.R")
```

View collected infomation at `${SICE_URL}/view/`.
