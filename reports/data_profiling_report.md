# Data Profiling & Quality Audit Report

**Generated during Level 4: Data Processing Pipeline**

---

## 1. Reviews Dataset Profile

* **Total Reviews Analysed:** 7,991
* **Date Range:** 2002-12-08 06:52:21 to 2023-03-16 18:19:42
* **Exact Duplicate Records:** 0
* **Potential Key Duplicates (Product + User + Timestamp):** 0
* **Invalid Star Ratings (< 1.0 or > 5.0):** 0

### Star Rating Distribution

| Star Rating | Review Count | Percentage |
| :--- | :--- | :--- |
| **5.0 Stars** | 5,452 | 68.23% |
| **4.0 Stars** | 1,085 | 13.58% |
| **3.0 Stars** | 525 | 6.57% |
| **2.0 Stars** | 316 | 3.95% |
| **1.0 Stars** | 613 | 7.67% |

### Verified Purchase Status

* **Verified Purchases:** 6,173 (77.25%)
* **Non-Verified Purchases:** 1,818 (22.75%)

### Review Text Length Distribution (Characters)

* **Minimum Length:** 1 chars
* **Maximum Length:** 10,189 chars
* **Mean Length:** 373.55 chars
* **Median Length:** 189.00 chars
* **25th Percentile:** 70.00 chars
* **75th Percentile:** 426.00 chars

---

## 2. Product Catalog Profile

* **Total Products Analysed:** 5,027
* **Duplicate Product IDs:** 0
* **Missing Product Names:** 0
* **Missing Listing Prices:** 1,415
* **Invalid Negative Prices (< $0.00):** 0
* **Zero Prices ($0.00):** 0
* **Missing or 'Unknown' Brands:** 8
* **Missing Categories:** 0
* **Catalog Average Rating Range:** 1.0 to 5.0 (Mean: 4.33)

---

## 3. Data Quality Findings Summary

1. **Zero Corrupted Ratings:** All 7,991 customer ratings are valid numerical values strictly bounded between 1.0 and 5.0.
2. **Referential Integrity:** 100% of review `product_id` references exist in the catalog.
3. **Price Null Integrity:** 1,415 products lack listing prices from the raw source; these are preserved as explicit `NULL`s and not artificially filled with zero.
4. **Text Integrity:** Real customer inputs, including short expressions (e.g. 'N/A') and dense reviews up to 10,189 characters, are preserved.
