# Borewell & Groundwater Siting Application
## Product Requirements Document (PRD)

**Prepared for:** BSMA Enterprises
**Owner:** Santosh Kumar Bhoda
**Version:** 0.1 (Draft for review)
**Status:** Draft — scope not yet finalized

---

## 1. Overview

A standalone, free-to-use application that helps a landowner or farmer identify the most probable spot(s) on their own plot to drill a productive borewell. The application combines open geospatial and remote-sensing data with a groundwater potential scoring model (AHP and/or machine learning) to generate a ranked set of candidate drilling locations for a user-defined plot, along with guidance on the field verification step needed before actual drilling.

The product is built entirely on open-source software and open/public data, with zero licensing cost, so it can be offered free to end users indefinitely.

---

## 2. Problem Statement

Landowners and farmers — particularly in hard-rock terrain such as Telangana, where groundwater occurs mainly in secondary porosity (fractures, joints, weathered zones) rather than a continuous aquifer — currently site borewells based on local knowledge, water diviners, or trial and error. Failed or low-yield borewells are common, wasting significant money (drilling cost, casing, pump installation) and time. Scientific groundwater prospecting exists (GIS/remote-sensing based groundwater potential mapping) but is typically only accessible to large infrastructure or government projects, not to an individual farmer sizing a single plot.

---

## 3. Goals

### 3.1 Business goals
- Establish BSMA as a visible, credible player in applied GeoAI for public/social good, ahead of commercial engagements.
- Create a distribution channel and data asset (aggregated plot queries, feedback on drilling outcomes) that has future value for adjacent BSMA/Dhineu offerings.
- Build a reference implementation that can later be adapted into a paid B2B/B2G capability (drilling contractors, state groundwater departments, real estate diligence).

### 3.2 Product goals
- Give any landowner a scientifically grounded, ranked recommendation of where to drill on their own plot, in plain language.
- Make the tool free, lightweight, and usable on a basic Android phone with limited connectivity.
- Be transparent about uncertainty — the app narrows down probability, it does not guarantee water.

### 3.3 Success metrics (indicative — to refine once pilot geography is chosen)
- Number of plots queried per month.
- % of users who complete a full plot query (location entered through to seeing a result).
- Correlation between app-recommended zones and actual drilling outcomes reported back by users (requires a feedback loop — see Section 6).
- Cost per query at scale (target: near-zero marginal cost, per the precomputed-tile architecture).

---

## 4. Target Users

- **Primary:** Individual farmers/landowners in the pilot geography deciding where to drill a new borewell.
- **Secondary:** Local borewell drilling contractors who want a lead-qualification/liability-reduction tool.
- **Tertiary (future):** State groundwater/agriculture departments, real estate diligence use cases, NGOs working on rural water access.

---

## 5. Guiding Principles

1. **Free and open** — no proprietary data, no proprietary map/API dependencies, no cost barrier to the end user.
2. **Honest about confidence** — always present results as probability/prospect zones, never as a guarantee, and always recommend field verification (VES resistivity survey) before drilling.
3. **Low-bandwidth first** — designed for rural connectivity and basic smartphones, not urban broadband assumptions.
4. **Local language first** — Telugu/Hindi from day one for the pilot geography, not bolted on later.
5. **Cheap to run at scale** — architecture must not create a recurring server cost that scales with usage (see Section 13).

---

## 6. Full Product Scope (Vision)

This is the complete long-term vision. MVP scope (Section 7) is a deliberate subset of this.

