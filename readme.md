Name:J.Prathyusha

PRN : 250200038

Section: 7



# 🎓 Sai University Research Intelligence Dashboard

## 📌 Project Overview

The **Sai University Research Intelligence Dashboard** is an interactive research analytics application built using **Python and Streamlit**.

The dashboard transforms Sai University's publication data into an interactive analytics platform that helps users explore:

* Research output
* Publication trends
* School-wise contribution
* Faculty publication activity
* Publication quality
* Indexing status
* SJR quartiles
* Sustainable Development Goals (SDGs)
* Publication details and links

The publication records are retrieved **dynamically from the Sai University Publications API**, rather than being manually entered.

---

## 🎯 Project Objective

The objective of this project is to transform raw publication data into a research intelligence system using the following workflow:

```text
Publications API
       ↓
     Python
       ↓
     Pandas
       ↓
Data Cleaning & Processing
       ↓
Data Analysis
       ↓
Matplotlib / Seaborn
       ↓
   Streamlit UI
       ↓
Interactive Research Dashboard
       ↓
Generate Research Insights
```

---

## 🌐 Data Source

The dashboard uses the Sai University Publications API:

**Publications API**

https://sai-publications-dashboard.vercel.app/api/publications

The data is fetched dynamically when the application runs.

---

## 🛠️ Technologies Used

* **Python** – Application development and data processing
* **Pandas** – Data cleaning, transformation and analysis
* **Streamlit** – Interactive dashboard development
* **Matplotlib** – Statistical visualizations
* **Seaborn** – Attractive data visualizations
* **Requests** – REST API data retrieval
* **REST API / JSON** – Dynamic publication data source

---

# 📊 Dashboard Features

## 1. KPI Section

The dashboard provides dynamically calculated research KPIs.

The KPIs respond to the selected filters.

### KPIs include:

* 📚 Total Publications
* 🔎 Scopus Indexed Publications
* 🌐 Web of Science Indexed Publications
* ⭐ Q1 Publications
* 🏫 Number of Schools
* 👩‍🏫 Number of Faculty Authors
* 🌍 Number of SDGs Represented
* 📅 Latest Publication Year

---

# 📈 Interactive Visualizations

The dashboard contains meaningful visualizations for understanding the university's research ecosystem.

### Publication Trends

Shows how publication output changes over time.

### Publications by School

Shows the contribution of different schools to university research output.

### Document Type Distribution

Shows the distribution of publication types.

### Indexing Status

Shows publication indexing information such as Scopus and Web of Science.

### SJR Quartile Distribution

Shows the distribution of publications across:

* Q1
* Q2
* Q3
* Q4

### Faculty / Author Contribution

Shows publication activity associated with Sai University faculty authors.

### SDG Distribution

Shows how university publications are represented across the Sustainable Development Goals.

---

# 🎛️ Interactive Filters

The dashboard provides interactive filtering.

Available filters include:

* 📅 Year
* 🏫 School
* 👩‍🏫 Faculty Author
* 📄 Document Type
* 🔎 Indexing Status
* ⭐ SJR Quartile
* 🏢 Publisher
* 📰 Publisher / Source
* 🌍 SDG

All major dashboard components respond to the selected filters.

This allows users to investigate specific areas of the university's research activity.

---

# 📊 Year-over-Year Analysis

The dashboard includes year-over-year analysis to help examine changes in publication output between consecutive years.

The analysis displays:

* Publication count
* Previous-year publication count
* Change in publication count
* Percentage change

---

# 💡 Automatic Research Insights

The dashboard automatically generates research insights based on the currently selected data.

Examples include:

* School with the highest publication activity
* Faculty contribution
* Most represented SJR quartile
* Most represented SDG

These insights change according to the active filters.

---

# 🔍 Publication Explorer

The Publication Explorer provides access to the underlying publication records.

Users can:

* Search publications
* Search authors
* Search schools
* Search publishers
* Search keywords
* Sort publication records
* View publication details
* Access DOI links
* Access article links
* Access journal links

---

# ⬇️ Data Export

The dashboard provides a CSV export option.

Users can download the currently filtered publication records for further analysis.

The exported data reflects the filters currently selected in the dashboard.

---

# 🌙 Dark Mode

The dashboard includes a dark mode interface for improved viewing and presentation.

The interface is designed to provide a clear and modern research analytics experience.

---

# 🧹 Data Cleaning

The application performs data preparation before analysis.

The processing includes:

