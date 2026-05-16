# roadmap.md

# Quick Commerce Cart Comparator — Development Roadmap

This roadmap is optimized for:
- approximately 10 focused hours
- development over 2 days
- a working end-to-end MVP
- personal use
- portfolio/demo value

The goal is NOT to build:
- a production-grade platform
- a startup-scale system
- a perfectly generalized OCR engine

The goal IS to build:
- a practical
- functional
- polished
- real-world demo

that works reliably enough for:
- personal use
- friends and family
- project showcase

---

# Final MVP Goal

The final application should:

```text
Upload screenshot
→ Extract products
→ Fetch live competitor prices
→ Compare prices
→ Detect out-of-stock items
→ Display savings
```

---

# Recommended Project Scope

To reduce complexity:

Initially support:
- one source app only
- one screenshot layout
- one competitor if necessary

This dramatically simplifies:
- OCR
- parsing
- matching
- testing

Avoid trying to support:
- every quick-commerce app
- every screenshot style
- every phone resolution

---

# Final Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| Styling | Tailwind CSS |
| Backend | FastAPI |
| OCR | Tesseract OCR |
| Image Processing | OpenCV |
| Matching | RapidFuzz |
| API Requests | httpx |
| Async Backend | asyncio |
| Storage | In-memory Python structures |

---

# Technologies Explicitly Avoided

The following technologies are intentionally excluded:

- PostgreSQL
- Redis
- Docker
- Kubernetes
- Vector databases
- Embeddings
- Semantic AI pipelines
- LangChain
- Recommendation systems
- Browser automation initially
- Selenium initially
- Large cloud infrastructure

Reason:
- unnecessary complexity
- limited development time
- minimal project scope

---

# High-Level Architecture

```text
Frontend
   ↓
FastAPI Backend
   ↓
OCR Pipeline
   ↓
Product Parser
   ↓
Competitor API Fetcher
   ↓
Matching Engine
   ↓
Comparison Logic
   ↓
Frontend Display
```

---

# DAY 1 ROADMAP

# Goal

By the end of Day 1:

```text
Screenshot → OCR → Product Extraction → Live Price Fetching
```

should work.

---

# Hour 1 — Backend Setup

# Objective

Create the FastAPI project structure.

---

# Tasks

Create:

```text
app/
 ├── main.py
 ├── ocr.py
 ├── parser.py
 ├── fetchers.py
 └── compare.py
```

---

# Install Dependencies

```bash
pip install fastapi uvicorn python-multipart
```

---

# Create Upload Endpoint

Example:

```python
POST /upload
```

This endpoint should:
- accept image uploads
- save/process the screenshot
- return extracted data later

---

# Expected Outcome

You should now have:
- a running backend
- image upload support
- working API routes

---

# Hour 2 — OCR Pipeline

# Objective

Convert screenshot images into text.

---

# Install OCR Libraries

```bash
pip install pytesseract opencv-python pillow
```

Install:
- Tesseract OCR engine

---

# Tasks

Implement:

```text
Image
→ OpenCV preprocessing
→ OCR extraction
→ Raw text
```

---

# OpenCV Preprocessing

Apply:
- grayscale conversion
- thresholding
- denoising

This improves OCR quality significantly.

---

# Expected Outcome

You should now be able to:
- upload screenshot
- extract raw cart text

---

# Hour 3 — Product Parsing

# Objective

Convert messy OCR text into structured product objects.

---

# Example

OCR output:

```text
Amul Taaza Milk ₹32
Bread ₹45
```

Parsed output:

```json
[
  {
    "name": "Amul Taaza Milk",
    "price": 32
  }
]
```

---

# Tasks

Use:
- regex
- string cleanup
- normalization

Focus ONLY on:
- your own screenshot patterns

Do NOT attempt generic parsing.

---

# Matching Cleanup

Use:
- lowercase normalization
- symbol removal
- spacing cleanup

---

# Expected Outcome

You should now have:
- structured cart products
- parsed prices
- clean searchable names

---

# Hour 4 — Discover Competitor APIs

# Objective

Find how competitor apps fetch product data internally.

---

# Tools

Use:
- browser developer tools
- Network tab
- XHR/fetch requests

---

# Process

