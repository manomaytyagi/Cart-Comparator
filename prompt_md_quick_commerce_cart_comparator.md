# prompt.md

# Project Title
Quick Commerce Cart Price Comparator

---

# Project Goal

Build a lightweight but powerful personal-use web application that:

1. Takes a screenshot of a cart from a quick-commerce app
2. Extracts the cart items using OCR
3. Fetches live prices from competitor apps
4. Compares totals and item-level prices
5. Detects out-of-stock items
6. Shows potential savings

The project is intended for:
- personal use
- friends and family
- portfolio/project showcase

This is NOT intended to be:
- a startup-scale platform
- a highly scalable distributed system
- a production SaaS product

The project should prioritize:
- simplicity
- speed of development
- real functionality
- clean engineering
- practical integration
- polished UX

---

# Core Functional Requirements

The application should support the following workflow:

```text
Upload screenshot
→ OCR extraction
→ Product parsing
→ Competitor product lookup
→ Product matching
→ Price comparison
→ Savings calculation
```

---

# Input

Input will be:
- screenshot images of carts from quick commerce apps

Initially optimize for:
- one source app only
- predictable screenshot layouts
- screenshots taken on the developer’s own device

The system does NOT need to support:
- every screenshot format
- every device resolution
- every UI variation

---

# Output

The application should display:

- extracted product names
- current cart prices
- competitor prices
- out-of-stock status
- cheapest alternatives
- total savings

Example:

```text
Amul Taaza Milk
Current App: ₹32
Zepto: ₹30

Bread
Current App: ₹45
Zepto: Out of Stock

Total:
Current App: ₹420
Zepto: ₹391

Savings: ₹29
```

---

# Scope Constraints

This project is intentionally constrained.

The goal is:
- short development cycle
- working end-to-end demo
- high practical impact
- low infrastructure complexity

Avoid:
- overengineering
- unnecessary AI
- premature scalability
- distributed systems
- microservices

---

# Time Constraints

The project is designed around approximately:

```text
10 focused hours over 2 days
```

This means:
- shortcuts are acceptable
- assumptions are acceptable
- hardcoded logic is acceptable where useful
- generalized architecture is NOT required

---

# Technical Philosophy

The project should:
- solve a real problem
- work reliably enough for personal use
- use minimal dependencies
- avoid unnecessary complexity
- maximize practical functionality

The project should NOT:
- chase AI hype
- use technologies only for resume buzzwords
- attempt perfect OCR or perfect matching
- attempt enterprise-grade scalability

---

# Preferred Tech Stack

## Frontend
- Next.js
- Tailwind CSS

Reason:
- fast development
- modern UI
- easy deployment
- clean UX

---

## Backend
- FastAPI
- Python

Reason:
- existing familiarity
- async support
- rapid development

---

# OCR Stack

Use:
- Tesseract OCR
- OpenCV preprocessing
- pytesseract

Preprocessing may include:
- grayscale conversion
- thresholding
- denoising
- sharpening

Do NOT use:
- expensive AI OCR APIs initially
- custom OCR models
- deep learning OCR pipelines

Optional future upgrade:
- Google Vision API if OCR quality becomes unacceptable

---

# Product Matching Strategy

Use:
- RapidFuzz
- fuzzy matching
- simple normalization
- regex cleanup

Avoid:
- embeddings
- vector databases
- semantic search systems
- LLM-based matching

The matching only needs to be:
- reasonably accurate
- practical for common grocery items

---

# Competitor Data Strategy

Preferred approach:
- discover internal APIs manually
- use browser devtools/network inspection
- recreate requests using Python httpx

Avoid:
- Selenium initially
- full browser automation
- complicated scraping systems
- anti-bot bypass engineering

Browser automation tools like Playwright may be used ONLY if necessary.

---

# Data Storage

Initially use:
- in-memory Python dictionaries/lists

Avoid:
- PostgreSQL initially
- Redis initially
- cloud infrastructure initially

Persistence is not important for the MVP.

---

# Real-Time Requirements

The application should:
- fetch reasonably fresh prices
- detect out-of-stock products
- support near real-time comparison

However:
- true real-time infrastructure is unnecessary
- slight delays are acceptable
- short-term caching is acceptable

---

# UX Requirements

The UI should be:
- clean
- fast
- minimal
- modern

Important UI components:
- screenshot upload
- loading indicator
- comparison table
- savings summary

Avoid:
- overly complex dashboards
- analytics systems
- excessive animations

---

# Features Explicitly OUT OF SCOPE

Do NOT build:

- authentication systems
- payment systems
- recommendation engines
- AI assistants/chatbots
- notification systems
- mobile apps
- distributed architecture
- microservices
- Kubernetes
- Docker orchestration
- vector databases
- embeddings infrastructure
- semantic AI pipelines
- recommendation ML models

---

# Suggested Project Structure

```text
app/
 ├── main.py
 ├── ocr.py
 ├── compare.py
 ├── fetchers.py
 ├── parser.py
 └── frontend/
```

---

# Recommended Development Priority

1. FastAPI setup
2. OCR extraction
3. Product parsing
4. Competitor API discovery
5. Live product fetching
6. Product matching
7. Comparison engine
8. Frontend polish

---

# Definition of Success

The project is successful if it can:

1. Accept a screenshot
2. Extract products reasonably accurately
3. Fetch live competitor prices
4. Detect out-of-stock items
5. Calculate savings
6. Display results in a polished UI

Even if:
- OCR is imperfect
- matching is not universal
- APIs are somewhat brittle
- assumptions are hardcoded

That is acceptable for this project.

---

# Overall Goal

Build:
- a compact
- practical
- impressive
- real-world
- end-to-end engineering project

without:
- unnecessary complexity
- excessive AI infrastructure
- enterprise-scale architecture