### 6.1 Core capability modules
1. **Plot input** — draw a boundary or drop a pin; optionally enter a survey number where cadastral data is available.
2. **Groundwater potential scoring** — AHP and/or trained ML model over geology, lineaments, geomorphology, drainage, slope, LULC, soil, rainfall recharge, and existing well data.
3. **Ranked candidate output** — top 1–3 recommended points within the plot, with a probability heatmap overlay.
4. **Regulatory check** — cross-reference candidate points against state groundwater stress/category maps and minimum-distance-from-existing-well rules (e.g. WALTA in Telangana) so the app never recommends an administratively restricted spot.
5. **Field verification guidance** — plain-language explanation of VES/resistivity survey as the confirming step, with option to request a local geophysical survey provider.
6. **Contractor connect** — optional directory/marketplace of local drilling contractors and geophysical survey providers.
7. **Outcome feedback loop** — users report actual drilling depth/yield after drilling; this data feeds back into retraining the ML model, improving accuracy over time and creating a growing proprietary ground-truth dataset.
8. **Multi-state coverage** — expand beyond the pilot state, with per-state calibration since hydrogeology varies (hard rock vs. alluvial/sedimentary terrain needs different weighting).
9. **Multi-language support** — beyond Telugu/Hindi, add other regional languages as coverage expands.
10. **API access** — expose the groundwater-prospect layer as an API/data layer for third-party use (e.g. real estate platforms doing land diligence, agri-fintech underwriting).
11. **Analytics dashboard** — aggregate, anonymized view for government/NGO partners on prospect zones and query density, useful for planning.
12. **Seasonal recalibration** — periodic reprocessing as CGWB water-level and rainfall data update, so prospect maps reflect current-year conditions, not a static one-time snapshot.

### 6.2 Full feature list

| Module | Feature |
|---|---|
| Onboarding | Language selection, simple guided first-use walkthrough |
| Plot input | Pin drop, boundary draw, survey-number lookup (where cadastral data available) |
| Scoring | AHP model (v1), ML model trained on CGWB well yield (v2), continuous retraining from feedback (v3) |
| Output | Probability heatmap, ranked top-3 points, estimated depth range, confidence indicator |
| Regulatory | WALTA/groundwater-category cross-check, minimum-distance-to-existing-well flag |
| Verification | VES survey explainer, request-a-survey option, provider directory |
| Contractor marketplace | Provider listings, ratings, contact/request flow |
| Feedback loop | Post-drilling outcome form (depth, yield, success/failure), tied back to model retraining |
| Offline support | Cached map tiles and last query result available without connectivity |
| Multi-state expansion | Per-state data pipelines and model calibration |
| API | Public read-only API for the groundwater-prospect layer |
| Admin/analytics | Internal dashboard for query volume, geographic coverage, model performance tracking |

---

## 7. MVP Scope

The MVP is intentionally narrow: one geography, one language pair, static precomputed output, no marketplace, no API.

### 7.1 MVP feature list
- Plot input via pin drop or simple boundary draw.
- Precomputed groundwater potential raster for the pilot geography (built offline via the AHP/ML pipeline — see Section 12).
- On-device/client-side lookup against the precomputed raster (no live server-side compute per query).
- Output: probability heatmap for the plot + top 3 candidate points, in plain language.
- A clear, non-dismissible note recommending a VES resistivity survey before drilling, with a short explainer of what that is.
- Basic WALTA/groundwater-category flag if the plot falls in a regulated/over-exploited zone (static overlay, not live regulatory data).
- Telugu and Hindi language support alongside English.
- Works as a PWA — installable on Android, functional on low bandwidth, caches the last-viewed area for offline reference.

### 7.2 MVP geography
- Single pilot state (Telangana recommended) or a smaller pilot district within it if faster validation against known CGWB well records is preferred.

