// All case-study content lives here. The site renders from this file.
// Any field set to null shows as a dashed "to fill in" placeholder, so nothing looks finished
// until you have run the analysis and typed in your own numbers.
window.PROFILE = {
  name: "Mihir Jasani",
  headline: "I build *Power BI reporting* that turns messy data into decisions.",
  intro: "I'm Mihir Jasani, a data analyst. I write the SQL, clean and reconcile the data, and build the Power BI dashboards that management uses to make decisions, most recently at Elevara Digital. I'm certified in Power BI (PL-300) and Microsoft Fabric (DP-600). My day-to-day work is confidential, so these case studies (four completed, one in development) use real Canadian public data. Each one is a short story: the question, the data, what I found and what I'd recommend.",
  email: "mailto:mihirjasani369@gmail.com",
  linkedin: "https://www.linkedin.com/in/mihir-jasani/",
  resume: "downloads/Mihir-Jasani-Resume.pdf",
  certs: [
    { label: "PL-300 Power BI Data Analyst Associate", url: "https://learn.microsoft.com/api/credentials/share/en-us/MihirJasani-7391/EC785C0EC14FA2EC?sharingId=43D033F7F8EE565A" },
    { label: "DP-600 Fabric Analytics Engineer Associate", url: "https://learn.microsoft.com/api/credentials/share/en-us/MihirJasani-7391/51AF5C13B57788B4?sharingId=43D033F7F8EE565A" }
  ],
  tools: "SQL · MySQL · Power BI · DAX · Power Query · Excel · Python · Fabric",
  location: "Toronto, Ontario",
  about: [
    "I am a business intelligence and analytics graduate based in Toronto. I work in SQL, Power BI, DAX, Power Query, Excel and Python, and I like turning a plain question into a report that someone can act on.",
    "I hold the Microsoft Power BI Data Analyst Associate (PL-300) and Fabric Analytics Engineer Associate (DP-600) certifications, and I build my projects on the same pattern: a clean star-schema model, documented DAX measures, and a short written recommendation."
  ],
  aboutPortfolio: "This portfolio has four completed case studies and one in development, all built on public Canadian data: banking, health, transportation and city services (a fifth, on federal contracts, is in progress). Each one lists its source and licence and states what the data cannot tell you. No employer or client data is used anywhere on this site.",
  experience: [
    {"when": "Oct 2025 - Present", "role": "Data Analyst", "org": "Elevara Digital, Toronto, ON", "text": ["Develop SQL queries using joins, aggregations, and filtering to retrieve and consolidate business data for reporting and analysis and generate data exports.", "Clean, validate, and reconcile reporting datasets to improve data completeness, accuracy, and consistency.", "Collaborate with business stakeholders to understand data requirements, define KPI calculations, and recommend reporting solutions.", "Develop and maintain Power BI dashboards and communicate operational trends and findings to support management decisions."]},
    {"when": "Apr 2025 - Sep 2025", "role": "Data Analyst Intern", "org": "Impact Zero, Toronto, ON", "text": ["Cleaned and consolidated HubSpot CRM data and developed a Power BI dashboard covering over $400K in pipeline revenue, reducing sales deal tracking time by 50%.", "Created custom reporting metrics and communicated sales pipeline findings to leadership to support business decisions.", "Built a Python and Streamlit application to summarize more than 500 meeting notes and extract action items, improving executive task follow-up by 35%."]},
    {"when": "Jun 2023 - Aug 2025", "role": "Peer Tutor", "org": "Humber College, Toronto, ON", "text": ["Delivered workshops and personalized support in Excel, Power BI, and statistics, adapting explanations to learners with different levels of technical understanding.", "Explained data modeling, regression analysis, and hypothesis testing in accessible language, helping students apply analytical concepts to coursework."]},
    {"when": "Dec 2021 - Oct 2022", "role": "Jr Reporting Analyst", "org": "Scalezix Technologies, Ahmedabad, India", "text": ["Developed Power BI data models and dashboards to analyze procurement spend across purchasing channels, improving leadership visibility and identifying potential cost savings of 30%.", "Used Excel Power Query, Pivot Tables, and XLOOKUP to prepare and analyze procurement data, reducing weekly reporting effort by 22 hours.", "Managed recurring weekly reporting deliverables, prioritized deadlines, and presented procurement spend trends and findings to non-technical stakeholders."]}
  ],
  toolGroups: [
    ["Power BI", "star-schema models, DAX, Power Query, report design, PBIP projects in version control"],
    ["Microsoft Fabric", "lakehouse, notebooks, semantic models"],
    ["SQL", "SQLite, MySQL; data-quality checks before every model"],
    ["Python", "repeatable load and clean scripts (pandas)"],
    ["Delivery", "short written findings, limits stated, recommendations a decision-maker can use"]
  ],
  education: [
    "Graduate Certificate, Business Insights and Analytics, Humber Polytechnic",
    "B.Tech, Information Technology, P.P. Savani University"
  ]
};

