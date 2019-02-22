Scrape resumes from indeed

# Running script

```bash
python indeed-scraper.py -h
usage: python indeed-scraper.py <arguments>

Scrape Indeed Resumes

optional arguments:
  -h, --help         show this help message and exit
  -q query           search query to run on indeed e.g software engineer
  -l location        location scope for search
  -si start          starting index (multiples of 50)
  -ei end            ending index (multiples of 50)
  --threads threads  # of threads to run
  --override         override existing result if any
  --name name        name of search (used to save files)
```

# Example
Scrape 100 resumes (1st - 100th resume) for software engineering in Canada
```bash
python indeed-scraper.py -q 'software engineer'  --name software-canada -ei 100
```