1. Open quick-commerce website
2. Search for products manually
3. Observe network requests
4. Find JSON product APIs
5. Copy request structure

---

# Important

DO NOT automate browsers yet.

Avoid:
- Playwright initially
- Selenium initially

The goal is only:
- discovering API endpoints

---

# Expected Outcome

You should be able to:
- manually call competitor product APIs
- receive live JSON product data

---

# Hour 5 — First End-to-End Integration

# Objective

Connect all components together.

---

# Final Flow

```text
Upload screenshot
→ OCR extraction
→ Product parsing
→ Competitor API request
→ Product comparison
```

---

# Expected Outcome

You should now have:
- a fully working backend pipeline
- live price fetching
- basic comparison logic

Even ugly JSON output is acceptable.

---

# DAY 2 ROADMAP

# Goal

By the end of Day 2:

```text
Polished UI + Better Matching + Out-of-Stock Detection
```

should work.

---

# Hour 6 — Product Matching Improvements

# Objective

Improve matching accuracy.

---

# Install

```bash
pip install rapidfuzz
```

---

# Tasks

Use:
- token similarity
- fuzzy matching
- quantity checks
- brand matching

Example:

```python
fuzz.token_sort_ratio(a, b)
```

---

# Important

Do NOT overcomplicate matching.

Simple fuzzy matching is sufficient.

---

# Expected Outcome

The system should now:
- match products more accurately
- reduce false comparisons

---

# Hour 7 — Frontend Development

# Objective

Build a clean user interface.

---

# Setup

Create frontend using:
- Next.js
- Tailwind CSS

---

# Build UI Components

Required components:
- screenshot upload button
- loading state
- comparison table
- savings summary

---

# Example UI

| Product | Current Price | Competitor Price |
|---|---|---|
| Milk | ₹32 | ₹30 |

---

# Expected Outcome

Users should now be able to:
- upload screenshots visually
- view comparisons cleanly
- see savings instantly

---

# Hour 8 — Out-of-Stock Detection

# Objective

Handle unavailable products.

---

# Tasks

Parse competitor API fields like:

```json
{
  "in_stock": false
}
```

or:

```json
{
  "inventory": 0
}
```

Convert into:

```text
Out of Stock
```

---

# Expected Outcome

The UI should clearly show:
- unavailable products
- missing competitor items

---

# Hour 9 — OCR and Parsing Polish

# Objective

Improve extraction reliability.

---

# Improve

- thresholding
- image scaling
- regex cleanup
- spacing cleanup
- OCR preprocessing

---

# Important

This phase often improves quality dramatically.

Small OCR improvements produce large UX improvements.

---

# Expected Outcome

The system should now:
- extract cleaner products
- make fewer parsing mistakes
- produce more reliable matches

---

# Hour 10 — Final Polish

# Objective

Improve presentation and usability.

---

# Polish Areas

Improve:
- spacing
- loading states
- typography
- totals display
- savings display
- error messages

---

# Add Final Features

Add:
- total cart comparison
- savings calculation
- better formatting
- cleaner responses

---

# Expected Outcome

The project should now feel:
- polished
- functional
- real-world
- demo-ready

---

# Final Expected Features

At the end of the roadmap, the application should support:

- screenshot upload
- OCR extraction
- product parsing
- live competitor pricing
- out-of-stock detection
- fuzzy product matching
- total price comparison
- savings calculation
- polished frontend UI

---

# Final Engineering Philosophy

This project intentionally prioritizes:

- practicality
- simplicity
- integration
- real functionality

instead of:

- complex AI
- enterprise architecture
- overengineering
- unnecessary infrastructure

---

# Final Success Criteria

The project is successful if:

1. OCR works reasonably well
2. Products are extracted correctly
3. Competitor prices are fetched live
4. Out-of-stock products are detected
5. Savings are calculated correctly
6. The UI feels polished and usable

Perfect accuracy is NOT required.

A clean and functional end-to-end demo is the primary goal.

---

# Final Takeaway

This project demonstrates:

- OCR integration
- Computer Vision preprocessing
- API reverse engineering
- Async backend engineering
- Fuzzy product matching
- Full-stack web development
- Real-world systems integration

without requiring:
- advanced machine learning
- distributed systems
- expensive infrastructure
- large-scale deployment

