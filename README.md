# sice: System Information Collector for Education

Install sice and its dependencies:
```sh
git clone https://github.com/heavywatal/sysinfocollector.git
cd sysinfocollector/
uv venv --allow-existing
source .venv/bin/activate
uv pip install -v -e .[dev]
```

Run sice:
```sh
sice -l id_list.tsv -o outdir -u "https://example.com/sice"
```

Students report their system information from R console:
```r
student_id = "C1SB0000"
source("https://example.com/sice/report.R")
```

View collected infomation at `${URL}/view/`.