* Cleaning column names
* Handling missing values
* Converting publication years into numeric values
* Processing text fields
* Handling incomplete publication information
* Extracting SDG information
* Identifying faculty authors
* Preparing categorical fields for analysis

Missing or incomplete values are handled without manually creating publication records.

---

# 📋 Publication Fields

The API provides publication information including fields such as:

* Authors
* SaiU Authors
* School
* SaiU Author Email
* Designation
* Title
* Year
* Publication Date
* Source Title
* Volume
* Issue
* Page information
* SJR Quartile
* Year Wise Quartile
* DOI
* DOI Link
* Article Link
* Journal Link
* Abstract
* Keywords
* Publisher
* Document Type
* Indexing Status
* Achieved SDG
* SaiU SDG Indexing
* Scopus URL
* Web of Science URL

---

# 🚀 How to Run the Project

## Step 1: Clone the Repository

Clone this repository to your computer.

```bash
git clone https://github.com/jampaniprathyusha12-creator/sai-research-intelligence-dashboard
```

Then enter the project directory:

```bash
cd sai-research-intelligence-dashboard
```

---

## Step 2: Install Required Libraries

Install the dependencies using:

```bash
pip install -r requirements.txt
```

---

## Step 3: Run the Streamlit Application

Run:

```bash
streamlit run app.py
```

The application will open in the browser.

Usually the local address is:

```text
http://localhost:8501
```

---

# 📁 Project Structure

```text
sai-research-intelligence-dashboard/
│
├── app.py
│
├── requirements.txt
│
└── README.md
```

### `app.py`

Contains the complete Streamlit dashboard application, including:

* API connection
* Data cleaning
* Data analysis
* KPI calculations
* Filters
* Visualizations
* Publication Explorer
* Export functionality
* Automatic insights
* Dark mode

### `requirements.txt`

Contains the Python libraries required to run the application.

### `README.md`

Contains project documentation and instructions.

---

# 🔄 Data Flow

```text
Sai University Publications API
              ↓
        REST API Request
              ↓
          JSON Data
              ↓
        Pandas DataFrame
              ↓
       Data Cleaning
              ↓
       Data Processing
              ↓
          Filtering
              ↓
          Analysis
              ↓
    Matplotlib / Seaborn
              ↓
       Streamlit Dashboard
              ↓
       Interactive Insights
```

---

# 🎓 Questions the Dashboard Helps Answer

The dashboard is designed to help users investigate questions such as:

### Research Output

* How has research output changed over time?
* Which years have higher publication activity?

### Schools

* Which schools contribute to publication output?
* How does school contribution change after applying filters?

### Publication Quality

* What is the distribution of SJR quartiles?
* How many publications are Q1?

### Indexing

* How many publications are indexed in Scopus?
* How many are indexed in Web of Science?

### Faculty

* Which faculty authors have publication activity?
* How does author contribution change with filtering?

### SDGs

* Which SDGs are represented in university research?
* How does SDG representation change across different selections?

### Publications

* Which publications match a particular search?
* What DOI, article or journal links are available?

---

# ⭐ Bonus Features Implemented

The project includes several additional features beyond the core requirements:

* ✅ Year-over-Year Analysis
* ✅ Automatic Research Insights
* ✅ Advanced Publication Search
* ✅ Publication Sorting
* ✅ CSV Export
* ✅ Responsive Dashboard Layout
* ✅ Dark Mode
* ✅ Interactive Drill-Down Through Filters
* ✅ Dynamic API Data
* ✅ DOI / Article / Journal Links

---

# 📌 Important Data Accuracy Principle

The dashboard does **not manually create publication records**.

Publication records are retrieved from the Sai University Publications API and then cleaned and analysed using Python and Pandas.

This ensures that the dashboard reflects the available API data and avoids manually entering or inventing publication records.

---

# 👩‍💻 Project Information

**Project:** Sai University Research Intelligence Dashboard

**Domain:** Research Analytics / Data Visualization

**Platform:** Streamlit

**Language:** Python

**Data Source:** Sai University Publications API

---

# 📜 Conclusion

The Sai University Research Intelligence Dashboard converts publication data into an interactive research analytics platform.

It combines:

```text
Data
  +
Analysis
  +
Visualization
  +
Interaction
  +
User Experience
  =
Research Intelligence
```

The dashboard enables university leadership, faculty and researchers to explore research output, publication quality, institutional contributions, indexing status, faculty activity and SDG representation through an interactive interface.
