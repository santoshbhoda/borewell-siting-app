# Production Deployment Guide: Supabase / Neon + Render

This guide details the exact steps to deploy the **BSMA GeoAI Borewell & Groundwater Siting Platform** to managed production cloud infrastructure.

---

## Architecture Overview

```mermaid
flowchart LR
    PWA["Static Web PWA (Cloudflare Pages / Render Static Site)"]
    API["FastAPI Microservice (Render Web Service)"]
    DB[("Managed PostgreSQL + PostGIS (Supabase / Neon - Mumbai Region)")]

    PWA -->|REST / GeoJSON API| API
    API -->|Spatial SQL & ORM| DB
```

---

## Step 1: Provision Managed PostGIS Database (Supabase or Neon)

### Option A: Supabase (Recommended)
1. Log in to [Supabase](https://supabase.com) and click **New Project**.
2. Project Name: `bsma-borewell-db`
3. Region: Select **South Asia (Mumbai - ap-south-1)** for lowest latency to Telangana / India.
4. Set a strong Database Password (save it securely).
5. Open the **SQL Editor** tab on the left sidebar and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
6. Go to **Project Settings** \(\rightarrow\) **Database** \(\rightarrow\) **Connection String** \(\rightarrow\) **URI**.
7. Copy the connection string (format):
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```

### Option B: Neon (Serverless Postgres)
1. Log in to [Neon Console](https://console.neon.tech) and create a project named `bsma-borewell`.
2. Region: **AWS ap-south-1 (Mumbai)**.
3. In the SQL Editor, run: `CREATE EXTENSION IF NOT EXISTS postgis;`
4. Copy the connection string:
   ```
   postgresql://[USER]:[PASSWORD]@[ENDPOINT].ap-south-1.aws.neon.tech/neondb?sslmode=require
   ```

---

## Step 2: Push Repository to GitHub

Open a terminal in `c:\BSMA\Borewell`:

```bash
# Set default branch to main
git branch -M main

# Add your GitHub repository remote
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/borewell-siting-app.git

# Push code to GitHub
git push -u origin main
```

---

## Step 3: Deploy FastAPI Backend on Render

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** (top right) \(\rightarrow\) **Blueprint**.
3. Connect your GitHub repository (`borewell-siting-app`).
4. Render will read `render.yaml` and configure the web service `bsma-borewell-api`.
5. Under **Environment Variables**, set:
   * **`DATABASE_URL`**: Paste your Supabase or Neon connection string from Step 1.
   * **`DEBUG`**: `False`
6. Click **Apply**.
7. Render will automatically:
   - Build using Python 3.12.
   - Install dependencies from `requirements.txt`.
   - Run `python -m backend.init_db` to create all PostGIS tables (`land_plots`, `candidate_spots`, `drilling_outcomes`, `service_providers`).
   - Start Uvicorn at `https://bsma-borewell-api.onrender.com`.

---

## Step 4: Deploy Web Frontend (PWA)

### Option A: Render Static Site (1-Click)
1. On Render, click **New +** \(\rightarrow\) **Static Site**.
2. Connect your GitHub repository.
3. Configure:
   * **Name**: `bsma-borewell-web`
   * **Publish Directory**: `web`
   * **Build Command**: *(Leave empty)*
4. Click **Create Static Site**.

### Option B: Cloudflare Pages (Free Global CDN with Edge Caching)
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com) \(\rightarrow\) **Workers & Pages** \(\rightarrow\) **Create Application** \(\rightarrow\) **Pages**.
2. Connect your GitHub repo.
3. Build Configuration:
   * **Framework preset**: *None*
   * **Build output directory**: `web`
4. Click **Save and Deploy**.

---

## Step 5: Post-Deployment Verification

1. **Verify Health Endpoint**:
   ```bash
   curl https://<YOUR_RENDER_APP>.onrender.com/health
   ```
   *Expected Response:*
   ```json
   {"status":"healthy","service":"BSMA GeoAI Borewell Siting Platform API","pilot_region":"Yadadri-Bhuvanagiri / Musi Basin (Telangana)","version":"1.0.0"}
   ```

2. **Open Interactive API Documentation**:
   Visit `https://<YOUR_RENDER_APP>.onrender.com/docs` to test endpoints via Swagger UI.

3. **Verify Database Seeding**:
   Open Supabase / Neon Table Editor and verify that `land_plots`, `candidate_spots`, `drilling_outcomes`, and `service_providers` have been populated with pilot data.
