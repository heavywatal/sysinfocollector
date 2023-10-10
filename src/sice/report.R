stopifnot(exists("student_id"))
stopifnot(is.character(student_id))
stopifnot(nchar(student_id) == 8L)

required = c(
  "broom",
  "colorspace",
  "cowplot",
  "dplyr",
  "forcats",
  "fs",
  "ggplot2",
  "lubridate",
  "modelr",
  "purrr",
  "ragg",
  "readr",
  "scales",
  "stringr",
  "tibble",
  "tidyr",
  "tidyverse"
)

ipkgs = as.data.frame(installed.packages())
ipkgs = ipkgs[ipkgs$Package %in% required, ]
installed = setNames(ipkgs$Version, ipkgs$Package)
Rversion = sessionInfo()$R.version

body = list()
body$id = student_id
body$platform = Rversion$platform
body$R = paste(Rversion$major, Rversion$minor, sep = ".")
if (require("rstudioapi")) body$RStudio = as.character(rstudioapi::versionInfo()$version)
body = append(body, as.list(installed))
body$libPaths = paste(.libPaths(), collapse = ":")
# str(body)

post = function(url, body) {
  json = jsonlite::toJSON(body, auto_unbox = TRUE)
  handle = curl::new_handle()
  curl::handle_setopt(handle, postfields = json)
  curl::handle_setheaders(handle, "Content-Type" = "application/json")
  curl::curl_fetch_memory(url, handle)
}

url = "${SICE_URL}/report"
if (!startsWith(url, "https")) url = "localhost:8000/report"
res = post(url, body)
cat(rawToChar(res$content))
