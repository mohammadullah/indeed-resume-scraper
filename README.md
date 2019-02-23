Scrape resumes from indeed

# Setup
Install `requirements.txt` for your `Python` environment e.g
```
pip install -r requirements.txt
```

or

```
conda install --file requirements.txt
```

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

## Example
Scrape 100 resumes (1st - 100th resume) for software engineering in Canada
```bash
python indeed-scraper.py -q 'software engineer'  --name software-canada -ei 100
```

## Multiple queries
The `script.sh` can be run with a file that has a job title per line
```
./script.sh <filename>
```

Please read `script.sh` for some more details