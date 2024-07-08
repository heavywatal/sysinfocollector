# sice: System Information Collector for Education

Install sice and its dependencies:
```sh
git clone https://github.com/heavywatal/sysinfocollector.git
cd sysinfocollector/
python3 -m venv .venv
source .venv/bin/activate
pip3 install -v -e .[dev]
```

Run sice:
```sh
python3 -m sice.main -l id_list.tsv -o outdir -u "https://example.com/sice"
```

Students report their system information from R console:
```r
student_id = "C1SB0000"
source("https://example.com/sice/report.R")
```

View collected infomation at `${URL}/view/`.
