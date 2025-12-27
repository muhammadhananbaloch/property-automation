# Property Automation Engine (PropAuto)

## 📖 Overview

**PropAuto** is a full-stack real estate lead generation platform designed to automate the discovery, enrichment, and management of off-market property leads.

Unlike standard scraping tools, PropAuto implements a cost-efficient **"Scout & Harvest" methodology**. It interacts with the **PropertyRadar API** to first identify potential leads based on specific investment criteria (Pre-Foreclosure, Tax Delinquent, etc.) without incurring costs, and then selectively "buys" (enriches) high-value targets to retrieve contact information (skip tracing), financial equity data, and owner demographics.

## 🚀 Key Features

### 1. "Scout & Harvest" Workflow

* **Scout (Scan):** Users can scan entire cities (e.g., Richmond, VA) for specific distressed property signals (e.g., Pre-Foreclosure). The system returns the *count* of available leads without spending API credits.
* **Harvest (Enrich):** Users utilize a slider to select a specific quantity of leads to purchase (e.g., "Buy 10 leads"). The system dynamically creates lists in PropertyRadar, triggers automation to fetch phone/email data, and downloads the enriched data to the local database.

### 2. Interactive Dashboard

* **Real-time Stats:** Immediate feedback on "New Leads" vs. "Already Owned" leads in the target area.
* **Data Visualization:** Detailed tables showing Property Equity, Estimated Value, Bed/Bath counts, and Owner details.
* **Smart Filtering:** Automatically hides leads already existing in the database to prevent duplicate spending.

### 3. Data Management & Export

* **CSV Export:** One-click export of selected leads for use in dialers or CRM tools.
* **Historical Archives:** Full history of every scan performed, allowing users to revisit past datasets without re-querying the API.
* **Safety Net Storage:** Stores the raw JSON response from providers in the database to ensure no data point is ever lost, even if not currently displayed in the UI.

### 4. Robust Architecture

* **Containerized:** Fully Dockerized environment (Frontend, Backend, Database) for one-command deployment.
* **Scalable Backend:** Built with FastAPI and SQLAlchemy, designed to handle thousands of records asynchronously.

---

## 🛠 Tech Stack

### **Frontend**

* **Framework:** React (Vite)
* **Styling:** Tailwind CSS (Custom "Premium" UI components)
* **State Management:** React Hooks
* **Icons:** Lucide React

### **Backend**

* **Framework:** FastAPI (Python 3.11)
* **Database:** PostgreSQL 15
* **ORM:** SQLAlchemy
* **API Integration:** PropertyRadar (Custom Service Layer)

### **Infrastructure**

* **Docker & Docker Compose:** Orchestration of web, api, and db services.
* **Adminer:** Lightweight database management GUI.

---

## 🏗 Architecture & Methodology

The application follows a **Domain-Driven Design (DDD)** approach to separate business logic from API routes.

### **The "Scout" Logic**

1. **Criteria Mapping:** The frontend sends a human-readable request (e.g., `State: VA, City: Richmond, Strategy: Pre-Foreclosure`).
2. **Translation:** The `CriteriaMapper` converts this into the complex JSON payload required by the PropertyRadar API.
3. **Execution:** The backend queries the provider for a *count* only. This ensures the user knows the market size before spending money.

### **The "Enrich" Logic**

1. **Dynamic List Creation:** When a user clicks "Buy", the system creates a temporary dynamic list in PropertyRadar.
2. **Automation Trigger:** It attaches an automation rule to this list to purchase Phone & Email data immediately upon lead entry.
3. **Harvesting:** The system retrieves the enriched profiles and saves them to the local PostgreSQL database, mapping them to the `Lead` model.

---

## 📂 Project Structure

```bash
property-automation/
├── app/
│   ├── api/            # API Routes (Endpoints)
│   │   └── routes/     # Search, History, etc.
│   ├── core/           # Configuration & Criteria Mappers
│   ├── database/       # DB Connection & SQLAlchemy Models
│   ├── domain/         # Business Logic (The "Brain")
│   ├── services/       # External API Clients (PropertyRadar, SMS)
│   └── main.py         # App Entry Point
├── frontend/
│   ├── src/
│   │   ├── components/ # Reusable UI (Cards, Tables, Buttons)
│   │   ├── pages/      # Dashboard, History, Campaigns
│   │   └── services/   # Frontend API connectors
├── docker-compose.yml  # Infrastructure definition
└── requirements.txt    # Python dependencies

```

---

## ⚡ Getting Started

### Prerequisites

* Docker & Docker Compose installed.
* A PropertyRadar API Token.

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-repo/property-automation.git
cd property-automation

```


2. **Configure Environment:**
Create a `.env` file in the root directory:
```env
PROPERTY_RADAR_API_TOKEN=your_token_here
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=property_db
DB_HOST=127.0.0.1
DB_PORT=5435

```


3. **Launch the System:**
```bash
docker-compose up --build

```


4. **Access the App:**
* **Frontend Dashboard:** `http://localhost:5173`
* **Backend Documentation:** `http://localhost:9999/docs`
* **Database Viewer (Adminer):** `http://localhost:8080`



---

## 🗺 Roadmap & Future Features

This project was built with modularity in mind. The following features are planned for future phases:

* **campaigns (SMS Marketing):**
* *Current Status:* The UI shell exists (`Campaigns.jsx`), and the database schema (`MessageLog`) is ready.
* *Implementation Plan:* Integrate Twilio or similar SMS gateway to enable one-click text blasts to harvested leads directly from the dashboard.


* **Skip Tracing 2.0:**
* Integrate secondary data providers (e.g., SkipGenie) for tiered data verification if primary phone numbers are disconnected.


* **CRM Integration:**
* Add Webhooks to automatically push "Purchased" leads to external CRMs like HubSpot or Salesforce.



---

## 📄 Database Schema

* **Leads:** Stores core property data (Address, Equity, Value) and contact info (JSON fields for multiple Phones/Emails).
* **SearchHistory:** Logs every scan criteria and timestamp.
* **SearchResults:** Junction table linking specific searches to the leads found (Many-to-Many).

---

## 📜 License

This project is proprietary software. Unauthorized copying or distribution is strictly prohibited.