### 7.3 Explicitly out of scope for MVP
- Contractor/geophysical-survey marketplace.
- User accounts, login, or profile management.
- Outcome feedback loop and model retraining pipeline (planned for v2 once there's a real user base to collect from).
- Public API.
- Multi-state coverage.
- Live/dynamic (on-demand) scoring for arbitrary plots outside the precomputed extent.
- Analytics dashboard for external partners.

---

## 8. User Flow (MVP)

1. User opens the app, selects language (Telugu / Hindi / English).
2. User is shown a map centered on their approximate location (device GPS) or can search/pan manually.
3. User drops a pin or draws a rough boundary for their plot.
4. App looks up the precomputed groundwater potential raster for that location.
5. App displays: a probability heatmap over the plot, the top 3 candidate points marked, and a plain-language summary ("This area shows moderate to high groundwater potential due to nearby fracture zones").
6. App shows the regulatory flag if relevant ("This area falls in a groundwater-stressed zone — additional permission may be required").
7. App shows the VES verification note with a short explainer and, optionally, a way to note interest in a survey (email/WhatsApp capture only in MVP — no live marketplace).
8. User can save/screenshot the result; last-viewed result is cached for offline access.

---

## 9. Functional Requirements

### 9.1 Data ingestion & processing (offline, batch — not part of the live app)
- Ingest and reproject all open datasets (Section 11) to a common CRS and resolution for the pilot geography.
- Derive drainage density, slope, and flow accumulation from DEM.
- Derive/ingest lineament density.
- Normalize each thematic layer to a common scale (e.g. 1–5) for AHP weighting, or assemble a feature stack for the ML model.
- Calibrate weights (AHP) or train the model (ML) against CGWB well yield ground-truth records for the pilot geography.
- Produce the final groundwater potential raster and export as cloud-optimized GeoTIFF, then pre-tile it.

### 9.2 Scoring engine
- v1 (MVP): weighted overlay (AHP) — transparent, explainable, no training data dependency beyond CGWB validation.
- v2 (post-MVP): trained ML model (Random Forest/XGBoost) once enough labeled well outcomes exist, either from CGWB records or the app's own feedback loop.

### 9.3 Application (frontend)
- Map rendering via MapLibre GL JS with OpenStreetMap base tiles.
- Plot input: pin and polygon draw tools.
- Result rendering: heatmap overlay + marker pins for top candidates.
- Language switch (Telugu/Hindi/English) with all user-facing strings externalized for translation.
- Offline caching of visited map tiles and last query result (PWA service worker).

### 9.4 Output/report
- On-screen summary in plain language, not just a raw score.
- Downloadable/shareable summary (image or simple PDF) for the user to keep or share with a drilling contractor.

---

## 10. Non-Functional Requirements

- **Cost:** Marginal server cost per query must be at or near zero (see precomputed-tile architecture, Section 13).
- **Performance:** Result should appear in under 2 seconds on a typical rural 3G/4G connection once the app shell is cached.
- **Accessibility:** Usable by a non-technical user with basic literacy; plain-language output, minimal jargon, iconography where possible.
- **Offline resilience:** Core app shell and last-used area must work without connectivity.
- **Data licensing:** Every dataset used must be open/free for this use case — no dataset should be adopted without confirming its license permits redistribution of derived outputs.
- **Transparency:** The app must always disclose that results are probabilistic and recommend field verification — this is a product integrity requirement, not just a legal disclaimer.

---

## 11. Data Sources

| Layer | Source | Coverage/resolution | Access |
|---|---|---|---|
| Geology/lithology | GSI Bhukosh | India, vector geology maps | Free download |
| DEM (slope, drainage) | SRTM 30m (USGS) or Cartosat-1 (Bhuvan) | India, 10–30m | Free |
| Lineaments/fractures | Derived from DEM (WhiteboxTools) or Bhuvan geomorphology layer | India | Free |
| Land use/land cover | ESA WorldCover or Bhuvan LULC | 10m global / India | Free |
| Soil | SoilGrids (ISRIC) | 250m global | Free |
| Rainfall | IMD gridded (0.25°) or CHIRPS | India / global | Free for research use |
| Existing well data (ground truth) | India-WRIS, CGWB dynamic groundwater resource reports | State/district | Free download |
| Groundwater stress category | CGWB category maps | State/district | Free |
| Base map/roads/villages | OpenStreetMap | Global | Free, open license |

---

## 12. Technology Stack

| Layer | Tool | Notes |
|---|---|---|
| GIS processing/ETL | GDAL, GRASS GIS, WhiteboxTools | WhiteboxTools automates lineament/stream extraction |
| Spatial database | PostgreSQL + PostGIS | Free, handles raster + vector |
| Scoring engine | AHP (v1) / scikit-learn or XGBoost (v2) | Python |
| Backend API (if/when needed) | FastAPI | Lightweight, async |
| Raster tile serving | Pre-tiled static tiles (MVP); TiTiler or GeoServer if dynamic serving is added later | Static tiles keep hosting cost near zero |
| Map frontend | MapLibre GL JS + OpenStreetMap tiles | No proprietary map API cost |
| App delivery | Progressive Web App (PWA) | Installable on Android, offline-capable, no app-store dependency |
| Hosting | Static hosting (e.g. Cloudflare Pages) for tiles/app shell; low-cost/free-tier server only if dynamic features are added later | Keeps recurring cost near zero for MVP |

---

## 13. System Architecture

**MVP architecture (precomputed, near-zero marginal cost):**

1. Offline batch job (run once per season/update cycle): ingest all open datasets for the pilot geography → GDAL/GRASS/WhiteboxTools processing → AHP scoring → groundwater potential raster → pre-tiled static tiles.
2. Static hosting serves the app shell (PWA) and the pre-tiled raster.
3. Client-side app performs the lookup against the static tiles for whatever plot the user selects — no server compute per query.
4. Periodic (e.g. seasonal) re-run of the batch job as CGWB water-level and rainfall data update.

**Post-MVP evolution (if dynamic/on-demand scoring is needed):** introduce the FastAPI backend and PostGIS database so arbitrary plots (including areas needing finer recalculation, or user-submitted soil data) can be scored live, and to support the contractor marketplace, feedback loop, and API access described in the full scope.

---

## 14. Regulatory & Compliance Considerations

- Telangana groundwater extraction is regulated under WALTA (Water, Land and Trees Act) — candidate points should be checked against groundwater-stress category maps and minimum-distance-from-existing-well rules so the app doesn't recommend an administratively restricted location.
- Any dataset used must be confirmed as licensed for this redistribution/derivative use before inclusion — to be verified per source at build time, not assumed from this document.
- No personal data collection is required for the MVP (no login); if the outcome feedback loop is added later, a lightweight privacy policy will be needed for whatever contact information is collected.

---

## 15. Risks & Assumptions

| Risk/assumption | Notes |
|---|---|
| GIS/RS-based scoring gives probability, not certainty | Mitigated by always recommending VES field verification before drilling |
| Open dataset quality/currency varies by district | Pilot geography should be chosen partly based on data quality, not just market interest |
| Farmer smartphone/connectivity constraints | Addressed via PWA + offline caching + lightweight tile design |
| Model accuracy depends on enough ground-truth well data | MVP uses AHP (expert-weighted, no training data dependency); ML upgrade depends on collecting real outcomes |
| Regulatory overlay is only as current as the last update cycle | Static overlay in MVP; note in-app that users should confirm current status with local authorities |

---

## 16. Roadmap / Phasing

- **Phase 0 — MVP:** Single pilot geography, AHP scoring, precomputed static tiles, PWA, Telugu/Hindi/English, VES guidance, WALTA flag.
- **Phase 1:** Outcome feedback loop, begin collecting real drilling results.
- **Phase 2:** ML scoring model trained on collected feedback + CGWB data; expand to additional districts/states.
- **Phase 3:** Contractor/geophysical-survey marketplace; public API; analytics dashboard for government/NGO partners.

---

## 17. Open Questions

- Final pilot geography: full state (Telangana) or a smaller pilot district first?
- Product name/branding.
- Whether "free" extends indefinitely to all future features, or only to the core MVP siting functionality (marketplace/contractor-connect could carry a commission model later without breaking the free core promise).
- Hosting owner/budget line — even near-zero cost architecture needs a nominal owner for domain, storage, and periodic batch-job compute.