window.PROJECTS = [
  {
    id: "household-credit",
    sector: "Banking",
    area: "Retail lending",
    title: "Canadian borrowing slows about 18 months after rates rise: what does that mean for lenders?",
    summary: "Household credit balances set against the policy rate, prime and mortgage rates, to see how long rate changes take to show up in borrowing.",
    provenance: "Real",
    source: "Bank of Canada Valet API; Statistics Canada tables 36-10-0639, 38-10-0238, 11-10-0065",
    tools: ["Power BI", "Power Query", "DAX", "Python"],
    headline: { value: "18 months", label: "after a rate rise before credit growth is lowest (correlation -0.52)" },
    question: "When the Bank of Canada moves rates, how long before household borrowing and debt-service burden change, and in which credit categories?",
    data: "Daily rates from the Bank of Canada Valet API rolled up to months. Monthly household credit liabilities by category, plus quarterly credit summary and debt-service indicators, from Statistics Canada. Market-level data only: no customer or account records.",
    approach: [
      "Load rates and the three Statistics Canada tables into SQLite with a repeatable script.",
      "Build a month-level model in Power BI: one date table, rates, credit, debt service.",
      "Compare YoY credit growth with rate changes at lags of 0 to 24 months, with a lag slicer.",
      "Document every DAX measure and its definition."
    ],
    found: [
      "Household credit grew from $1.48 trillion in January 2010 to $3.30 trillion in August 2026, 2.22 times as large.",
      "Credit growth peaked at 8.69% in May 2022 and slowed to 3.48% by October 2023, after the prime rate rose from 2.45% to 7.20%.",
      "Credit growth is lowest about 18 months after a rate rise, with a correlation of -0.52. At 6 months it is only -0.17.",
      "Debt payments took 15.17% of household income in early 2023, up from 12.56% in the April 2020 quarter, and are 14.52% now."
    ],
    recommend: [
      "Plan for a delayed response: expect credit growth to react to a rate change over about 1.5 years, not right away.",
      "Track the debt service ratio each quarter next to rates; it was 15.17% in early 2023 and is 14.52% now.",
      "Add delinquency data to test whether higher debt service led to missed payments; this public data cannot."
    ],
    limits: [
      "Correlation is not causation: many things move at once when rates change.",
      "Rates and credit both trend and the 12-month windows overlap, so the lag is a pattern, not a precise delay.",
      "The data is national and aggregated, so it says nothing about individual borrowers or default risk.",
      "I did not find a Statistics Canada table with delinquency or arrears, so the project does not report it.",
      "Credit data ends in August 2026, rates in October 2026 and debt service in April 2026.",
      "Credit cards and personal loans show jumps in 2011 to 2014 that look like reclassifications, so they are used as latest-month figures only."
    ],
    repo: "01-banking-household-credit",
    hero: 3,
    shots: [
      { file: "images/hc-1-start.png", caption: "Start here: the question, four headline numbers and how to use the report" },
      { file: "images/hc-2-rates.png", caption: "Rates: policy, prime and 5-year mortgage rates, 2010 to 2026" },
      { file: "images/hc-3-credit.png", caption: "Credit: growth for the total and each category, with a scorecard" },
      { file: "images/hc-4-lag.png", caption: "Rate lag: pick a lag in months to compare credit growth with an earlier rate change" },
      { file: "images/hc-5-quality.png", caption: "Data quality: what each source covers, where the gaps are and what I did about them" }
    ],
    kpis: [
      { label: "Household credit", value: "$3.30T", sub: "As of Aug 2026", icon: "bars" },
      { label: "Credit growth", value: "4.05%", sub: "\u25bc from 8.69% (May 2022)", icon: "clock" },
      { label: "Prime rate", value: "4.45%", sub: "\u25bc from 7.20% (Jul 2023)", icon: "check" },
      { label: "Strongest lag", value: "18 months", sub: "Correlation -0.52", icon: "warn" }
    ],
    stats: [
      {
        "value": "5",
        "label": "report pages",
        "sub": ""
      },
      {
        "value": "36",
        "label": "data visuals",
        "sub": ""
      },
      {
        "value": "10",
        "label": "tables",
        "sub": "4 data, 5 helper, 1 measures"
      },
      {
        "value": "5",
        "label": "relationships",
        "sub": ""
      },
      {
        "value": "60",
        "label": "DAX measures",
        "sub": ""
      }
    ],
    techniques: ["Star schema", "Date table", "Year-over-year DAX", "Lag selector", "DAX variables", "Reset-filters bookmark", "Custom theme (JSON)", "PBIP + TMDL project"],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/household-credit-report.pdf", note: "All five report pages, as exported from Power BI Desktop." },
      { label: "Download the Power BI project (.zip)", file: "downloads/household-credit-powerbi-project.zip", note: "The .pbip project plus the model CSVs. The README inside says how to set the CSV folder." }
    ],
    chapters: [
      { visuals: [{ ref: 0 }] },
      { visuals: [{ ref: 1 }, { ref: 2 }] },
      { visuals: [{ ref: 3 }] },
      { visuals: [{ ref: 4 }] }
    ],
    charts: [
      {"type": "line", "title": "Policy, prime and 5-year mortgage rates by month (%)", "labels": ["2010-01", "2010-02", "2010-03", "2010-04", "2010-05", "2010-06", "2010-07", "2010-08", "2010-09", "2010-10", "2010-11", "2010-12", "2011-01", "2011-02", "2011-03", "2011-04", "2011-05", "2011-06", "2011-07", "2011-08", "2011-09", "2011-10", "2011-11", "2011-12", "2012-01", "2012-02", "2012-03", "2012-04", "2012-05", "2012-06", "2012-07", "2012-08", "2012-09", "2012-10", "2012-11", "2012-12", "2013-01", "2013-02", "2013-03", "2013-04", "2013-05", "2013-06", "2013-07", "2013-08", "2013-09", "2013-10", "2013-11", "2013-12", "2014-01", "2014-02", "2014-03", "2014-04", "2014-05", "2014-06", "2014-07", "2014-08", "2014-09", "2014-10", "2014-11", "2014-12", "2015-01", "2015-02", "2015-03", "2015-04", "2015-05", "2015-06", "2015-07", "2015-08", "2015-09", "2015-10", "2015-11", "2015-12", "2016-01", "2016-02", "2016-03", "2016-04", "2016-05", "2016-06", "2016-07", "2016-08", "2016-09", "2016-10", "2016-11", "2016-12", "2017-01", "2017-02", "2017-03", "2017-04", "2017-05", "2017-06", "2017-07", "2017-08", "2017-09", "2017-10", "2017-11", "2017-12", "2018-01", "2018-02", "2018-03", "2018-04", "2018-05", "2018-06", "2018-07", "2018-08", "2018-09", "2018-10", "2018-11", "2018-12", "2019-01", "2019-02", "2019-03", "2019-04", "2019-05", "2019-06", "2019-07", "2019-08", "2019-09", "2019-10", "2019-11", "2019-12", "2020-01", "2020-02", "2020-03", "2020-04", "2020-05", "2020-06", "2020-07", "2020-08", "2020-09", "2020-10", "2020-11", "2020-12", "2021-01", "2021-02", "2021-03", "2021-04", "2021-05", "2021-06", "2021-07", "2021-08", "2021-09", "2021-10", "2021-11", "2021-12", "2022-01", "2022-02", "2022-03", "2022-04", "2022-05", "2022-06", "2022-07", "2022-08", "2022-09", "2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "unit": "% per year", "noLabels": true, "datasets": [{"label": "Policy rate", "values": [0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.5, 1.5, 1.5, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 1.0, 1.0, 1.5, 2.5, 2.5, 3.25, 3.75, 3.75, 4.25, 4.5, 4.5, 4.5, 4.5, 4.5, 4.75, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.75, 4.5, 4.5, 4.25, 3.75, 3.75, 3.25, 3.0, 3.0, 2.75, 2.75, 2.75, 2.75, 2.75, 2.75, 2.5, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.25, 2.5]}, {"label": "Prime rate", "values": [2.25, 2.25, 2.25, 2.25, 2.25, 2.5, 2.75, 2.75, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 2.85, 2.85, 2.85, 2.85, 2.85, 2.85, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.95, 2.95, 3.2, 3.2, 3.2, 3.2, 3.45, 3.45, 3.45, 3.45, 3.45, 3.45, 3.7, 3.7, 3.7, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 3.95, 2.95, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45, 2.7, 3.2, 3.2, 3.7, 4.7, 4.7, 5.45, 5.45, 5.95, 6.45, 6.45, 6.7, 6.7, 6.7, 6.7, 6.95, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 6.95, 6.7, 6.7, 6.45, 5.95, 5.95, 5.45, 5.45, 5.2, 4.95, 4.95, 4.95, 4.95, 4.95, 4.95, 4.7, 4.7, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45, 4.45]}, {"label": "5-year mortgage rate", "values": [5.49, 5.39, 5.85, 6.25, 5.99, 5.89, 5.79, 5.39, 5.39, 5.29, 5.44, 5.19, 5.19, 5.44, 5.34, 5.69, 5.59, 5.39, 5.39, 5.39, 5.19, 5.29, 5.29, 5.29, 5.29, 5.24, 5.24, 5.44, 5.34, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 5.14, 5.14, 5.14, 5.14, 5.14, 5.34, 5.34, 5.34, 5.34, 5.34, 5.24, 5.24, 4.99, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.74, 4.74, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.74, 4.74, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.64, 4.84, 4.84, 4.89, 4.99, 4.99, 4.99, 5.14, 5.14, 5.14, 5.14, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.34, 5.19, 5.19, 5.19, 5.19, 5.19, 5.19, 5.19, 5.19, 5.04, 5.04, 4.94, 4.94, 4.94, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.79, 4.99, 5.39, 6.04, 6.14, 6.14, 6.14, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.84, 6.84, 7.04, 7.04, 7.04, 6.89, 6.84, 6.84, 6.84, 6.84, 6.84, 6.79, 6.59, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.49, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.09, 6.19]}]},
      {"type": "line", "title": "Year-over-year credit growth by month (%)", "labels": ["2010-01", "2010-02", "2010-03", "2010-04", "2010-05", "2010-06", "2010-07", "2010-08", "2010-09", "2010-10", "2010-11", "2010-12", "2011-01", "2011-02", "2011-03", "2011-04", "2011-05", "2011-06", "2011-07", "2011-08", "2011-09", "2011-10", "2011-11", "2011-12", "2012-01", "2012-02", "2012-03", "2012-04", "2012-05", "2012-06", "2012-07", "2012-08", "2012-09", "2012-10", "2012-11", "2012-12", "2013-01", "2013-02", "2013-03", "2013-04", "2013-05", "2013-06", "2013-07", "2013-08", "2013-09", "2013-10", "2013-11", "2013-12", "2014-01", "2014-02", "2014-03", "2014-04", "2014-05", "2014-06", "2014-07", "2014-08", "2014-09", "2014-10", "2014-11", "2014-12", "2015-01", "2015-02", "2015-03", "2015-04", "2015-05", "2015-06", "2015-07", "2015-08", "2015-09", "2015-10", "2015-11", "2015-12", "2016-01", "2016-02", "2016-03", "2016-04", "2016-05", "2016-06", "2016-07", "2016-08", "2016-09", "2016-10", "2016-11", "2016-12", "2017-01", "2017-02", "2017-03", "2017-04", "2017-05", "2017-06", "2017-07", "2017-08", "2017-09", "2017-10", "2017-11", "2017-12", "2018-01", "2018-02", "2018-03", "2018-04", "2018-05", "2018-06", "2018-07", "2018-08", "2018-09", "2018-10", "2018-11", "2018-12", "2019-01", "2019-02", "2019-03", "2019-04", "2019-05", "2019-06", "2019-07", "2019-08", "2019-09", "2019-10", "2019-11", "2019-12", "2020-01", "2020-02", "2020-03", "2020-04", "2020-05", "2020-06", "2020-07", "2020-08", "2020-09", "2020-10", "2020-11", "2020-12", "2021-01", "2021-02", "2021-03", "2021-04", "2021-05", "2021-06", "2021-07", "2021-08", "2021-09", "2021-10", "2021-11", "2021-12", "2022-01", "2022-02", "2022-03", "2022-04", "2022-05", "2022-06", "2022-07", "2022-08", "2022-09", "2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08"], "unit": "% growth", "suffix": "%", "noLabels": true, "datasets": [{"label": "Total", "values": [7.7, 7.6, 7.5, 7.3, 7.4, 7.3, 6.9, 6.8, 6.7, 6.2, 6.2, 6.0, 6.5, 6.2, 6.2, 6.2, 6.0, 6.1, 6.3, 6.4, 6.3, 6.2, 6.2, 5.8, 5.2, 5.2, 5.4, 5.3, 5.0, 4.6, 4.3, 4.3, 4.3, 4.3, 4.1, 4.4, 4.3, 4.5, 4.3, 4.2, 4.2, 4.2, 4.6, 4.3, 4.3, 4.1, 4.3, 4.2, 4.4, 4.1, 4.2, 4.2, 4.2, 4.2, 4.1, 4.3, 4.5, 4.7, 4.7, 4.6, 4.8, 4.7, 4.7, 4.8, 5.0, 5.2, 5.3, 5.4, 5.4, 5.4, 5.5, 5.7, 5.7, 5.7, 5.8, 6.0, 5.9, 5.8, 5.8, 5.7, 5.7, 5.6, 5.6, 5.6, 5.6, 5.8, 5.8, 5.8, 5.8, 5.7, 5.8, 5.7, 5.5, 5.4, 5.4, 5.2, 5.1, 5.0, 4.8, 4.6, 4.5, 4.3, 4.2, 4.2, 4.2, 4.1, 4.1, 4.1, 3.9, 3.8, 3.8, 3.8, 3.9, 3.9, 3.8, 3.8, 3.7, 3.8, 3.7, 3.8, 4.0, 4.2, 3.8, 3.4, 2.9, 2.8, 2.9, 3.2, 3.5, 3.7, 4.0, 4.0, 4.1, 3.9, 4.4, 5.4, 6.1, 6.8, 7.1, 7.2, 7.2, 7.2, 7.5, 7.7, 8.0, 8.5, 8.7, 8.6, 8.7, 8.4, 8.2, 8.0, 7.7, 7.4, 6.8, 6.4, 5.9, 5.4, 5.0, 4.5, 4.1, 3.7, 3.6, 3.6, 3.5, 3.5, 3.6, 3.6, 3.7, 3.7, 3.7, 3.7, 3.7, 3.7, 3.8, 3.8, 4.0, 4.1, 4.3, 4.4, 4.4, 4.4, 4.5, 4.5, 4.6, 4.7, 4.5, 4.6, 4.6, 4.6, 4.5, 4.3, 4.4, 4.4, 4.4, 4.3, 4.2, 4.1, 4.2, 4.1]}, {"label": "Mortgages", "values": [7.8, 7.9, 8.0, 7.9, 8.6, 8.9, 8.5, 8.4, 8.3, 8.0, 8.1, 7.9, 8.1, 7.8, 7.9, 7.8, 7.5, 7.3, 7.7, 8.0, 8.0, 8.1, 7.9, 7.3, 7.2, 7.2, 7.3, 7.2, 6.7, 6.1, 5.6, 5.3, 5.3, 5.2, 5.1, 5.5, 5.4, 5.2, 4.9, 4.8, 4.9, 5.0, 5.4, 5.1, 5.0, 4.9, 5.2, 4.9, 4.9, 5.0, 5.0, 4.9, 4.9, 4.9, 4.7, 4.9, 5.1, 5.4, 5.3, 5.3, 5.5, 5.5, 5.5, 5.5, 5.7, 6.1, 6.3, 6.5, 6.6, 6.7, 6.9, 7.2, 7.2, 7.1, 7.2, 7.4, 7.3, 7.4, 7.3, 7.3, 7.4, 7.1, 7.0, 6.9, 6.8, 6.9, 6.9, 6.9, 6.9, 6.7, 6.7, 6.4, 6.1, 6.1, 6.0, 6.0, 5.9, 5.8, 5.6, 5.3, 5.1, 4.9, 4.8, 4.7, 4.7, 4.5, 4.4, 4.4, 4.3, 4.2, 4.3, 4.3, 4.5, 4.5, 4.5, 4.6, 4.6, 4.8, 4.8, 4.8, 5.0, 5.2, 5.3, 5.5, 5.3, 5.3, 5.5, 5.7, 6.2, 6.6, 7.0, 7.2, 7.4, 7.5, 7.8, 8.4, 9.1, 10.0, 10.4, 10.5, 10.4, 10.3, 10.5, 10.6, 10.7, 11.0, 10.9, 10.6, 10.5, 10.0, 9.6, 9.2, 8.9, 8.4, 7.6, 7.1, 6.5, 5.9, 5.5, 5.0, 4.4, 4.0, 3.8, 3.8, 3.7, 3.8, 3.8, 3.8, 3.7, 3.7, 3.7, 3.6, 3.7, 3.7, 3.7, 3.7, 3.8, 3.9, 4.1, 4.2, 4.5, 4.5, 4.6, 4.8, 4.8, 4.9, 4.8, 4.8, 4.8, 4.9, 4.8, 4.7, 4.6, 4.5, 4.4, 4.2, 4.1, 4.0, 4.0, 3.8]}, {"label": "Non-mortgage loans", "values": [7.5, 7.1, 6.6, 6.3, 5.5, 4.5, 4.3, 4.0, 3.9, 3.2, 2.9, 2.7, 3.7, 3.5, 3.3, 3.4, 3.4, 3.9, 3.8, 3.5, 3.2, 2.7, 3.0, 2.9, 1.7, 1.7, 1.9, 1.7, 2.0, 2.0, 1.8, 2.3, 2.5, 2.7, 2.2, 2.2, 2.2, 3.2, 3.1, 3.1, 3.0, 2.8, 3.1, 2.8, 2.8, 2.7, 2.7, 2.9, 3.3, 2.5, 2.7, 2.8, 2.7, 3.0, 3.0, 3.0, 3.2, 3.5, 3.5, 3.4, 3.3, 3.2, 3.2, 3.4, 3.5, 3.5, 3.3, 3.1, 3.0, 2.7, 2.8, 2.7, 2.7, 2.8, 2.9, 3.0, 2.8, 2.7, 2.8, 2.4, 2.2, 2.5, 2.5, 3.0, 3.1, 3.3, 3.6, 3.4, 3.5, 3.5, 3.8, 4.1, 4.2, 4.0, 4.0, 3.6, 3.4, 3.2, 2.9, 2.9, 3.1, 3.2, 3.1, 3.1, 3.3, 3.3, 3.4, 3.3, 3.0, 2.7, 2.6, 2.7, 2.6, 2.4, 2.3, 2.0, 1.7, 1.6, 1.3, 1.4, 1.6, 1.8, 0.6, -1.5, -2.7, -2.8, -2.9, -2.7, -2.7, -2.8, -2.9, -3.5, -3.8, -4.6, -3.8, -2.1, -1.2, -1.2, -1.2, -1.2, -0.9, -0.7, 0.1, 0.4, 1.0, 1.9, 2.7, 3.3, 3.9, 4.1, 4.2, 4.6, 4.5, 4.8, 4.3, 4.4, 4.2, 4.0, 3.5, 3.3, 3.3, 3.0, 3.2, 2.8, 2.7, 2.6, 2.9, 3.1, 3.6, 3.9, 3.8, 4.0, 3.5, 3.8, 4.0, 4.2, 4.5, 4.7, 4.6, 4.9, 4.3, 3.9, 4.4, 3.9, 3.9, 4.0, 3.8, 3.9, 4.1, 3.6, 3.6, 3.3, 3.8, 4.2, 4.2, 4.3, 4.7, 4.7, 4.8, 4.9]}]},
      {"type": "bar", "title": "Latest growth vs a year earlier, by category (Aug 2026)", "labels": ["Credit cards", "Non-mortgage loans", "Total household credit", "Home equity lines of credit", "Lines of credit", "Mortgage loans", "Personal loans", "Auto loans"], "values": [6.49, 4.93, 4.05, 3.91, 3.88, 3.75, 1.39, 1.00], "unit": "% growth", "suffix": "%", "decimals": 2, "highlight": 2},
      {"type": "bar", "orient": "v", "title": "Correlation of credit growth with the prime-rate change, by lag in months", "labels": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"], "values": [0.27, 0.19, 0.12, 0.04, -0.04, -0.11, -0.17, -0.22, -0.27, -0.31, -0.35, -0.39, -0.43, -0.46, -0.48, -0.49, -0.51, -0.52, -0.52, -0.52, -0.51, -0.5, -0.48, -0.45, -0.41], "unit": "correlation", "highlight": 18, "noLabels": true},
      {"type": "line", "title": "Share of household income going to debt payments, by quarter (%)", "labels": ["2010 Q1", "2010 Q2", "2010 Q3", "2010 Q4", "2011 Q1", "2011 Q2", "2011 Q3", "2011 Q4", "2012 Q1", "2012 Q2", "2012 Q3", "2012 Q4", "2013 Q1", "2013 Q2", "2013 Q3", "2013 Q4", "2014 Q1", "2014 Q2", "2014 Q3", "2014 Q4", "2015 Q1", "2015 Q2", "2015 Q3", "2015 Q4", "2016 Q1", "2016 Q2", "2016 Q3", "2016 Q4", "2017 Q1", "2017 Q2", "2017 Q3", "2017 Q4", "2018 Q1", "2018 Q2", "2018 Q3", "2018 Q4", "2019 Q1", "2019 Q2", "2019 Q3", "2019 Q4", "2020 Q1", "2020 Q2", "2020 Q3", "2020 Q4", "2021 Q1", "2021 Q2", "2021 Q3", "2021 Q4", "2022 Q1", "2022 Q2", "2022 Q3", "2022 Q4", "2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4", "2025 Q1", "2025 Q2", "2025 Q3", "2025 Q4", "2026 Q1", "2026 Q2"], "unit": "% of income", "suffix": "%", "noLabels": true, "datasets": [{"label": "Total", "values": [13.8, 14.1, 14.1, 14.0, 14.1, 14.2, 14.1, 14.0, 13.9, 14.0, 14.0, 14.0, 13.8, 13.8, 13.9, 13.8, 13.8, 13.9, 13.9, 14.1, 14.0, 13.9, 13.8, 13.8, 14.2, 14.2, 14.2, 14.1, 14.3, 14.3, 14.2, 14.4, 14.6, 14.8, 15.0, 14.9, 15.1, 15.0, 15.1, 14.9, 14.6, 12.6, 13.5, 13.9, 13.6, 13.7, 13.7, 13.9, 13.8, 14.0, 14.4, 14.6, 15.2, 15.1, 15.1, 15.1, 15.1, 15.1, 14.8, 14.7, 14.7, 14.8, 14.7, 14.7, 14.7, 14.5]}, {"label": "Mortgage", "values": [6.1, 6.2, 6.2, 6.2, 6.2, 6.3, 6.3, 6.2, 6.2, 6.3, 6.3, 6.3, 6.2, 6.3, 6.3, 6.3, 6.4, 6.4, 6.4, 6.4, 6.4, 6.3, 6.4, 6.5, 6.6, 6.7, 6.7, 6.7, 6.8, 6.7, 6.7, 6.8, 6.9, 7.0, 7.1, 7.1, 7.2, 7.2, 7.2, 7.2, 7.1, 6.2, 6.8, 7.0, 6.9, 7.1, 7.1, 7.2, 7.2, 7.3, 7.6, 7.8, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.0, 7.9, 7.9, 7.9, 7.9, 7.8, 7.8, 7.7]}, {"label": "Non-mortgage", "values": [7.7, 7.9, 7.9, 7.8, 7.8, 7.9, 7.9, 7.8, 7.7, 7.7, 7.7, 7.7, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.7, 7.6, 7.5, 7.4, 7.4, 7.5, 7.5, 7.4, 7.4, 7.5, 7.5, 7.5, 7.6, 7.7, 7.8, 7.9, 7.8, 7.9, 7.8, 7.8, 7.8, 7.5, 6.4, 6.7, 6.9, 6.7, 6.7, 6.6, 6.7, 6.6, 6.7, 6.8, 6.8, 7.0, 6.9, 6.9, 6.9, 6.9, 6.9, 6.8, 6.8, 6.8, 6.9, 6.8, 6.8, 6.9, 6.8]}]}
    ],
    model: {
      measures: [
        { name: "Credit $B (Latest)", dax: "VAR m = [Credit Latest Month]\nRETURN\n    CALCULATE (\n        [Credit $B],\n        fact_credit[MonthStart] = m\n    )" },
        { name: "Credit YoY %", dax: "VAR cur = [Credit $B]\nVAR py =\n    CALCULATE (\n        [Credit $B],\n        SAMEPERIODLASTYEAR ( 'Date'[Date] )\n    )\nRETURN\n    IF (\n        ISBLANK ( cur ) || ISBLANK ( py ),\n        BLANK (),\n        DIVIDE ( cur - py, py )\n    )" },
        { name: "Mortgage Share (Latest)", dax: "DIVIDE (\n    CALCULATE (\n        [Credit $B (Latest)],\n        Dim_Category[Category] = \"Mortgage loans\"\n    ),\n    [Total Credit $B (Latest)]\n)" },
        { name: "Prime Chg 12m (Lagged)", dax: "VAR k = [Selected Lag]\nRETURN\n    CALCULATE (\n        [Prime Chg 12m],\n        DATEADD ( 'Date'[Date], -k, MONTH )\n    )" },
        { name: "Strongest Lag", dax: "VAR t =\n    ADDCOLUMNS (\n        ALL ( lag_correlation ),\n        \"a\", ABS ( lag_correlation[correlation] )\n    )\nRETURN\n    MAXX (\n        TOPN ( 1, t, [a], DESC ),\n        lag_correlation[lag_months]\n    )" }
      ]
    },
    story: {
      bottom: "credit growth is lowest about 18 months after a rate rise, so lenders should plan for a delayed response. The lag depends on the method, and the data cannot show cause.",
      toc: true,
      terms: "Policy rate = the Bank of Canada's overnight target. Prime rate = the rate banks charge their best customers. Debt service ratio = the share of household income going to debt payments. Correlation = how closely two series move together, from -1 to +1.",
      next: ["Add delinquency or arrears data to test whether higher debt service led to missed payments.", "Test the lag with the rate level and other windows, to see how stable 18 months is.", "Refresh the report each quarter when Statistics Canada publishes new debt-service figures."],
      dek: "When the Bank of Canada raises interest rates, borrowing is supposed to cool. I used public Bank of Canada and Statistics Canada data from 2010 to 2026 to check how long that takes: how quickly Canadian household borrowing slowed after rates went up, and whether families ended up spending more of their income on debt payments.",
      chips: ["Python (pandas)", "SQL (SQLite)", "API data pulls", "Power Query", "Star schema", "DAX time intelligence", "What-if lag selector", "Correlation analysis", "Custom theme", "PBIP + TMDL in Git"],
      meta: [
        { k: "Data", v: "Bank of Canada Valet API and Statistics Canada tables 36-10-0639, 38-10-0238 and 11-10-0065 (real, market-level)" },
        { k: "Scope", v: "202 months of rates, 8 credit categories and 66 quarters of debt service" },
        { k: "Tools", v: "Power BI, DAX, Power Query, Python" },
        { k: "My role", v: "End to end: pulled the data from two public sources, checked it in Python, built the star-schema model and DAX, designed the five-page report and wrote the findings" },
        { k: "Source links", links: [{"v": "Bank of Canada Valet API", "href": "https://www.bankofcanada.ca/valet/"}, {"v": "Statistics Canada 36-10-0639", "href": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610063901"}, {"v": "38-10-0238", "href": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3810023801"}, {"v": "11-10-0065", "href": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1110006501"}] }
      ],
      findings: [
        "Household credit grew from $1.48 trillion in January 2010 to $3.30 trillion in August 2026, 2.22 times as large.",
        "Credit growth peaked at 8.69% in May 2022 and slowed to 3.48% by October 2023, after the prime rate rose from 2.45% to 7.20%.",
        "Credit growth is lowest about 18 months after a rate rise, with a correlation of -0.52. At 6 months it is only -0.17.",
        "Debt payments took 15.17% of household income in early 2023, up from 12.56% in the April 2020 quarter, and are 14.52% now."
      ],
      chapters: [
        { n: "01 \u00b7 RATES", ch: 0, title: "Interest rates rose fast in 2022 and 2023, then eased",
          paras: ["The prime rate went from 2.45% in February 2022 to 7.20% in July 2023, and stayed there for 11 months.",
                  "It has since eased to 4.45%. The 5-year mortgage rate peaked at 7.04% in October 2023 and is 6.19% now, 1.74 points above prime."],
          note: "Rates are shown to two decimals because that is how they are published.",
          tabs: [], src: "Source: Bank of Canada Valet API. Prime and mortgage rates are weekly, so each month shows the last weekly value." },
        { n: "02 \u00b7 CREDIT", ch: 1, title: "Credit growth slowed from 8.69% to about 4%",
          paras: ["Total household credit grew 8.69% a year at its May 2022 peak. Growth fell to 3.48% by October 2023 and is 4.05% now.",
                  "Mortgage growth peaked at 11.02% in February 2022 and is 3.75% now. Non-mortgage loans shrank 4.59% year over year in February 2021, during the pandemic, and first grew faster than mortgages in February 2024 (4.93% now)."],
          note: "Credit cards and personal loans show year-over-year spikes above 20% in 2011 to 2014 that look like reclassifications, not real borrowing.",
          tabs: ["Growth by month", "Latest, by category"], src: "Source: Statistics Canada table 36-10-0639, seasonally adjusted." },
        { n: "03 \u00b7 THE LAG", ch: 2, title: "Credit growth is lowest about 18 months after rates rise",
          paras: ["I compared credit growth with the change in the prime rate over the previous 12 months, shifted back by 0 to 24 months. The relationship is strongest at 18 months, with a correlation of -0.52.",
                  "At 6 months it is only -0.17 and at 12 months -0.43. With no delay the correlation is positive (+0.27), which fits a central bank raising rates when borrowing is already strong."],
          note: "Using the level of the prime rate instead of its 12-month change, the strongest lag is about 8 months, so the exact delay depends on the method.",
          tabs: [], src: "Correlation across 164 to 188 months, 2010 to 2026; 170 months at the 18-month lag." },
        { n: "04 \u00b7 DEBT SERVICE", ch: 3, title: "Debt payments took a bigger share of income after rates rose",
          paras: ["The share of household income going to debt payments rose from 12.56% in the April 2020 quarter to 15.17% in the January 2023 quarter, as rates started to rise.",
                  "It is 14.52% now. The mortgage part peaked at 8.23% and is 7.72% now; the non-mortgage part is 6.80%."],
          note: "The quarter labels follow Statistics Canada: 2026 Q2 is the quarter starting April 2026.",
          tabs: [], src: "Source: Statistics Canada table 11-10-0065, seasonally adjusted at annual rates." }
      ],
      recs: [
        { who: "Head of retail lending", title: "Plan for a delayed response to rate changes", text: "Expect credit growth to react to a rate change over about 18 months, not right away. Review lending targets against rate moves from 12 to 24 months earlier.", measure: "Measure: credit growth vs the prime-rate change 18 months earlier" },
        { who: "Risk and finance", title: "Watch debt service alongside rates", text: "Debt payments reached 15.17% of income in early 2023 and are 14.52% now. Track the ratio each quarter, for the total and for mortgages.", measure: "Measure: debt service ratio, total and mortgage" },
        { who: "Analytics team", title: "Add delinquency data to test repayment pressure", text: "This public data has no arrears or default figures, so it cannot say whether higher debt service led to missed payments. Add an arrears series to answer that.", measure: "Next step: join an arrears series" }
      ],
      recNote: "These are proposals from public, market-level data. They are not a lending model.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Bank of Canada and Statistics Canada", s: "Rates from the Valet API and three Statistics Canada tables, 2010 to 2026" },
        { i: "02 \u00b7 PREPARE", b: "Python", s: "Rolled rates up to months and kept 8 credit categories that appear once per month, because lender names repeat across the hierarchy" },
        { i: "03 \u00b7 CHECK", b: "Reconciliation", s: "Checked the report cards and the lag measures against the Python results; auto loans start in 2016, the only gap" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "Monthly credit and rates, quarterly debt service, 5 helper tables and 60 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "5 pages with a lag selector, continuous time axes, a data-quality page and a reset-filters button" }
      ]
    },
  },
  {
    id: "collision-risk",
    sector: "Insurance",
    area: "Underwriting and claims analytics",
    title: "Fatal collisions are more than twice as likely at night: when and where do Canadian roads turn deadly?",
    summary: "185,772 police-reported fatal and injury collisions across Canada, broken down by hour, road conditions, people and the change from 2019 to 2020.",
    provenance: "Real",
    source: "Transport Canada, National Collision Database (2019 and 2020)",
    tools: ["Power BI", "DAX", "SQL", "Python"],
    headline: { value: "2.24×", label: "as likely to be fatal at night (3.41%) as by day (1.52%)" },
    question: "When, where and under what conditions do fatal collisions concentrate, and who is most at risk, so an insurer's analytics team knows what to monitor and what to say about safe driving?",
    data: "Person-level rows for police-reported fatal and injury collisions, 2019 and 2020: 185,772 collisions and 463,630 people after cleaning. No property-damage-only collisions and no insurance claims.",
    approach: [
      "Download the open CSVs and check every code against the data dictionary.",
      "Find the real collision ID and drop dummy rows before counting anything.",
      "Build a star schema with an unknown member in every dimension, then a seven-page Power BI report.",
      "Compare 2019 with 2020, and test the safety-device finding within age bands before stating it."
    ],
    found: [
      "Collisions fell 24.38% in 2020, but fatal collisions only 1.29%, so the fatal share rose from 1.53% to 2.00%. Injury collisions account for 99.92% of the decline.",
      "Night collisions (10 pm to 6 am) are 3.41% fatal against 1.52% by day, 2.24 times as likely. The riskiest hour is 4 am, at 4.89%.",
      "Curved roads (3.63%), night (3.41%) and single-vehicle collisions (2.73%) have the highest fatal shares. No traffic control carries 2,349 of the 3,225 fatal collisions (72.84%).",
      "Occupants with no safety device used die at 6.98% against 0.43% with one, 16.09 times as often, and the gap holds in every age band."
    ],
    recommend: [
      "Monitor the fatal share, not only the count: in 2020 collisions fell but fatal ones did not.",
      "Put night driving, single-vehicle collisions, curved roads and roads with no traffic control on the risk watch list: they carry far more fatal outcomes than their share of collisions.",
      "Use the safety-device gap in safe-driving messaging. These are proposals from police-reported data, not claims or pricing advice."
    ],
    limits: [
      "Not claims data: it supports no loss ratio, premium or pricing statement.",
      "Police-reported fatal and injury collisions only, so shares are of serious collisions.",
      "No traffic volumes or kilometres driven, so nothing here is a risk per trip.",
      "Unadjusted associations, not causes. The what-if assumes the road causes the gap.",
      "2020 was a pandemic year, so it is not a typical comparison.",
      "Safety-device use is as recorded by police, and 21.99% of records are unknown."
    ],
    repo: "02-insurance-collision-risk",
    hero: 1,
    shots: [
      { file: "images/cr-1-start.png", caption: "Start here: four headline numbers, what the data shows and what I would do" },
      { file: "images/cr-2-when.png", caption: "When: a heat map of fatal share by hour and weekday, with the night hours highlighted" },
      { file: "images/cr-3-compare.png", caption: "Compare: 2020 against 2019, with fatal and injury collisions indexed to 2019" },
      { file: "images/cr-4-conditions.png", caption: "Conditions: a what-if scenario that sets how much of the gap between risky and safer roads to close" },
      { file: "images/cr-5-people.png", caption: "People: fatality rates by road user, age, safety device and vehicle, against the average person" },
      { file: "images/cr-6-explore.png", caption: "Explore: a decomposition tree that splits the fatal collisions by any factor" },
      { file: "images/cr-7-quality.png", caption: "Data quality: how I found the collision ID, what is unknown and what was excluded" }
    ],
    kpis: [
      { label: "Collisions, 2019 and 2020", value: "185,772", sub: "3,225 fatal, 182,547 injury", icon: "bars" },
      { label: "Fatal share overall", value: "1.74%", sub: "Night 3.41%, day 1.52%", icon: "check" },
      { label: "Fatal share in 2020", value: "2.00%", sub: "\u25b2 from 1.53% in 2019", icon: "clock" },
      { label: "Safety device gap", value: "16.09×", sub: "6.98% with none used against 0.43%", icon: "warn" }
    ],
    stats: [
      { value: "7", label: "report pages", sub: "" },
      { value: "50", label: "data visuals", sub: "" },
      { value: "23", label: "tables", sub: "2 data, 20 helper, 1 measures" },
      { value: "17", label: "relationships", sub: "" },
      { value: "102", label: "DAX measures", sub: "" }
    ],
    techniques: ["Star schema with unknown members", "Date table", "Time intelligence", "Calculation group", "What-if parameter", "Heat map by DAX colour", "Decomposition tree", "Data-quality page", "PBIP + TMDL project"],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/collision-risk-report.pdf", note: "All seven report pages, as exported from Power BI Desktop." },
      { label: "Download the Power BI project (.zip)", file: "downloads/collision-risk-powerbi-project.zip", note: "The .pbip project plus the model CSVs (about 25 MB). The README inside says how to set the CSV folder." }
    ],
    chapters: [
      { visuals: [{ ref: 0 }] },
      { visuals: [{ ref: 1 }, { ref: 2 }] },
      { visuals: [{ ref: 3 }] },
      { visuals: [{ ref: 4 }] },
      { visuals: [{ ref: 5 }] }
    ],
    charts: [
      {"type": "bar", "orient": "v", "title": "Share of collisions that are fatal, by hour of day (amber = 10 pm to 6 am)", "labels": ["12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p"], "values": [3.81, 3.93, 4.4, 4.05, 4.89, 3.24, 2.09, 1.43, 1.0, 1.62, 1.6, 1.41, 1.37, 1.62, 1.42, 1.37, 1.33, 1.42, 1.6, 1.64, 2.18, 2.28, 2.3, 3.2], "unit": "% fatal", "suffix": "%", "decimals": 2, "highlight": [0, 1, 2, 3, 4, 5, 22, 23], "noLabels": true},
      {"type": "bar", "orient": "v", "title": "Collisions by month, 2019 and 2020", "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "unit": "collisions", "noLabels": true, "datasets": [{"label": "2019", "color": "#1B3A5C", "values": [9713, 8327, 7480, 6787, 8037, 9328, 9596, 9371, 9122, 9614, 9370, 9036]}, {"label": "2020", "color": "#2A7F8E", "values": [8519, 7525, 5121, 3251, 5095, 6788, 7652, 7918, 7580, 7270, 6948, 6322]}]},
      {"type": "line", "title": "2020 as a percentage of the same month of 2019 (100 = no change)", "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], "unit": "index", "noLabels": true, "datasets": [{"label": "Injury collisions", "color": "#1B3A5C", "values": [88, 90, 68, 47, 63, 72, 79, 84, 83, 75, 74, 70]}, {"label": "Fatal collisions", "color": "#C77700", "values": [97, 107, 84, 88, 101, 101, 99, 108, 116, 100, 90, 83]}, {"label": "2019 level", "color": "#8A9BAE", "values": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]}]},
      {"type": "bar", "title": "Fatal collisions avoided if the gap were fully closed (2019 and 2020 together)", "labels": ["Add traffic control where there is none", "Treat curved roads like straight ones", "Make night as safe as midday"], "values": [1744, 459, 402], "unit": "fatal collisions avoided", "highlight": 0},
      {"type": "bar", "title": "Occupants: share who die, by safety device", "labels": ["No safety device used", "No safety device equipped", "Safety device used", "Other safety device"], "values": [6.98, 0.52, 0.43, 0.35], "unit": "% who die", "suffix": "%", "decimals": 2, "highlight": 0},
      {"type": "bar", "title": "Share of records with an unknown value, by field", "labels": ["Safety device", "Collision type", "Traffic control", "Age band", "Road alignment", "Road surface", "Weather", "Time of day"], "values": [21.99, 8.95, 7.25, 5.56, 5.22, 4.63, 1.71, 0.96], "unit": "% unknown", "suffix": "%", "decimals": 2, "highlight": 0}
    ],
    model: {
      measures: [
        { name: "Fatal Share", dax: "DIVIDE (\n    [Fatal Collisions],\n    [Collisions]\n)" },
        { name: "Night Fatal Share", dax: "CALCULATE (\n    [Fatal Share],\n    Dim_Hour[Day Part] = \"Night (10 pm to 6 am)\"\n)" },
        { name: "Heat Share", dax: "IF (\n    SELECTEDVALUE ( Dim_Hour[Hour Key], 0 ) = 0,\n    BLANK (),\n    IF (\n        [Collisions] >= 100,\n        [Fatal Share],\n        BLANK ()\n    )\n)" },
        { name: "Fatal Index", dax: "VAR py =\n    CALCULATE (\n        [Fatal Collisions],\n        SAMEPERIODLASTYEAR ( 'Date'[Date] )\n    )\nRETURN\n    IF (\n        ISBLANK ( py ) || ISBLANK ( MAX ( 'Date'[Date] ) ),\n        BLANK (),\n        DIVIDE ( [Fatal Collisions], py ) * 100\n    )" },
        { name: "Scn Avoided", dax: "[Scn Fatal Now]\n    * ( 1 - DIVIDE ( [Scn Rate Safer], [Scn Rate Now] ) )\n    * [Uptake Value]" },
        { name: "Times Avg", dax: "DIVIDE (\n    [Person Fatality Rate],\n    [People Avg Rate]\n)" }
      ]
    },
    story: {
      dek: "Police report every fatal and injury collision in Canada, and Transport Canada publishes the records. I used the 2019 and 2020 files to see when fatal collisions concentrate, which conditions and people carry the most risk, and what changed when traffic fell in 2020.",
      bottom: "fatal collisions concentrate at night, in single-vehicle collisions, on curved roads and where nothing controls traffic, and 2020's drop was almost all injury collisions, so the fatal share rose. These are associations in police-reported data, not causes.",
      toc: true,
      terms: "Fatal share = fatal collisions divided by fatal and injury collisions. Fatality rate = deaths among the people in these collisions, not a risk per person on the road. Unknown = left blank by police or not supplied by that jurisdiction. Collision ID = the C_CASE key that links the rows of one collision.",
      next: ["Add traffic volume or kilometres driven, to turn collision counts into a risk per trip.", "Add the 2021 file and provinces, to test whether the 2020 pattern holds.", "Adjust the safety-device comparison for age, vehicle and collision type with a regression, instead of checking it band by band."],
      chips: ["SQL (11 queries)", "Python", "Power BI", "DAX", "Power Query", "Star schema", "Time intelligence", "Calculation group", "What-if parameter", "Decomposition tree", "PBIP + TMDL in Git"],
      meta: [
        { k: "Data", v: "Transport Canada, National Collision Database, 2019 and 2020 (real, Open Government Licence)" },
        { k: "Scope", v: "185,772 collisions, 330,576 vehicles and 463,630 people" },
        { k: "Tools", v: "Power BI, DAX, Power Query, SQL, Python" },
        { k: "My role", v: "End to end: found the hidden collision ID, checked the data in SQL and Python, built the star-schema model and DAX, designed the seven-page report and wrote the findings" },
        { k: "Source link", v: "Transport Canada National Collision Database (accessed November 2026)", href: "https://open.canada.ca/data/en/dataset/1eb9eba7-71d1-4b30-9fb1-30cbdab7e63a" }
      ],
      findings: [
        "Collisions fell 24.38% in 2020, but fatal collisions only 1.29%, so the fatal share rose from 1.53% to 2.00%. Injury collisions account for 99.92% of the decline.",
        "Night collisions (10 pm to 6 am) are 3.41% fatal against 1.52% by day, 2.24 times as likely. The riskiest hour is 4 am, at 4.89%.",
        "Curved roads (3.63%), night (3.41%) and single-vehicle collisions (2.73%) have the highest fatal shares. No traffic control carries 2,349 of the 3,225 fatal collisions (72.84%).",
        "Occupants with no safety device used die at 6.98% against 0.43% with one, 16.09 times as often, and the gap holds in every age band."
      ],
      chapters: [
        { n: "01 \u00b7 WHEN", ch: 0, title: "Fatal collisions are 2.24 times as likely at night",
          paras: ["Between 10 pm and 6 am, 3.41% of collisions are fatal, against 1.52% from 6 am to 10 pm. The fatal share peaks at 4 am, at 4.89%, against the 1.74% average.",
                  "The pattern holds on every day of the week: the darkest cells in the heat map run from midnight to 5 am from Monday to Sunday."],
          note: "Night has few collisions (about 1,400 at 4 am against 16,000 at 4 pm), so single cells move more. Cells under 100 collisions are blank.",
          tabs: [], src: "Source: Transport Canada, National Collision Database, 2019 and 2020." },
        { n: "02 \u00b7 COMPARE", ch: 1, title: "The 2020 drop was almost entirely injury collisions",
          paras: ["Collisions fell from 105,782 in 2019 to 79,990 in 2020, down 24.38%. Fatal collisions fell only from 1,623 to 1,602, down 1.29%, so the fatal share rose from 1.53% to 2.00%.",
                  "Injury collisions account for 99.92% of the 25,792 fewer collisions. April 2020 was the lowest month, 52.10% below April 2019, while fatal collisions stayed between 83% and 116% of their 2019 level all year."],
          note: "2020 was a pandemic year, so this is a change in the mix of recorded collisions, not proof that driving became riskier.",
          tabs: ["Collisions by month", "Fatal against injury"], src: "Source: Transport Canada. In the second view each line is 2020 as a percentage of the same month of 2019 (100 = no change). Monthly fatal counts are small (about 70 to 200), so single months move more." },
        { n: "03 \u00b7 CONDITIONS", ch: 2, title: "If uncontrolled roads matched signalled ones, about 1,744 fewer deaths",
          paras: ["Roads with no traffic control carry 2,349 of the 3,225 fatal collisions (72.84%) and are 2.41% fatal, against 0.62% at signals. The report turns that gap into a what-if: a dropdown sets how much of it to close.",
                  "Closing all of it on uncontrolled roads would avoid about 1,744 fatal collisions (54.09%). Treating curved roads like straight ones would avoid about 459 (14.25%), and making night as safe as midday about 402 (12.46%)."],
          note: "A scenario, not a forecast: it assumes the gap is caused by the road, uses no traffic volumes, and the three levers overlap.",
          tabs: [], src: "Avoided = fatal collisions on the risky roads x (1 - safer share / risky share) x share of the gap closed." },
        { n: "04 \u00b7 PEOPLE", ch: 3, title: "Occupants with no safety device used die 16 times as often",
          paras: ["Among drivers and passengers, 6.98% of those with no safety device used die, against 0.43% of those who used one: 16.09 times as often. The gap holds in every age band, at 7.02% to 10.83% for ages 16 and over, against 0.30% to 1.05%.",
                  "Against the average person, motorcyclists die at 4.91 times the rate and pedestrians at 3.77 times, while drivers, the largest group, are at 0.76 times. People aged 65 and over are at 2.11 times."],
          note: "These are unadjusted comparisons in police-reported data. The 6.98% rests on 7,939 occupants (554 deaths), with a 95% interval of 6.44% to 7.56%.",
          tabs: [], src: "Source: Transport Canada, National Collision Database. Unknown safety-device records (16%) are left out." },
        { n: "05 \u00b7 DATA QUALITY", ch: 4, title: "The file has a hidden collision ID, and some fields are mostly unknown",
          paras: ["The data dictionary lists no collision ID. My first version derived one from row order and found 185,359 collisions. The file holds a key, C_CASE, that the dictionary does not mention: it gives 185,772 collisions, severity, hour, weather and road surface never change inside a case, and every fatal collision has a death.",
                  "I also removed 7,416 dummy rows (a parked car gets a dummy person, a pedestrian a dummy vehicle). Every dimension has an unknown member, so no record disappears from a chart. Safety device is the most often unknown field, at 21.99%."],
          note: "Two collisions have no recorded month, so they leave the monthly charts. Full-year numbers include them.",
          tabs: [], src: "Checks are in the SQL file in the project folder." }
      ],
      recs: [
        { who: "Claims and underwriting analytics lead", title: "Monitor the fatal share, not only the count", text: "In 2020 collisions fell 24.38% but fatal ones only 1.29%. A falling count can hide a rising share of serious outcomes.", measure: "Measure: fatal share, by year" },
        { who: "Risk and portfolio manager", title: "Put night, single-vehicle, curved and uncontrolled roads on the watch list", text: "Night is 2.24 times as likely to be fatal, and no traffic control carries 72.84% of fatal collisions. They carry far more fatal outcomes than their share of collisions.", measure: "Measure: fatal share by condition, with collisions and fatal counts" },
        { who: "Road safety communications", title: "Use the safety-device gap in safe-driving messaging", text: "Occupants with no safety device used die at 6.98% against 0.43%. Use it as a message, not as a claim or pricing input.", measure: "Measure: fatality rate, no device used against device used" }
      ],
      recNote: "These are proposals for discussion from police-reported public data. They are not claims, pricing or safety advice.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Transport Canada", s: "Open CSVs for 2019 and 2020 under the Open Government Licence; every code checked against the data dictionary" },
        { i: "02 \u00b7 PREPARE", b: "Python and SQLite", s: "Found the real collision ID, cast mixed code formats, kept unknown codes as unknown and removed 7,416 dummy rows" },
        { i: "03 \u00b7 CHECK", b: "SQL checks", s: "Unique collision ID, every person has a collision, every severity is fatal or injury, and every headline number against SQL" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "Two fact tables, 15 dimensions with unknown members, a date table and 102 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "7 pages: heat map, time intelligence, a what-if scenario, a decomposition tree and a data-quality page" }
      ]
    }
  },
  {
    id: "toronto-311",
    sector: "Public sector",
    area: "City operations",
    title: "Half of Toronto's parks and forestry requests are recorded as open: what is 311 telling the city?",
    summary: "1.35 million 311 requests from 2023 to 2025: what drives demand, which divisions leave requests unresolved, and a change in request types that breaks year-over-year comparisons.",
    provenance: "Real",
    source: "Open Data Toronto, 311 Service Requests - Customer Initiated (Open Government Licence - Toronto)",
    tools: ["Power BI", "Power Query", "DAX", "SQL", "Python"],
    headline: { value: "49.45%", label: "of 2025 parks, forestry and environment requests are recorded as open, against 1.37% to 6.60% in every other division" },
    question: "Where does the city leave requests unresolved, and what is behind the growth in 311 demand?",
    data: "Customer-initiated 311 requests for 2023, 2024 and 2025: 1,351,594 rows with creation time, status, location (postal area or intersection), ward, request type, division and section. There is no close date, so time to close cannot be measured.",
    approach: [
      "Download the three yearly files and repair about 8% of rows where an unquoted comma split the division name into two fields.",
      "Group the Parks and Forestry division with its 2025 successors, since it was renamed and split.",
      "Group status into Resolved, Cancelled, Open and Unknown, and reconcile row counts against the source files.",
      "Run ten SQL queries for volume, outcomes, divisions, types and seasonality, then build the Power BI report from a monthly summary table."
    ],
    found: [
      "Requests grew from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025, up 14.47% in 2025.",
      "Parks, forestry and environment is the outlier: 49.45% of its 2025 requests are recorded as open (18,597 of 37,611), and so are 44.66% of its 2023 requests (12,637 of 28,298). Every other division is between 1.37% and 6.60% open. General pruning is 66% open and tree removal 73%.",
      "The request-type list changed in January 2025: 255 type names appear only in 2025 and cover 58.17% of that year's requests (for example, bin lid repairs were renamed). Growth by type cannot be compared across that boundary.",
      "Between 2023 and 2024, the fastest-growing named types were litter and illegal dumping cleanup (+46.8%) and bin lid repair or replacement (+36.6%).",
      "10.33% of 2025 requests were cancelled, but dead-wildlife pick-up was cancelled 38.84% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%.",
      "February 2025 had 53,707 requests, against 24,871 in February 2024. 19,876 of them were snow-related types that exist only from January 2025, so I cannot tell how much was more demand and how much better capture."
    ],
    recommend: [
      "Check whether the old open forestry requests are a real backlog or statuses that were never updated, and publish expected waits for pruning and tree removal.",
      "Add the closed date to the open dataset. It is the single most useful missing field.",
      "Publish a mapping table whenever request types are renamed, so year-over-year comparisons stay possible.",
      "Review the cancel-heavy types, such as dead-wildlife pick-up and missed recycling, to test whether duplicate or repeat calls are behind the cancellations. This is a hypothesis I have not tested."
    ],
    impact: [
      { action: "Audit the open parks, forestry and environment requests and publish expected waits for pruning and tree removal.", owner: "Division lead, Parks, Forestry and Environment", track: "Open share of the division's requests: 49.45% in 2025, against 1.37% to 6.60% elsewhere." },
      { action: "Add a closed date to the open dataset so time to close can be measured.", owner: "Open data and 311 data team", track: "Share of requests with a measurable time to close: 0% today." },
      { action: "Publish a mapping table whenever request types are renamed.", owner: "311 data owner", track: "Share of requests under renamed or new types that map back to a prior type: 58.17% of 2025 requests are affected today." },
      { action: "Test whether duplicate or repeat calls drive cancellations on the cancel-heavy types. This is a hypothesis, not a finding.", owner: "311 service operations", track: "Cancelled share: 10.33% overall in 2025, 38.84% for dead-wildlife pick-up." }
    ],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/toronto-311-report.pdf", note: "All five report pages, as exported from Power BI Desktop." },
      { label: "Download the Power BI project (.zip)", file: "downloads/toronto-311-powerbi-project.zip", note: "The .pbip project with the model, measures and pages, plus the monthly summary CSV. Open it in Power BI Desktop (free); the README inside says how to set the CSV path." }
    ],
    story: {
      bottom: "one division leaves about half its requests open, and request type names changed in 2025, so the 14.47% rise in demand cannot be split into more problems and new labels. The extract has no close date, so open means open at extraction, not a confirmed backlog, and time to close cannot be measured.",
      toc: true,
      terms: "311 = Toronto's city line for non-emergency service requests. Open = status Open or In Progress when the data was taken. Division = the city department handling the request. Taxonomy era = whether a request type name existed before or only after January 2025.",
      next: ["Add the closed date to the open dataset so time to close can be measured.", "Build a mapping from old to new request types to restore year-over-year comparison.", "Test whether duplicate calls explain the cancellations on dead-wildlife and missed-pickup requests."],
      dek: "When Toronto residents see a problem, such as a missed garbage pickup, a fallen tree or a pothole, they report it to the city by calling 311. I studied 1.35 million of these reports from 2023 to 2025 to find out which kinds of problems the city leaves unresolved, and whether the rise in reports means more problems or just a change in how they are labelled.",
      chips: ["SQL (10 queries)", "Python data repair", "Power Query", "Star schema", "DAX time intelligence", "Drill-through", "Data-quality page", "Dynamic card titles", "Data cleaning (1.35M rows)", "PBIP + TMDL in Git"],
      meta: [
        { k: "Data", v: "City of Toronto Open Data, 311 Service Requests, 2023 to 2025 (real, Open Government Licence)" },
        { k: "Scope", v: "1,351,594 requests, 7 divisions, 829 request types" },
        { k: "Tools", v: "Power BI, DAX, Power Query, SQL, Python" },
        { k: "My role", v: "End to end: repaired a broken CSV, checked the data in SQL and Python, built the star-schema model and DAX, designed the five-page report and wrote the findings" },
        { k: "Source links", links: [{"v": "Open Data Toronto: 311 Service Requests", "href": "https://open.toronto.ca/dataset/311-service-requests-customer-initiated/"}] }
      ],
      findings: [
        "Half of parks and forestry requests are recorded as open: 49.45% in 2025, against 1.37% to 6.60% in every other division.",
        "Demand grew 14.47% in 2025, to 500,269 requests, but request type names changed that year, so growth by type is not comparable.",
        "58.17% of 2025 requests sit under renamed or new request types, so year-over-year growth by type is not valid.",
        "Dead-wildlife pick-up is cancelled 38.84% of the time, the highest of any large request type."
      ],
      chapters: [
        { n: "01 \u00b7 DEMAND", ch: 0, title: "Demand rose 14.47%, but type names changed in 2025",
          paras: ["Requests went from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025.",
                  "February 2025 alone had 53,707 requests, against 24,871 a year earlier, and 19,876 of them were snow types that only exist from January 2025. Type labels changed, so growth by type is not comparable across the boundary."],
          note: "With this data I cannot separate more demand from better capture.",
          tabs: ["By month", "By year"], src: "Source: Open Data Toronto, 311 Service Requests, 2023 to 2025." },
        { n: "02 \u00b7 WHERE IT STALLS", ch: 1, title: "One division leaves half its requests open",
          paras: ["49.45% of 2025 requests in parks, forestry and environment are open, and so are 44.66% of its 2023 requests, so these are old requests and not only recent ones. Every other division is between 1.37% and 6.60%.",
                  "Inside the division, general pruning is 66.2% open and tree removal 73.3%."],
          note: "An open status could mean a real backlog or a status nobody updated. The data cannot separate the two.",
          tabs: ["By division", "By division and year", "Forestry types"], src: "Open = status Open or In Progress at the data snapshot. No close date is published." },
        { n: "03 \u00b7 A NAMING TRAP", ch: 2, title: "Renamed request types break year-over-year growth",
          paras: ["255 type names appear only in 2025 and cover 58.17% of that year's requests. Bin lid repairs, for example, were renamed.",
                  "So type-level growth is only valid within 2023 to 2024 or within 2025. The report adds a Taxonomy Era filter and a warning instead of showing invalid growth rates."],
          note: "This is the trap of comparing years: what looks like growth can be a new label.",
          tabs: ["Renamed share", "February snow types"], src: "Type names compared between February 2024 and February 2025." },
        { n: "04 \u00b7 CANCELLATIONS", ch: 3, title: "Some request types are cancelled far more than others",
          paras: ["10.33% of 2025 requests were cancelled, but dead-wildlife pick-up was cancelled 38.84% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%.",
                  "Repeat or duplicate calls are one possible reason, but I have not tested it."],
          note: "Shown for 2025 request types with at least 5,000 requests.", tabs: [], src: "Source: Open Data Toronto, 311 Service Requests, 2025." }
      ],
      recs: [
        { who: "Parks, Forestry and Environment lead", title: "Audit the open requests and publish expected waits", text: "Check whether the old open requests are a real backlog or statuses never updated, then set expected waits for pruning and tree removal.", measure: "Measure: open share, 49.45% in 2025" },
        { who: "311 data team", title: "Publish a closed date and a type-rename mapping", text: "A closed date makes time to close measurable. A mapping table keeps year-over-year comparisons valid when types are renamed.", measure: "Measure: share of requests with a time to close" },
        { who: "311 service operations", title: "Test why some types are cancelled so often", text: "Check whether duplicate or repeat calls drive cancellations on dead-wildlife and missed-pickup requests. This is a hypothesis, not a finding.", measure: "Measure: cancelled share, 10.33% overall" }
      ],
      recNote: "These are proposals. The data has no before-and-after, so I do not claim a measured effect.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Open Data Toronto", s: "Three yearly request files, 1,351,594 rows" },
        { i: "02 \u00b7 PREPARE", b: "Python and SQL", s: "Repaired about 8% of rows broken by an unquoted comma; grouped statuses and the renamed division" },
        { i: "03 \u00b7 CHECK", b: "Reconciliation", s: "Ten SQL queries; totals, yearly counts and shares reconciled to the report" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "One fact table of monthly counts, four dimensions, 61 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "5 pages with drill-through, icon number cards, a data-quality page and a custom theme" }
      ]
    },
    brief: {
      findings: [
        "Half of parks and forestry requests are recorded as open: 49.45% in 2025, against 1.37% to 6.60% in every other division.",
        "Demand grew 14.47% in 2025, to 500,269 requests, but request type names changed that year, so growth by type is not comparable.",
        "58.17% of 2025 requests sit under renamed or new request types, so year-over-year growth by type is not valid.",
        "Dead-wildlife pick-up is cancelled 38.84% of the time, the highest of any large request type."
      ],
      skills: [
        { skill: "Data modelling", proof: "Star schema with a date table and 61 DAX measures, reconciled to SQL." },
        { skill: "Data cleaning", proof: "Repaired about 8% of 1.35 million rows broken by an unquoted comma." },
        { skill: "DAX and time intelligence", proof: "Year-over-year, variables and dynamic card subtitles." },
        { skill: "Report design", proof: "5 pages with drill-through, icon number cards, a data-quality page and a custom theme." },
        { skill: "SQL and Python", proof: "Ten SQL queries and a Python loader behind the report." },
        { skill: "Analytical judgement", proof: "Refused invalid comparisons and stated the limits of the data." }
      ],
      help: [
        { title: "Find where the problem is", text: "I turned a million rows into one clear answer: which division leaves requests unresolved." },
        { title: "Make the numbers trustworthy", text: "Every figure is reconciled to the source, and I flag where the data cannot support a conclusion." },
        { title: "Hand over something you can run", text: "A documented Power BI project, with navigation and findings on every page, that others can open and extend." }
      ]
    },
    stats: [
      {
        "value": "5",
        "label": "report pages",
        "sub": "+ a drill-through page"
      },
      {
        "value": "46",
        "label": "data visuals",
        "sub": "cards, charts, slicers, tables"
      },
      {
        "value": "6",
        "label": "tables",
        "sub": "1 fact, 4 dimensions, 1 measures"
      },
      {
        "value": "4",
        "label": "relationships",
        "sub": "one-to-many, single direction"
      },
      {
        "value": "61",
        "label": "DAX measures",
        "sub": "all in one measures table"
      }
    ],
    techniques: ["Star schema", "Date table", "Year-over-year with SAMEPERIODLASTYEAR", "DAX variables", "Dynamic card subtitles", "Drill-through page", "Reset-filters bookmark", "Year slicer defaulting to the latest year", "Icon number cards", "Data-quality page", "Custom theme (JSON)", "PBIP + TMDL project"],
    impactNote: "These are proposals. The data has no before-and-after, so I do not claim a measured effect.",
    pitfalls: [
      { title: "A broken CSV", text: "About 8% of rows had an unquoted comma inside the division name, which shifted every later column. I repaired them in the loader and reconciled row counts against the source files." },
      { title: "Two spellings, one type", text: "SQL counted 255 renamed types and the model counts 254, because \"Picked\" and \"PIcked\" differ only by case and DAX merges them. Request totals match exactly." },
      { title: "Status is a snapshot", text: "With no close date, open share is a status at extraction time, so I never trend it as if it were a rate. Cards only compare same-year or same-volume figures." },
      { title: "Renamed types break year-over-year", text: "Type names changed in January 2025. I added an era flag to the type dimension and a warning on the Types page rather than show invalid growth rates." },
      { title: "A February spike with two explanations", text: "February 2025 requests more than doubled on February 2024, but 19,876 were snow types that only exist from 2025. I report it as unresolved: more demand, better capture, or both." }
    ],
    limits: [
      "No close date: I report request status as of the data snapshot, not how long anything took.",
      "An open status could mean a genuine backlog or a status never updated. The data cannot separate the two.",
      "Request type names changed in January 2025, so type-level comparisons are valid only within 2023 to 2024 or within 2025.",
      "Ward counts are not adjusted for population, and requests reflect who reports as well as where problems occur.",
      "1.5% of requests have an Unknown status and are excluded from the resolved share."
    ],
    repo: "03-government-311",
    hero: 2,
    shots: [
      { file: "images/01-start.png", caption: "Start here: the question, four headline numbers and how to use the report" },
      { file: "images/02-overview.png", caption: "Overview: demand by month, key findings and year-over-year change" },
      { file: "images/03-outcomes.png", caption: "Outcomes: share of requests recorded as open by division, with drill-through to request types" },
      { file: "images/04-types.png", caption: "Request types: top types, taxonomy-era filter and the naming-change warning" },
      { file: "images/05-quality.png", caption: "Data quality: what the file covers, the repaired rows and the limits of the data" }
    ],
    kpis: [
      { label: "Requests in 2025", value: "500,269", sub: "\u25b2 14.47% vs 2024", icon: "bars" },
      { label: "Resolved", value: "80.52%", sub: "of 2025 requests", icon: "check" },
      { label: "Recorded as open", value: "7.77%", sub: "of 2025 requests", icon: "clock" },
      { label: "Parks & forestry recorded as open", value: "49.45%", sub: "\u25b2 vs 1.37% to 6.60% elsewhere", icon: "warn" }
    ],
    facts: [
      { label: "Busiest month in 2025", value: "Feb 2025", sub: "53,707 requests, lifted by new snow request types" },
      { label: "Quietest month in 2025", value: "Jan 2025", sub: "32,793 requests" },
      { label: "Parks & forestry share of open requests", value: "47.9%", sub: "of all open requests, from 7.5% of requests" }
    ],
    glance: [
      { value: "1,351,594", label: "requests, 2023 to 2025" },
      { value: "829", label: "request types, each in one division" },
      { value: "7", label: "divisions" },
      { value: "295,239", label: "rows after monthly summary" }
    ],
    chapters: [
      {
        title: "Demand rose 14.47% in 2025",
        text: "Requests went from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025. Part of the February 2025 spike comes from snow-related request types that only exist from January 2025, so the true rise in demand is smaller than the headline suggests.",
        stat: { value: "+14.47%", label: "more requests in 2025 than in 2024" },
        visuals: [
          { ref: 1 },
          { type: "bar", orient: "v", title: "Requests by year", labels: ["2023", "2024", "2025"], values: [414282, 437043, 500269], unit: "requests", highlight: 2 }
        ]
      },
      {
        title: "Half of parks and forestry requests are recorded as open",
        text: "49.45% of 2025 requests in parks, forestry and environment are open, and so are 44.66% of its 2023 requests, so these are old requests and not only recent ones. Every other division is between 1.37% and 6.60%. Within the division, general pruning is 66.2% open and tree removal 73.3%. The data cannot say whether this is a backlog or statuses nobody updated.",
        stat: { value: "49.45%", label: "of 2025 parks, forestry and environment requests are open" },
        visuals: [
          { ref: 0 },
          {
            type: "bar", grouped: true, title: "Share recorded as open, by division and year",
            labels: ["Parks, Forestry & Environment", "Transportation Services", "Toronto Water", "Municipal Licensing & Standards", "Solid Waste Management", "311"],
            datasets: [
              { label: "2023", values: [44.7, 14.3, 12.2, 5.5, 1.2, 9.4] },
              { label: "2024", values: [51.5, 9.3, 7.1, 8.1, 1.2, 2.9] },
              { label: "2025", values: [49.4, 6.6, 5.7, 5.6, 1.7, 1.4] }
            ],
            unit: "% recorded as open", suffix: "%"
          },
          {
            type: "bar", title: "Parks, forestry and environment: share recorded as open, by request type (2023 to 2025)",
            labels: ["Residential or Park Tree Removal", "Stemming", "General Pruning", "General Tree Maintenance", "Tree Emergency Clean-Up", "Storm Clean Up", "By-Law Contravention Invest", "Dangerous Private Tree Investigation"],
            values: [73.3, 68.2, 66.2, 62.0, 37.0, 29.8, 11.7, 2.6], unit: "% recorded as open", suffix: "%"
          }
        ]
      },
      {
        title: "Request types were renamed in January 2025",
        text: "255 type names appear only in 2025 and cover 58.17% of that year's requests. Type-level growth is only valid within 2023 to 2024 or within 2025, so the report adds a Taxonomy Era filter instead of comparing across the break.",
        stat: { value: "58.17%", label: "of 2025 requests use type names introduced in January 2025" },
        warn: true,
        visuals: [
          { type: "doughnut", title: "2025 requests by type-name status", labels: ["Under renamed or new types", "Other requests"], values: [290985, 209284], unit: "requests" },
          { type: "bar", title: "February 2025 requests for type names that did not exist in February 2024", labels: ["Sidewalk Snow Clearing Required", "Road Plowing Request", "Driveway Blocked By Plowed Snowbank", "Snow at Intersections - Impeded Mobility", "Residential Bin Lid Damaged", "Road Pothole / Road Damage"], values: [8722, 4987, 3811, 1248, 1233, 1154], unit: "requests" }
        ]
      },
      {
        title: "Some types are cancelled far more often than others",
        text: "10.33% of 2025 requests were cancelled overall, but dead-wildlife pick-up was cancelled 38.84% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%. Duplicate or repeat calls are one possible reason; I have not tested it.",
        stat: { value: "38.84%", label: "of dead-wildlife pick-up requests were cancelled in 2025" },
        visuals: [
          {
            type: "bar", title: "Share cancelled in 2025, 10 highest among types with 5,000+ requests",
            labels: ["Pick up Dead Wildlife", "Res / Recycle / Not Picked Up", "Clean up Illegal Dumping on City Road Allowance", "Res / Garbage / Not Picked Up", "Residential Furniture / Not Picked Up", "Res / Organic Green Bin / Not Picked Up", "Injured - Wildlife", "Long Grass and Prohibited Plants on Private Property", "Waste or Illegal Dumping on Private Property", "Zoning Regulations Violations"],
            values: [38.8, 28.6, 28.0, 26.7, 23.7, 20.1, 14.1, 11.5, 10.8, 9.4], unit: "% cancelled", suffix: "%", highlight: 0
          }
        ]
      }
    ],
    model: {
      intro: "The report is built on a star schema: one fact table of monthly request counts, and four small dimension tables that hold the names, so filters are fast and every measure reads the same way.",
      tables: [
        { name: "requests", role: "Fact", short: "295,239 monthly rows", rows: "295,239 monthly summary rows (1,351,594 requests)" },
        { name: "Date", role: "Dimension", short: "2023 to 2025 calendar", rows: "Calendar 2023 to 2025, marked as the date table" },
        { name: "Dim_Division", role: "Dimension", short: "7 divisions", rows: "7 divisions" },
        { name: "Dim_ServiceType", role: "Dimension", short: "829 types, era flag", rows: "829 request types, each in one division, with a Taxonomy Era flag" },
        { name: "Dim_Status", role: "Dimension", short: "4 statuses, fixed order", rows: "4 statuses in a fixed order: Resolved, Open, Cancelled, Unknown" }
      ],
      measures: [
        { name: "Open %", dax: "DIVIDE (\n    [Open],\n    [Requests]\n)" },
        { name: "Requests PY", dax: "CALCULATE (\n    [Requests],\n    SAMEPERIODLASTYEAR ( 'Date'[Date] )\n)" },
        { name: "Requests YoY %", dax: "DIVIDE (\n    [Requests] - [Requests PY],\n    [Requests PY]\n)" },
        { name: "Parks Open %", dax: "CALCULATE (\n    [Open %],\n    Dim_Division[Division] = \"Parks, Forestry & Environment\"\n)" },
        { name: "Open Type Peak %", dax: "VAR t =\n    FILTER (\n        ADDCOLUMNS (\n            VALUES ( Dim_ServiceType[Service Type] ),\n            \"r\", [Requests],\n            \"p\", [Open %]\n        ),\n        [r] >= 100 && NOT ISBLANK ( [p] )\n    )\nVAR tp =\n    TOPN ( 1, t, [p], DESC )\nRETURN\n    MAXX ( tp, [p] )" }
      ],
      note: "Imported from a 33 MB monthly summary of the full request file, so the report stays fast. Results were reconciled against the SQL: totals, yearly counts, open share by division and the 58.17% renamed-type share all match."
    },
    charts: [
      {
        type: "bar",
        title: "Share of 2025 requests recorded as open, by division",
        labels: ["Parks, Forestry & Environment", "Transportation Services", "Toronto Water", "Municipal Licensing & Standards", "Solid Waste Management", "311"],
        values: [49.4, 6.6, 5.7, 5.6, 1.7, 1.4],
        unit: "% recorded as open",
        suffix: "%",
        highlight: 0
      },
      {
        type: "line",
        title: "311 requests per month, 2023 to 2025",
        labels: ["2023-01","2023-02","2023-03","2023-04","2023-05","2023-06","2023-07","2023-08","2023-09","2023-10","2023-11","2023-12","2024-01","2024-02","2024-03","2024-04","2024-05","2024-06","2024-07","2024-08","2024-09","2024-10","2024-11","2024-12","2025-01","2025-02","2025-03","2025-04","2025-05","2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12"],
        values: [34341,31102,39698,36159,41643,41170,39723,37091,33623,30043,27423,22266,32203,24871,26629,33340,45424,44253,47275,43477,41517,38041,32460,27553,32793,53707,37317,38111,44571,46971,48120,43555,44851,37840,33525,38908],
        unit: "requests"
      }
    ]
  },
  {
    id: "federal-contracts",
    sector: "IT consulting",
    area: "Fabric lakehouse",
    title: "Who wins federal contracts, and how competitive are the awards?",
    summary: "Federal contracts over $10,000 in a Fabric lakehouse, modelled as a star schema for spend, competition, amendments and vendor concentration.",
    provenance: "Real",
    source: "Treasury Board of Canada Secretariat, Proactive Publication - Contracts",
    tools: ["Fabric", "PySpark", "Power BI", "DAX", "Row-level security"],
    headline: { value: null, label: "share of contract value awarded without open competition" },
    question: "How is federal contract money distributed, how often is it competed, and how much do contracts grow after award?",
    data: "A roughly 655 MB file of disclosed contracts over $10,000, published up to several months after award.",
    approach: [
      "Land the file in a lakehouse and build bronze, silver and gold Delta tables.",
      "Create a star schema with a semantic model, documented measures and a department-level security example.",
      "Reconcile row counts and total value at every layer.",
      "Write a handover document: refresh approach, data dictionary, known limits."
    ],
    found: [],
    recommend: [],
    limits: [
      "The latest months are incomplete because of the publication delay.",
      "Vendor names are not standardised, so concentration figures are approximate.",
      "Whether a procedure counts as competitive depends on how I group the procedure codes, which I document."
    ],
    repo: "04-consulting-fabric-procurement",
    chart: null
  },
  {
    id: "substance-harms",
    sector: "Healthcare",
    area: "Public health",
    title: "Opioid deaths are down 29.43%, but ambulance calls are not: what is Canada's data telling us?",
    summary: "Hospital stays, emergency visits, ambulance calls and deaths across Canada, with a clear view of what each number covers.",
    provenance: "Real",
    source: "Public Health Agency of Canada, Opioid- and Stimulant-related Harms in Canada (Health Infobase)",
    tools: ["Power BI", "DAX", "SQL", "Python"],
    headline: { value: "-29.43%", label: "opioid deaths in 2025 against the 2023 peak, while EMS responses fell only 7.84%" },
    question: "Which harm measures are falling, which are not, and where is the burden greatest, so a public health team knows where to plan?",
    data: "Published aggregated counts and rates by province or territory, year and quarter, for hospital stays, emergency department visits, EMS responses and deaths. Small counts are suppressed.",
    approach: [
      "Download the open CSV and profile every column before defining any measure.",
      "Rebuild the chart export as three tables and check what each value means.",
      "Build a Power BI report: four measures side by side, trend, provinces and who.",
      "Show suppressed and missing values as such, never as zero."
    ],
    found: [
      "Opioid deaths jumped from 3,602 in 2019 to 6,184 in 2020, peaked at 8,083 in 2023 and were 5,704 in 2025, down 29.43%.",
      "Against their peaks, hospital stays are down 21.75% and emergency department visits 28.51%, but EMS responses are down only 7.84%, and early 2026 is the highest quarter on record.",
      "In 2024 the opioid death rate was 35.7 per 100,000 in British Columbia, 24.4 in Alberta, 14.0 in Ontario and 3.4 in Quebec.",
      "About 71.64% of opioid deaths in 2024 were men, and 52.58% were aged 30 to 49."
    ],
    recommend: [
      "Track EMS responses and emergency department visits next to deaths: deaths alone understate the ongoing burden.",
      "Start with the high-rate places (British Columbia, Yukon, Manitoba, Alberta, Saskatchewan: 22 to 36 per 100,000 in 2024), using the same year for every place.",
      "Aim outreach at men aged 30 to 49, the largest group."
    ],
    limits: [
      "Provinces report differently, so rankings are a prompt for questions, not a verdict.",
      "Rates are crude, not age-adjusted, and counts depend on population size.",
      "A Canada total only adds up the places that report: hospital stays leave out Quebec and emergency department visits cover 7 of 13 provinces and territories.",
      "Some 2025 provincial values look provisional (Ontario deaths fell 37.49% and Quebec rose 93.14% in a year), so the report compares provinces on 2024.",
      "Small counts are suppressed, so age and sex cells in small regions are blank.",
      "No patient-level data, so no conclusions about individuals."
    ],
    repo: "05-healthcare-opioid-harms",
    hero: 1,
    shots: [
      { file: "images/oh-1-start.png", caption: "Start here: four headline numbers, what the data shows and what I would do" },
      { file: "images/oh-2-four.png", caption: "Four measures: deaths, hospital stays, ED visits and EMS responses side by side" },
      { file: "images/oh-3-trend.png", caption: "Trend: quarterly counts for one source and substance, with yearly totals" },
      { file: "images/oh-4-provinces.png", caption: "Provinces: a tile map of rates, with suppressed and missing values labelled" },
      { file: "images/oh-5-who.png", caption: "Who: a heat map of counts by age group and year, with the sex split" },
      { file: "images/oh-6-quality.png", caption: "Data quality: who reports what, and what I did about missing values" }
    ],
    kpis: [
      { label: "Opioid deaths, 2025", value: "5,704", sub: "\u25bc from 8,083 (2023)", icon: "bars" },
      { label: "Deaths against the peak", value: "-29.43%", sub: "Hospital stays -21.75%, ED visits -28.51%", icon: "check" },
      { label: "EMS against the peak", value: "-7.84%", sub: "2026 Q1 is +60.93% on a year ago", icon: "clock" },
      { label: "Hospital stays per death", value: "0.88", sub: "Sources differ in coverage; read the trend only", icon: "warn" }
    ],
    stats: [
      {
        "value": "6",
        "label": "report pages",
        "sub": ""
      },
      {
        "value": "51",
        "label": "data visuals",
        "sub": ""
      },
      {
        "value": "11",
        "label": "tables",
        "sub": "3 data, 7 helper, 1 measures"
      },
      {
        "value": "14",
        "label": "relationships",
        "sub": ""
      },
      {
        "value": "95",
        "label": "DAX measures",
        "sub": ""
      }
    ],
    techniques: ["Star schema", "Date table", "Slicer defaults in DAX", "Tile-grid map", "Heat map by DAX colour", "Suppression handling", "Data-quality page", "PBIP + TMDL project"],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/opioid-harms-report.pdf", note: "All six report pages, as exported from Power BI Desktop." },
      { label: "Download the Power BI project (.zip)", file: "downloads/opioid-harms-powerbi-project.zip", note: "The .pbip project plus the model CSVs. The README inside says how to set the CSV folder." }
    ],
    chapters: [
      { visuals: [{ ref: 0 }] },
      { visuals: [{ ref: 1 }] },
      { visuals: [{ ref: 2 }] },
      { visuals: [{ ref: 3 }] },
      { visuals: [{ ref: 4 }] }
    ],
    charts: [
      {"type": "bar", "orient": "v", "title": "Opioid deaths in Canada by year", "labels": ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"], "values": [2832, 3928, 4262, 3602, 6184, 7617, 7274, 8083, 6669, 5704], "unit": "deaths", "highlight": 7},
      {"type": "line", "title": "Opioid counts compared with 2019 (2019 = 100)", "labels": ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"], "unit": "index", "noLabels": true, "datasets": [{"label": "Deaths", "color": "#1B3A5C", "values": [79.0, 109.0, 118.0, 100.0, 172.0, 211.0, 202.0, 224.0, 185.0, 158.0]}, {"label": "Hospital stays", "color": "#2A7F8E", "values": [102.0, 114.0, 112.0, 100.0, 116.0, 139.0, 121.0, 144.0, 125.0, 113.0]}, {"label": "Emergency department visits", "color": "#C77700", "values": [65.0, 93.0, 100.0, 100.0, 124.0, 179.0, 133.0, 156.0, 135.0, 128.0]}, {"label": "EMS responses", "color": "#8A9BAE", "values": [null, 81.0, 97.0, 100.0, 138.0, 192.0, 166.0, 199.0, 168.0, 184.0]}]},
      {"type": "bar", "title": "Opioid death rate per 100,000: 2024, and 2025 (provisional)", "labels": ["British Columbia", "Yukon", "Manitoba", "Alberta", "Saskatchewan", "Canada", "Northwest Territories", "Ontario", "New Brunswick", "Newfoundland and Labrador", "Nova Scotia", "Prince Edward Island", "Quebec"], "unit": "per 100,000", "datasets": [{"label": "2024", "color": "#1B3A5C", "values": [35.7, 29.4, 25.0, 24.4, 21.8, 16.2, 15.5, 14.0, 10.0, 8.6, 6.2, 4.5, 3.4]}, {"label": "2025 (provisional)", "color": "#8A9BAE", "values": [32.6, 29.0, 15.3, 22.9, 18.7, 13.7, 4.4, 8.7, 9.9, 4.9, 7.0, 7.1, 6.5]}]},
      {"type": "bar", "orient": "v", "title": "Opioid deaths by age group and sex, 2024", "labels": ["0 to 19 years", "20 to 29 years", "30 to 39 years", "40 to 49 years", "50 to 59 years", "60 years or more"], "unit": "deaths", "datasets": [{"label": "Female", "values": [44, 332, 520, 441, 311, 219], "color": "#2A7F8E"}, {"label": "Male", "values": [54, 649, 1334, 1167, 885, 628], "color": "#1B3A5C"}]},
      {"type": "bar", "title": "What the 34,890 rows contain", "labels": ["Numbers (5.11% are real zeros)", "Blank: not available", "Suppressed: small counts"], "values": [62.08, 24.82, 13.09], "unit": "% of rows", "suffix": "%", "decimals": 2, "highlight": 0}
    ],
    model: {
      measures: [
        { name: "Count", dax: "VAR scoped = ISFILTERED ( Dim_Region )\nRETURN\n    IF (\n        scoped,\n        SUM ( fact_year[number] ),\n        CALCULATE (\n            SUM ( fact_year[number] ),\n            Dim_Region[Region] = \"Canada\"\n        )\n    )" },
        { name: "Rate (Focus Year)", dax: "VAR y = [Focus Year]\nVAR s = [Sel Source]\nVAR sub = [Sel Substance]\nRETURN\n    CALCULATE (\n        [Rate per 100k],\n        REMOVEFILTERS ( Date ),\n        fact_year[year] = y,\n        Dim_Source[Source] = s,\n        Dim_Substance[Substance] = sub\n    )" },
        { name: "Opioid Deaths Peak", dax: "VAR yrs =\n    CALCULATETABLE (\n        VALUES ( fact_year[year] ),\n        REMOVEFILTERS ( Date ),\n        fact_year[partial_period] = 0\n    )\nRETURN\n    MAXX (\n        yrs,\n        CALCULATE (\n            [Count],\n            REMOVEFILTERS ( Date ),\n            Dim_Source[Source] = \"Deaths\",\n            Dim_Substance[Substance] = \"Opioids\"\n        )\n    )" },
        { name: "Coverage Status", dax: "CALCULATE (\n    IF (\n        COUNTROWS ( fact_year ) = 0,\n        \"Not in file\",\n        SELECTEDVALUE ( fact_year[number_status] )\n    ),\n    REMOVEFILTERS ( Date ),\n    fact_year[year] = 2024,\n    Dim_Substance[Substance] = \"Opioids\"\n)" },
        { name: "Tile Fill", dax: "VAR code = SELECTEDVALUE ( Dim_Region[Tile Code], \"\" )\nVAR r = [Rate (Focus Year)]\nVAR k = DIVIDE ( r, [Tile Max] )\nRETURN\n    IF (\n        code = \"\",\n        BLANK (),\n        IF (\n            ISBLANK ( r ),\n            \"#E3E3E3\",\n            SWITCH (\n                TRUE (),\n                k < 0.2, \"#E4ECF3\",\n                k < 0.4, \"#A9C3D9\",\n                k < 0.6, \"#5F8FB5\",\n                k < 0.8, \"#2D5F8A\",\n                \"#1B3A5C\"\n            )\n        )\n    )" }
      ]
    },
    story: {
      dek: "Hospitals, ambulance services and death records all count opioid and stimulant harms, but not in the same way or in the same places. I used the Public Health Agency of Canada's open data, 2016 to early 2026, to see which measures are falling, where the burden is greatest, and what each number really covers.",
      bottom: "deaths are falling faster than hospital and ambulance activity, so deaths alone understate the burden. Provinces differ several times over, and several Canada totals leave places out.",
      toc: true,
      terms: "EMS = ambulance calls (emergency medical services). ED = emergency department. Suppressed = small counts hidden by the agency to protect privacy. Crude rate = cases per 100,000 people, not adjusted for age.",
      next: ["Age-adjust the provincial rates with population data, so provinces with older or younger populations compare fairly.", "Add treatment and naloxone data to test whether falling deaths come from fewer overdoses or from more of them being survived.", "Re-run the report when the 2025 figures are final, and re-check the Ontario and Quebec changes."],
      chips: ["Python (pandas)", "SQL (SQLite checks)", "Power Query", "Star schema (3 facts)", "Advanced DAX", "Conditional formatting by DAX", "Heat map and tile map", "Data-quality profiling", "Suppression handling", "PBIP + TMDL in Git"],
      meta: [
        { k: "Data", v: "Public Health Agency of Canada, Opioid- and Stimulant-related Harms in Canada (real, aggregated)" },
        { k: "Scope", v: "2016 to Q1 2026, yearly and quarterly, four sources, 19 regions" },
        { k: "Tools", v: "Power BI, DAX, SQL, Python" },
        { k: "My role", v: "End to end: checked the data in SQL and Python, built the star-schema model and DAX, designed the six-page report and wrote the findings" },
        { k: "Source link", v: "PHAC Health Infobase, Open Government Licence - Canada (accessed November 2026)", href: "https://health-infobase.canada.ca/substance-related-harms/opioids-stimulants/" }
      ],
      findings: [
        "Opioid deaths jumped from 3,602 in 2019 to 6,184 in 2020, peaked at 8,083 in 2023 and were 5,704 in 2025, down 29.43%.",
        "Against their peaks, hospital stays are down 21.75% and emergency department visits 28.51%, but EMS responses are down only 7.84%, and early 2026 is the highest quarter on record.",
        "In 2024 the opioid death rate was 35.7 per 100,000 in British Columbia, 24.4 in Alberta, 14.0 in Ontario and 3.4 in Quebec.",
        "About 71.64% of opioid deaths in 2024 were men, and 52.58% were aged 30 to 49."
      ],
      chapters: [
        { n: "01 \u00b7 TREND", ch: 0, title: "Opioid deaths jumped in 2020 and have fallen since the 2023 peak",
          paras: ["Opioid deaths rose from 3,602 in 2019 to 6,184 in 2020, a jump of 71.68%. They peaked at 8,083 in 2023 and were 5,704 in 2025.",
                  "The rate per 100,000 went from 9.6 in 2019 to 20.2 in 2023 and 13.7 in 2025. Stimulant deaths followed the same shape: 5,395 in 2023 and 3,634 in 2025."],
          note: "The 2026 figure covers January to March only, so full years end at 2025.",
          tabs: [], src: "Source: Public Health Agency of Canada, Health Infobase." },
        { n: "02 \u00b7 FOUR MEASURES", ch: 1, title: "Deaths have fallen faster than ambulance calls",
          paras: ["Against their peaks, opioid deaths are 29.43% lower, hospital stays 21.75% lower and emergency department visits 28.51% lower, but EMS responses are only 7.84% lower.",
                  "In the first quarter of 2026 deaths were 5.31% below a year earlier while hospital stays were 13.55% higher and EMS responses 60.93% higher. Hospital stays per death fell from 1.62 in 2016 to 0.88 in 2025, but hospital and death counts come from sources with different coverage, so read the ratio as a trend, not an exact rate."],
          note: "The EMS rise in 2026 comes mostly from British Columbia and Winnipeg and may reflect how services record calls.",
          tabs: [], src: "Each line is shown as a percentage of its own 2019 value: 100 is the 2019 level, 150 is 50% higher and 80 is 20% lower. The sources count different things, so compare direction, not size." },
        { n: "03 \u00b7 PROVINCES", ch: 2, title: "Death rates differ several times between provinces",
          paras: ["In 2024 the opioid death rate was 35.7 per 100,000 in British Columbia, 29.4 in Yukon, 25.0 in Manitoba and 24.4 in Alberta, against 14.0 in Ontario and 3.4 in Quebec.",
                  "The lighter bars are 2025, which looks provisional: Ontario falls from 14.0 to 8.7 and Quebec rises from 3.4 to 6.5 in one year. That looks like reporting timing, so I compare provinces on 2024. The Canada rate (16.2 in 2024) only counts the places that report."],
          note: "Rates are crude, not age-adjusted, so use them to ask questions, not to rank provinces. The report opens on 2024.",
          tabs: [], src: "Source: Public Health Agency of Canada. Nunavut has no death rate for 2024 or 2025." },
        { n: "04 \u00b7 WHO", ch: 3, title: "Seven in ten deaths are men, and half are aged 30 to 49",
          paras: ["In 2024, 71.64% of opioid deaths were men and 52.58% were aged 30 to 49. Counts roughly doubled in every age group from 2019 to 2021 and are lower in every group than at the 2023 peak.",
                  "I show 2024 because the age and sex split covers 98.73% of its deaths, against 91.09% for 2025. The rest is suppressed because the counts are small."],
          note: "In smaller regions many age and sex cells are blank, because PHAC hides small counts to protect privacy.",
          tabs: [], src: "Source: Public Health Agency of Canada, age and sex counts." },
        { n: "05 \u00b7 DATA QUALITY", ch: 4, title: "A quarter of the file is blank, and Canada does not mean all of Canada",
          paras: ["The file is a chart export with 34,890 rows and 39 columns, not a table. 62.08% of values are numbers (5.11% are real zeros), 24.82% are blank and 13.09% are suppressed small counts. I keep the three apart and never show a missing value as zero.",
                  "A Canada total only adds up the places that report: hospital stays leave out Quebec and emergency department visits cover 7 of 13 provinces and territories. Quarters add up to as much as 1.57% less than the published year, so I never build a year from quarters."],
          note: "Every headline number was checked against a separate Python calculation.",
          tabs: [], src: "Checks are in the SQL file in the project folder." }
      ],
      recs: [
        { who: "Public health planner", title: "Track EMS and emergency visits next to deaths", text: "Deaths fell 29.43% from the peak, but EMS responses only 7.84%. Deaths alone understate the ongoing burden, so report all four measures together.", measure: "Measure: change from peak, by source" },
        { who: "Regional health lead", title: "Start with the high-rate places", text: "In 2024 British Columbia, Yukon, Manitoba, Alberta and Saskatchewan had rates of 22 to 36 per 100,000. Compare places on the same year, and ask how each reports.", measure: "Measure: death rate per 100,000, 2024" },
        { who: "Harm-reduction program lead", title: "Aim outreach at men aged 30 to 49", text: "This group is the largest: 71.64% of deaths are men and 52.58% are aged 30 to 49. Test the outreach against local data before spending.", measure: "Measure: share of deaths by age group and sex" }
      ],
      recNote: "These are proposals for discussion from public, aggregated data. They are not clinical advice.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Public Health Agency of Canada", s: "Open CSV from Health Infobase under the Open Government Licence, updated September 2026" },
        { i: "02 \u00b7 PREPARE", b: "Python and SQLite", s: "Turned the chart export into three tables; kept suppressed and blank values apart" },
        { i: "03 \u00b7 CHECK", b: "SQL checks", s: "Keys unique, Canada equals the places that report, quarters against years, and every headline number against Python" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "Three fact tables, six dimensions, a date table and 95 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "6 pages: indexed lines, tile map, heat map and a coverage grid" }
      ]
    }
  }
];

// Chart format when you have results (shown on the case page):
// chart: { type: "bar", title: "Fatal share by hour", labels: ["0","1"], values: [3.1, 2.8], unit: "%" }
