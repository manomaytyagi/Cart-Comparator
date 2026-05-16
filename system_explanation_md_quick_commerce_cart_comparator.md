# system_explanation.md

# Quick Commerce Cart Comparator — System Explanation

This document explains how the Quick Commerce Cart Comparator works internally.

The purpose of this file is to help a student or developer:
- understand the architecture
- understand the data flow
- understand why each technology was chosen
- understand how the system processes screenshots
- understand how live competitor comparison works

This document assumes the application has already been built.

---

# 1. High-Level Idea

The application compares grocery cart prices across quick-commerce apps.

The user uploads a screenshot of a shopping cart from one app.

The system:
1. extracts product names from the screenshot
2. cleans and parses the text
3. searches competitor platforms for matching items
4. compares prices
5. detects unavailable products
6. calculates savings

---

# 2. Overall System Flow

The full workflow is:

```text
User uploads screenshot
        ↓
OCR extracts text
        ↓
Parser cleans product names
        ↓
Competitor APIs are queried
        ↓
Matching engine finds equivalent products
        ↓
Prices are compared
        ↓
Frontend displays savings and stock status
```

---

# 3. Frontend Overview

The frontend is built using:
- Next.js
- Tailwind CSS

The frontend is responsible for:
- screenshot upload
- loading states
- displaying results
- displaying savings

The frontend itself contains very little business logic.

Most important operations happen in the backend.

---

# 4. Backend Overview

The backend is built using:
- FastAPI
- Python

The backend handles:
- image uploads
- OCR
- product parsing
- competitor API requests
- matching logic
- comparison logic

The backend acts as the “brain” of the system.

---

# 5. Why FastAPI Was Chosen

FastAPI was chosen because:
- it is lightweight
- it is fast
- it supports async operations
- it works very well with Python
- it is ideal for APIs

The application needs to make multiple external requests quickly.

FastAPI makes this easier.

---

# 6. OCR Pipeline

The OCR pipeline converts screenshots into readable text.

The stack used is:
- Tesseract OCR
- OpenCV
- pytesseract

---

# 7. Why OCR Is Needed

Quick-commerce apps do not provide cart export APIs.

Therefore:
- the only accessible input is often a screenshot

OCR allows the system to “read” the screenshot.

---

# 8. Image Preprocessing

Before OCR runs, the image is cleaned using OpenCV.

Typical preprocessing includes:
- converting image to grayscale
- thresholding
- denoising
- sharpening
- resizing

This improves OCR accuracy.

Without preprocessing:
- OCR mistakes increase significantly

---

# 9. OCR Extraction

After preprocessing:
- Tesseract extracts raw text from the image

Example:

```text
Amul Taaza Milk ₹32
Bread ₹45
Eggs ₹72
```

This raw OCR text is still messy and unstructured.

---

# 10. Product Parsing

The parser converts messy OCR output into structured products.

Example:

Raw OCR:

```text
amul taza milk 500ml ₹32
```

Parsed object:

```json
{
  "name": "Amul Taaza Milk",
  "quantity": "500ml",
  "price": 32
}
```

The parser uses:
- regex
- string cleanup
- normalization

---

# 11. Why Parsing Is Important

OCR output is inconsistent.

Problems include:
- spelling mistakes
- weird spacing
- broken lines
- incorrect symbols

The parser improves consistency before comparison.

---

# 12. Competitor Data Fetching

The system compares products using live competitor data.

Competitor apps include:
- Blinkit
- Zepto
- Instamart

The application does NOT scrape rendered HTML pages.

Instead:
- it directly calls internal APIs used by the apps themselves

---

# 13. How Competitor APIs Were Discovered

Browser developer tools were used.

Process:
1. open quick-commerce website
2. inspect Network tab
3. search for products manually
4. observe API requests
5. copy API structure
6. recreate requests in Python

This is simpler and faster than browser automation.

---

# 14. Fetching Live Product Data

The backend sends requests using:
- httpx
- async requests

Example:

```python
response = await client.get(api_url)
```

The API typically returns:
- product names
- prices
- stock information
- product IDs

---

# 15. Why Async Requests Are Important

The application may query multiple competitors.

Without async:
- requests happen sequentially
- response time becomes slow

Async requests allow:
- concurrent API calls
- faster user experience

---

# 16. Product Matching Problem

Different apps describe the same product differently.

Example:

```text
Amul Taaza Milk 500ml
```

vs

```text
Amul Fresh Milk 0.5L
```

The system must determine whether these refer to the same item.

---

# 17. Matching Strategy

The application uses:
- RapidFuzz
- fuzzy matching
- token similarity

The goal is not perfect AI-level understanding.

The goal is:
- practical matching
- acceptable accuracy
- fast execution

---

# 18. Why Embeddings Were Avoided

Embeddings and semantic AI systems were intentionally avoided because:
- they add unnecessary complexity
- they require additional infrastructure
- they are excessive for a small personal project

Simple fuzzy matching is sufficient here.

---

# 19. Out-of-Stock Detection

Competitor APIs usually expose stock information.

Examples:

```json
{
  "in_stock": false
}
```

or

```json
{
  "inventory": 0
}
```

The backend converts this into user-friendly labels.

Example:

```text
Out of Stock
```

---

# 20. Price Comparison Logic

After matching products:
- prices are aggregated
- totals are calculated
- savings are computed

Example:

```text
Current Cart Total: ₹420
Zepto Total: ₹391
Savings: ₹29
```

---

# 21. Why No Database Was Used Initially

This project was designed as:
- a short personal project
- not a large-scale platform

Therefore:
- persistence was unnecessary
- databases would increase complexity

The application mainly uses:
- temporary in-memory data structures

---

# 22. Why Redis and PostgreSQL Were Avoided

These technologies are useful at scale.

However:
- they increase setup time
- they increase maintenance
- they are unnecessary for a lightweight demo

The project intentionally prioritizes simplicity.

---

# 23. Why Browser Automation Was Avoided

Tools like:
- Selenium
- Playwright

can automate websites.

However:
- they are slower
- harder to maintain
- more fragile
- unnecessary if APIs are accessible

Direct API usage is cleaner.

---

# 24. Error Sources in the System

Possible inaccuracies include:
- OCR mistakes
- product mismatch
- changing APIs
- regional pricing differences
- stock fluctuations

This is acceptable for the project scope.

---

# 25. What Makes This Project Interesting

This project combines multiple domains:

- OCR
- Computer Vision
- API integration
- Async backend engineering
- Fuzzy matching
- Real-time data fetching
- Full-stack web development

Even though the architecture is simple, the integration itself is powerful.

---

# 26. Important Engineering Philosophy

The project intentionally avoids:
- overengineering
- unnecessary AI complexity
- enterprise architecture
- hype-driven tooling

The focus is:
- practical engineering
- real functionality
- fast iteration
- clean architecture

---

# 27. Final System Summary

The Quick Commerce Cart Comparator is essentially:

```text
OCR + Product Parsing + Live API Fetching + Fuzzy Matching
```

combined into a single workflow.

The application demonstrates:
- backend engineering
- systems integration
- practical problem solving
- API understanding
- asynchronous programming
- full-stack development

without requiring:
- advanced machine learning
- expensive infrastructure
- distributed systems
- large-scale deployment

---

# 28. Final Takeaway

The most important lesson from this project is:

A useful real-world system does not need:
- complex AI
- massive infrastructure
- enterprise tooling

A clean integration of:
- OCR
- APIs
- matching logic
- frontend presentation

is already enough to create a highly practical and impressive application.

