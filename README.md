# 🏗️ Career Page Job Scraping Pipeline

This repository provides an end-to-end MLOps-friendly pipeline for scraping, extracting, and processing job listings from company career pages. It uses **Playwright** for dynamic HTML scraping, a **fine-tuned language model** for information extraction, and **pandas** for post-processing and deduplication.  

---

## 📂 Folder Structure

```
scrape-extract-jobs/
├── src/
│   ├── html_extractor/
|   |   ├── base_extractor.py
|   |   └── extractor.py
│   ├── post_extractor/
|   |   ├── base_post.py
|   |   └── post.py
│   ├── scraper/
|   |   ├── base_scraper.py
|   |   └── scraper.py
|   ├── constants.py
|   ├── utils.py
│   └── scrape_clean_extract.py
├── scratch/
├── data/
├── README.md
├── .gitignore
└── requirements.txt
```

## ⚙️ Features

- 🔍 **Scalable Scraping** — Handles static, paginated, and infinite-scroll career pages.
- 🤖 **LLM Extraction** — Uses a fine-tuned Llama 3.2 1B parameter model to convert messy HTML into structured JSON.
- 🧹 **Post-Processing** — Cleans, standardizes, deduplicates, and prepares job listings for production use.
- 📦 **Modular Design** — Each component can be developed, tested, and deployed independently.
- 🧪 **Reproducibility** — Every pipeline run is versioned using timestamps.

```bash
git clone https://github.com/your-org/career-page-scraper.git
cd career-page-scraper
pip install -r requirements.txt
```

## 🧠 Architecture

```
                   ┌──────────────┐
                   │ scraper.py   │
                   └──────┬───────┘
                          ▼
                   HTML Pages (.txt)
                          ▼
             ┌────────── extractor.py ──────────┐
             │   LLM (HTML → JSON Extraction)   │
             └──────────┬───────────────────────┘
                        ▼
               Extracted JSON/Text (.txt)
                        ▼
               ┌────── post.py ──────┐
               │   Data Cleaning     │
               │   Deduplication     │
               └────────┬────────────┘
                        ▼
                 Final DataFrame (.parquet)
```

## 🧪 Example Output from Fine Tuned LLM

```
{
  "job_id": "R157984",
  "job_title": "Senior Data Scientist",
  "location": "New York, NY",
  "company_name": "Acme Corp",
  "job_link": "https://careers.acme.com/jobs/R157984"
}
```

---

## 🙋‍♂️ Feel free to reach out to me!
- pradyuman.gangan02@gmail.com
- [LinkedIn](https://www.linkedin.com/in/pradyumangangan/)
