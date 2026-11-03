// All case-study content lives here. The site renders from this file.
// Any field set to null shows as a dashed "to fill in" placeholder, so nothing looks finished
// until you have run the analysis and typed in your own numbers.
window.PROFILE = {
  name: "Mihir Jasani",
  headline: "I build *Power BI reporting* that turns messy data into decisions.",
  intro: "I'm Mihir Jasani, a data analyst. I write the SQL, clean and reconcile the data, and build the Power BI dashboards that management uses to make decisions, most recently at Elevara Digital. I'm certified in Power BI (PL-300) and Microsoft Fabric (DP-600). My day-to-day work is confidential, so these five case studies use real Canadian public data. Each one is a short story: the question, the data, what I found and what I'd recommend.",
  email: "mailto:mihirjasani369@gmail.com",
  linkedin: "https://www.linkedin.com/in/mihir-jasani/",
  resume: null,
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
  aboutPortfolio: "This portfolio has five case studies built on public Canadian data: banking, health, transportation, government and city services. Each one lists its source and licence and states what the data cannot tell you. No employer or client data is used anywhere on this site.",
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
    title: "Do Canadian borrowers feel rate moves, and how fast?",
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
      "Compare YoY credit growth with rate changes at lags of 0 to 12 months, with a lag slicer.",
      "Document every DAX measure and its definition."
    ],
    found: [
      "Household credit grew from $1.5 trillion in January 2010 to $3.3 trillion in August 2026, 2.2 times as large.",
      "Credit growth peaked at 8.7% in May 2022 and slowed to 3.5% by October 2023, after the prime rate rose from 2.45% to 7.20%.",
      "Credit growth is lowest about 18 months after a rate rise, with a correlation of -0.52. At 6 months it is only -0.17.",
      "Debt payments took 15.2% of household income in early 2023, up from 12.6% in the April 2020 quarter, and are 14.5% now."
    ],
    recommend: [
      "Plan for a delayed response: expect credit growth to react to a rate change over about 1.5 years, not right away.",
      "Track the debt service ratio each quarter next to rates; it was 15.2% in early 2023 and is 14.5% now.",
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
    shots: [
      { file: "images/hc-1-start.png", caption: "Start here: the question, three findings and how to use the report" },
      { file: "images/hc-2-rates.png", caption: "Rates: policy, prime and 5-year mortgage rates, 2010 to 2026" },
      { file: "images/hc-3-credit.png", caption: "Credit: growth for the total and each category, with a scorecard" },
      { file: "images/hc-4-lag.png", caption: "Rate lag: pick a lag in months to compare credit growth with an earlier rate change" }
    ],
    kpis: [
      { label: "Household credit", value: "$3.3T", sub: "As of Aug 2026", icon: "bars" },
      { label: "Credit growth", value: "4.1%", sub: "\u25bc from 8.7% (May 2022)", icon: "clock" },
      { label: "Prime rate", value: "4.45%", sub: "\u25bc from 7.20% (Jul 2023)", icon: "check" },
      { label: "Strongest lag", value: "18 months", sub: "Correlation -0.52", icon: "warn" }
    ],
    stats: [
      { value: "4", label: "report pages", sub: "" },
      { value: "31", label: "data visuals", sub: "" },
      { value: "9", label: "tables", sub: "4 data, 4 helper, 1 measures" },
      { value: "5", label: "relationships", sub: "" },
      { value: "51", label: "DAX measures", sub: "" }
    ],
    techniques: ["Star schema", "Date table", "Year-over-year DAX", "Lag selector", "DAX variables", "Reset-filters bookmark", "Custom theme (JSON)", "PBIP + TMDL project"],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/household-credit-report.pdf", note: "All four report pages, as exported from Power BI Desktop." },
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
      {"type": "bar", "title": "Latest growth vs a year earlier, by category (Aug 2026)", "labels": ["Credit cards", "Non-mortgage loans", "Total household credit", "Home equity lines of credit", "Lines of credit", "Mortgage loans", "Personal loans", "Auto loans"], "values": [6.5, 4.9, 4.1, 3.9, 3.9, 3.8, 1.4, 1.0], "unit": "% growth", "suffix": "%", "highlight": 2},
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
      dek: "When the Bank of Canada raises interest rates, borrowing is supposed to cool. I used public Bank of Canada and Statistics Canada data from 2010 to 2026 to check how long that takes: how quickly Canadian household borrowing slowed after rates went up, and whether families ended up spending more of their income on debt payments.",
      chips: ["Star schema", "Date table", "Year-over-year DAX", "Lag selector", "DAX variables", "Reset-filters bookmark", "Custom theme"],
      meta: [
        { k: "Data", v: "Bank of Canada Valet API and Statistics Canada tables 36-10-0639, 38-10-0238 and 11-10-0065 (real, market-level)" },
        { k: "Scope", v: "202 months of rates, 8 credit categories and 66 quarters of debt service" },
        { k: "Tools", v: "Power BI, DAX, Power Query, Python" }
      ],
      findings: [
        "Household credit grew from $1.5 trillion in January 2010 to $3.3 trillion in August 2026, 2.2 times as large.",
        "Credit growth peaked at 8.7% in May 2022 and slowed to 3.5% by October 2023, after the prime rate rose from 2.45% to 7.20%.",
        "Credit growth is lowest about 18 months after a rate rise, with a correlation of -0.52. At 6 months it is only -0.17.",
        "Debt payments took 15.2% of household income in early 2023, up from 12.6% in the April 2020 quarter, and are 14.5% now."
      ],
      chapters: [
        { n: "01 \u00b7 RATES", ch: 0, title: "Interest rates rose fast in 2022 and 2023, then eased",
          paras: ["The prime rate went from 2.45% in February 2022 to 7.20% in July 2023, and stayed there for 11 months.",
                  "It has since eased to 4.45%. The 5-year mortgage rate peaked at 7.04% in October 2023 and is 6.19% now, 1.74 points above prime."],
          note: "Rates are shown to two decimals because that is how they are published.",
          tabs: [], src: "Source: Bank of Canada Valet API. Prime and mortgage rates are weekly, so each month shows the last weekly value." },
        { n: "02 \u00b7 CREDIT", ch: 1, title: "Credit growth slowed from 8.7% to about 4%",
          paras: ["Total household credit grew 8.7% a year at its May 2022 peak. Growth fell to 3.5% by October 2023 and is 4.1% now.",
                  "Mortgage growth peaked at 11.0% in February 2022 and is 3.8% now. Non-mortgage loans shrank 4.6% year over year in February 2021, during the pandemic, and first grew faster than mortgages in February 2024 (4.9% now)."],
          note: "Credit cards and personal loans show year-over-year spikes above 20% in 2011 to 2014 that look like reclassifications, not real borrowing.",
          tabs: ["Growth by month", "Latest, by category"], src: "Source: Statistics Canada table 36-10-0639, seasonally adjusted." },
        { n: "03 \u00b7 THE LAG", ch: 2, title: "Credit growth is lowest about 18 months after rates rise",
          paras: ["I compared credit growth with the change in the prime rate over the previous 12 months, shifted back by 0 to 24 months. The relationship is strongest at 18 months, with a correlation of -0.52.",
                  "At 6 months it is only -0.17 and at 12 months -0.43. With no delay the correlation is positive (+0.27), which fits a central bank raising rates when borrowing is already strong."],
          note: "Using the level of the prime rate instead of its 12-month change, the strongest lag is about 8 months, so the exact delay depends on the method.",
          tabs: [], src: "Correlation across 164 to 188 months, 2010 to 2026; 170 months at the 18-month lag." },
        { n: "04 \u00b7 DEBT SERVICE", ch: 3, title: "Debt payments took a bigger share of income after rates rose",
          paras: ["The share of household income going to debt payments rose from 12.6% in the April 2020 quarter to 15.2% in the January 2023 quarter, as rates started to rise.",
                  "It is 14.5% now. The mortgage part peaked at 8.2% and is 7.7% now; the non-mortgage part is 6.8%."],
          note: "The quarter labels follow Statistics Canada: 2026 Q2 is the quarter starting April 2026.",
          tabs: [], src: "Source: Statistics Canada table 11-10-0065, seasonally adjusted at annual rates." }
      ],
      recs: [
        { who: "Head of retail lending", title: "Plan for a delayed response to rate changes", text: "Expect credit growth to react to a rate change over about 18 months, not right away. Review lending targets against rate moves from 12 to 24 months earlier.", measure: "Measure: credit growth vs the prime-rate change 18 months earlier" },
        { who: "Risk and finance", title: "Watch debt service alongside rates", text: "Debt payments reached 15.2% of income in early 2023 and are 14.5% now. Track the ratio each quarter, for the total and for mortgages.", measure: "Measure: debt service ratio, total and mortgage" },
        { who: "Analytics team", title: "Add delinquency data to test repayment pressure", text: "This public data has no arrears or default figures, so it cannot say whether higher debt service led to missed payments. Add an arrears series to answer that.", measure: "Next step: join an arrears series" }
      ],
      recNote: "These are proposals from public, market-level data. They are not a lending model.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Bank of Canada and Statistics Canada", s: "Rates from the Valet API and three Statistics Canada tables, 2010 to 2026" },
        { i: "02 \u00b7 PREPARE", b: "Python", s: "Rolled rates up to months and kept 8 credit categories that appear once per month, because lender names repeat across the hierarchy" },
        { i: "03 \u00b7 CHECK", b: "Reconciliation", s: "Checked the report cards and the lag measures against the Python results; auto loans start in 2016, the only gap" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "Monthly credit and rates, quarterly debt service, 4 helper tables and 51 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "4 pages with a lag selector, continuous time axes and a reset-filters button" }
      ]
    },
  },
  {
    id: "collision-risk",
    sector: "Insurance",
    area: "Underwriting and claims analytics",
    title: "When and where do Canadian roads turn deadly?",
    summary: "National police-reported fatal and injury collisions, broken down by hour, weather, road surface, driver age and vehicle age.",
    provenance: "Real",
    source: "Transport Canada National Collision Database (2019 and 2020)",
    tools: ["Power BI", "DAX", "SQL", "Python"],
    headline: { value: null, label: "share of collisions that are fatal in the riskiest hour, versus the all-hours average" },
    question: "Which conditions and people are linked to the most severe outcomes, so a claims or underwriting team knows where to look first?",
    data: "Person-level rows for fatal and injury collisions reported by police, 2019 and 2020. No property-damage-only collisions and no insurance claims.",
    approach: [
      "Validate columns against the data dictionary and map code values to labels.",
      "Derive a collision ID from row order and check it against the declared vehicle count.",
      "Build collision and person tables, then a Power BI report on time, conditions, and people and vehicles.",
      "Compare 2019 with 2020 and explain the change with its caveats."
    ],
    found: [],
    recommend: [],
    limits: [
      "This is not claims data: it supports no loss ratio or pricing statement.",
      "Only fatal and injury collisions are included, so shares are shares of serious collisions.",
      "The collision ID is derived from row order, an assumption I check but cannot confirm.",
      "2020 was a pandemic year with unusual traffic."
    ],
    repo: "02-insurance-collision-risk",
    chart: null
  },
  {
    id: "toronto-311",
    sector: "Public sector",
    area: "City operations",
    title: "What is Toronto calling 311 about, and which requests stay open?",
    summary: "1.35 million 311 requests from 2023 to 2025: what drives demand, which divisions leave requests unresolved, and a change in request types that breaks year-over-year comparisons.",
    provenance: "Real",
    source: "Open Data Toronto, 311 Service Requests - Customer Initiated (Open Government Licence - Toronto)",
    tools: ["Power BI", "Power Query", "DAX", "SQL", "Python"],
    headline: { value: "49.4%", label: "of 2025 parks, forestry and environment requests are still open, against 1.4% to 6.6% in every other division" },
    question: "Where does the city leave requests unresolved, and what is behind the growth in 311 demand?",
    data: "Customer-initiated 311 requests for 2023, 2024 and 2025: 1,351,594 rows with creation time, status, location (postal area or intersection), ward, request type, division and section. There is no close date, so time to close cannot be measured.",
    approach: [
      "Download the three yearly files and repair about 8% of rows where an unquoted comma split the division name into two fields.",
      "Group the Parks and Forestry division with its 2025 successors, since it was renamed and split.",
      "Group status into Resolved, Cancelled, Open and Unknown, and reconcile row counts against the source files.",
      "Run ten SQL queries for volume, outcomes, divisions, types and seasonality, then build the Power BI report from a monthly summary table."
    ],
    found: [
      "Requests grew from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025, up 14.5% in 2025.",
      "Parks, forestry and environment is the outlier: 49.4% of its 2025 requests are still open (18,597 of 37,611), and so are 44.7% of its 2023 requests (12,637 of 28,298). Every other division is between 1.4% and 6.6% open. General pruning is 66% open and tree removal 73%.",
      "The request-type list changed in January 2025: 255 type names appear only in 2025 and cover 58.2% of that year's requests (for example, bin lid repairs were renamed). Growth by type cannot be compared across that boundary.",
      "Between 2023 and 2024, the fastest-growing named types were litter and illegal dumping cleanup (+46.8%) and bin lid repair or replacement (+36.6%).",
      "10.3% of 2025 requests were cancelled, but dead-wildlife pick-up was cancelled 38.8% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%.",
      "February 2025 had 53,707 requests, against 24,871 in February 2024. 19,876 of them were snow-related types that exist only from January 2025, so I cannot tell how much was more demand and how much better capture."
    ],
    recommend: [
      "Check whether the old open forestry requests are a real backlog or statuses that were never updated, and publish expected waits for pruning and tree removal.",
      "Add the closed date to the open dataset. It is the single most useful missing field.",
      "Publish a mapping table whenever request types are renamed, so year-over-year comparisons stay possible.",
      "Review the cancel-heavy types, such as dead-wildlife pick-up and missed recycling, to test whether duplicate or repeat calls are behind the cancellations. This is a hypothesis I have not tested."
    ],
    impact: [
      { action: "Audit the open parks, forestry and environment requests and publish expected waits for pruning and tree removal.", owner: "Division lead, Parks, Forestry and Environment", track: "Open share of the division's requests: 49.4% in 2025, against 1.4% to 6.6% elsewhere." },
      { action: "Add a closed date to the open dataset so time to close can be measured.", owner: "Open data and 311 data team", track: "Share of requests with a measurable time to close: 0% today." },
      { action: "Publish a mapping table whenever request types are renamed.", owner: "311 data owner", track: "Share of requests under renamed or new types that map back to a prior type: 58.2% of 2025 requests are affected today." },
      { action: "Test whether duplicate or repeat calls drive cancellations on the cancel-heavy types. This is a hypothesis, not a finding.", owner: "311 service operations", track: "Cancelled share: 10.3% overall in 2025, 38.8% for dead-wildlife pick-up." }
    ],
    downloads: [
      { label: "Download report (PDF)", file: "downloads/toronto-311-report.pdf", note: "All four report pages, as exported from Power BI Desktop." },
      { label: "Download the Power BI project (.zip)", file: "downloads/toronto-311-powerbi-project.zip", note: "The .pbip project with the model, measures and pages, plus the monthly summary CSV. Open it in Power BI Desktop (free); the README inside says how to set the CSV path." }
    ],
    story: {
      dek: "When Toronto residents see a problem, such as a missed garbage pickup, a fallen tree or a pothole, they report it to the city by calling 311. I studied 1.35 million of these reports from 2023 to 2025 to find out which kinds of problems the city leaves unresolved, and whether the rise in reports means more problems or just a change in how they are labelled.",
      chips: ["Star schema", "Date table", "Year-over-year DAX", "DAX variables", "Drill-through", "Tooltip page", "Custom theme"],
      meta: [
        { k: "Data", v: "City of Toronto Open Data, 311 Service Requests, 2023 to 2025 (real, Open Government Licence)" },
        { k: "Scope", v: "1,351,594 requests, 7 divisions, 829 request types" },
        { k: "Tools", v: "Power BI, DAX, Power Query, SQL, Python" }
      ],
      findings: [
        "Half of parks and forestry requests are still open: 49.4% in 2025, against 1.4% to 6.6% in every other division.",
        "Demand grew 14.5% in 2025, to 500,269 requests, but part of that is new request types, not more problems.",
        "58.2% of 2025 requests sit under renamed or new request types, so year-over-year growth by type is not valid.",
        "Dead-wildlife pick-up is cancelled 38.8% of the time, the highest of any large request type."
      ],
      chapters: [
        { n: "01 \u00b7 DEMAND", ch: 0, title: "Demand rose 14.5%, but not all of it is new demand",
          paras: ["Requests went from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025.",
                  "February 2025 alone had 53,707 requests, against 24,871 a year earlier, and 19,876 of them were snow types that only exist from January 2025. The true rise is smaller than the headline suggests."],
          note: "With this data I cannot separate more demand from better capture.",
          tabs: ["By month", "By year"], src: "Source: Open Data Toronto, 311 Service Requests, 2023 to 2025." },
        { n: "02 \u00b7 WHERE IT STALLS", ch: 1, title: "One division leaves half its requests open",
          paras: ["49.4% of 2025 requests in parks, forestry and environment are open, and so are 44.7% of its 2023 requests, so these are old requests and not only recent ones. Every other division is between 1.4% and 6.6%.",
                  "Inside the division, general pruning is 66.2% open and tree removal 73.3%."],
          note: "An open status could mean a real backlog or a status nobody updated. The data cannot separate the two.",
          tabs: ["By division", "By division and year", "Forestry types"], src: "Open = status Open or In Progress at the data snapshot. No close date is published." },
        { n: "03 \u00b7 A NAMING TRAP", ch: 2, title: "Renamed request types break year-over-year growth",
          paras: ["255 type names appear only in 2025 and cover 58.2% of that year's requests. Bin lid repairs, for example, were renamed.",
                  "So type-level growth is only valid within 2023 to 2024 or within 2025. The report adds a Taxonomy Era filter and a warning instead of showing invalid growth rates."],
          note: "This is the trap of comparing years: what looks like growth can be a new label.",
          tabs: ["Renamed share", "February snow types"], src: "Type names compared between February 2024 and February 2025." },
        { n: "04 \u00b7 CANCELLATIONS", ch: 3, title: "Some request types are cancelled far more than others",
          paras: ["10.3% of 2025 requests were cancelled, but dead-wildlife pick-up was cancelled 38.8% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%.",
                  "Repeat or duplicate calls are one possible reason, but I have not tested it."],
          note: "Shown for 2025 request types with at least 5,000 requests.", tabs: [], src: "Source: Open Data Toronto, 311 Service Requests, 2025." }
      ],
      recs: [
        { who: "Parks, Forestry and Environment lead", title: "Audit the open requests and publish expected waits", text: "Check whether the old open requests are a real backlog or statuses never updated, then set expected waits for pruning and tree removal.", measure: "Measure: open share, 49.4% in 2025" },
        { who: "311 data team", title: "Publish a closed date and a type-rename mapping", text: "A closed date makes time to close measurable. A mapping table keeps year-over-year comparisons valid when types are renamed.", measure: "Measure: share of requests with a time to close" },
        { who: "311 service operations", title: "Test why some types are cancelled so often", text: "Check whether duplicate or repeat calls drive cancellations on dead-wildlife and missed-pickup requests. This is a hypothesis, not a finding.", measure: "Measure: cancelled share, 10.3% overall" }
      ],
      recNote: "These are proposals. The data has no before-and-after, so I do not claim a measured effect.",
      pipeline: [
        { i: "01 \u00b7 SOURCE", b: "Open Data Toronto", s: "Three yearly request files, 1,351,594 rows" },
        { i: "02 \u00b7 PREPARE", b: "Python and SQL", s: "Repaired about 8% of rows broken by an unquoted comma; grouped statuses and the renamed division" },
        { i: "03 \u00b7 CHECK", b: "Reconciliation", s: "Ten SQL queries; totals, yearly counts and shares reconciled to the report" },
        { i: "04 \u00b7 MODEL", b: "Star schema", s: "One fact table of monthly counts, four dimensions, 47 DAX measures" },
        { i: "05 \u00b7 REPORT", b: "Power BI", s: "4 pages with drill-through, a tooltip page, navigation and a custom theme" }
      ]
    },
    brief: {
      findings: [
        "Half of parks and forestry requests are still open: 49.4% in 2025, against 1.4% to 6.6% in every other division.",
        "Demand grew 14.5% in 2025, to 500,269 requests, but part of that is new request types, not more problems.",
        "58.2% of 2025 requests sit under renamed or new request types, so year-over-year growth by type is not valid.",
        "Dead-wildlife pick-up is cancelled 38.8% of the time, the highest of any large request type."
      ],
      skills: [
        { skill: "Data modelling", proof: "Star schema with a date table and 47 DAX measures, reconciled to SQL." },
        { skill: "Data cleaning", proof: "Repaired about 8% of 1.35 million rows broken by an unquoted comma." },
        { skill: "DAX and time intelligence", proof: "Year-over-year, variables and dynamic card subtitles." },
        { skill: "Report design", proof: "4 pages with drill-through, a tooltip page, navigation and a custom theme." },
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
      { value: "4", label: "report pages", sub: "+ drill-through and tooltip" },
      { value: "41", label: "data visuals", sub: "cards, charts, slicers, tables" },
      { value: "6", label: "tables", sub: "1 fact, 4 dimensions, 1 measures" },
      { value: "4", label: "relationships", sub: "one-to-many, single direction" },
      { value: "47", label: "DAX measures", sub: "all in one measures table" }
    ],
    techniques: ["Star schema", "Date table", "Year-over-year with SAMEPERIODLASTYEAR", "DAX variables", "Dynamic card subtitles", "Drill-through page", "Report-page tooltip", "Reset-filters bookmark", "Synced slicers", "Page navigation buttons", "Custom theme (JSON)", "PBIP + TMDL project"],
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
    shots: [
      { file: "images/01-start.png", caption: "Start here: the question, three live findings and how to use the report" },
      { file: "images/02-overview.png", caption: "Overview: demand by month, key findings and year-over-year change" },
      { file: "images/03-outcomes.png", caption: "Outcomes: share of requests still open by division, with drill-through to request types" },
      { file: "images/04-types.png", caption: "Request types: top types, taxonomy-era filter and the naming-change warning" }
    ],
    kpis: [
      { label: "Requests in 2025", value: "500,269", sub: "\u25b2 14.5% vs 2024", icon: "bars" },
      { label: "Resolved", value: "80.5%", sub: "of 2025 requests", icon: "check" },
      { label: "Still open", value: "7.8%", sub: "of 2025 requests", icon: "clock" },
      { label: "Parks & forestry still open", value: "49.4%", sub: "\u25b2 45.1 pts vs other divisions", icon: "warn" }
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
        title: "Demand rose 14.5% in 2025",
        text: "Requests went from 414,282 in 2023 to 437,043 in 2024 and 500,269 in 2025. Part of the February 2025 spike comes from snow-related request types that only exist from January 2025, so the true rise in demand is smaller than the headline suggests.",
        stat: { value: "+14.5%", label: "more requests in 2025 than in 2024" },
        visuals: [
          { ref: 1 },
          { type: "bar", orient: "v", title: "Requests by year", labels: ["2023", "2024", "2025"], values: [414282, 437043, 500269], unit: "requests", highlight: 2 }
        ]
      },
      {
        title: "Half of parks and forestry requests are still open",
        text: "49.4% of 2025 requests in parks, forestry and environment are open, and so are 44.7% of its 2023 requests, so these are old requests and not only recent ones. Every other division is between 1.4% and 6.6%. Within the division, general pruning is 66.2% open and tree removal 73.3%. The data cannot say whether this is a backlog or statuses nobody updated.",
        stat: { value: "49.4%", label: "of 2025 parks, forestry and environment requests are open" },
        visuals: [
          { ref: 0 },
          {
            type: "bar", grouped: true, title: "Share still open, by division and year",
            labels: ["Parks, Forestry & Environment", "Transportation Services", "Toronto Water", "Municipal Licensing & Standards", "Solid Waste Management", "311"],
            datasets: [
              { label: "2023", values: [44.7, 14.3, 12.2, 5.5, 1.2, 9.4] },
              { label: "2024", values: [51.5, 9.3, 7.1, 8.1, 1.2, 2.9] },
              { label: "2025", values: [49.4, 6.6, 5.7, 5.6, 1.7, 1.4] }
            ],
            unit: "% still open", suffix: "%"
          },
          {
            type: "bar", title: "Parks, forestry and environment: share still open, by request type (2023 to 2025)",
            labels: ["Residential or Park Tree Removal", "Stemming", "General Pruning", "General Tree Maintenance", "Tree Emergency Clean-Up", "Storm Clean Up", "By-Law Contravention Invest", "Dangerous Private Tree Investigation"],
            values: [73.3, 68.2, 66.2, 62.0, 37.0, 29.8, 11.7, 2.6], unit: "% still open", suffix: "%"
          }
        ]
      },
      {
        title: "Request types were renamed in January 2025",
        text: "255 type names appear only in 2025 and cover 58.2% of that year's requests. Type-level growth is only valid within 2023 to 2024 or within 2025, so the report adds a Taxonomy Era filter instead of comparing across the break.",
        stat: { value: "58.2%", label: "of 2025 requests use type names introduced in January 2025" },
        warn: true,
        visuals: [
          { type: "doughnut", title: "2025 requests by type-name status", labels: ["Under renamed or new types", "Other requests"], values: [290985, 209284], unit: "requests" },
          { type: "bar", title: "February 2025 requests for type names that did not exist in February 2024", labels: ["Sidewalk Snow Clearing Required", "Road Plowing Request", "Driveway Blocked By Plowed Snowbank", "Snow at Intersections - Impeded Mobility", "Residential Bin Lid Damaged", "Road Pothole / Road Damage"], values: [8722, 4987, 3811, 1248, 1233, 1154], unit: "requests" }
        ]
      },
      {
        title: "Some types are cancelled far more often than others",
        text: "10.3% of 2025 requests were cancelled overall, but dead-wildlife pick-up was cancelled 38.8% of the time (6,026 of 15,513) and missed recycling pick-up 28.6%. Duplicate or repeat calls are one possible reason; I have not tested it.",
        stat: { value: "38.8%", label: "of dead-wildlife pick-up requests were cancelled in 2025" },
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
      note: "Imported from a 33 MB monthly summary of the full request file, so the report stays fast. Results were reconciled against the SQL: totals, yearly counts, open share by division and the 58.2% renamed-type share all match."
    },
    charts: [
      {
        type: "bar",
        title: "Share of 2025 requests still open, by division",
        labels: ["Parks, Forestry & Environment", "Transportation Services", "Toronto Water", "Municipal Licensing & Standards", "Solid Waste Management", "311"],
        values: [49.4, 6.6, 5.7, 5.6, 1.7, 1.4],
        unit: "% still open",
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
    title: "How have opioid and stimulant harms changed across provinces?",
    summary: "Hospitalizations, emergency medical service responses and deaths by province over time.",
    provenance: "Real",
    source: "Public Health Agency of Canada, Health Infobase",
    tools: ["Power BI", "DAX", "SQL", "Python"],
    headline: { value: null, label: "change in hospitalizations from the first to the latest period in the largest province" },
    question: "Where and in which groups are harms rising or falling, and do hospital, EMS and death trends tell the same story?",
    data: "Published aggregated counts and rates by province or territory and period. Small counts may be suppressed.",
    approach: [
      "Download the open CSV and profile every column before defining any measure.",
      "Read the user guide to separate counts from rates and to note reporting differences.",
      "Build a Power BI report: trend, province comparison, hospital vs EMS vs deaths.",
      "Show suppressed values as suppressed, never as zero."
    ],
    found: [],
    recommend: [],
    limits: [
      "Provinces report differently, so rankings need a comparability note.",
      "Counts depend on population size: compare published rates, not counts.",
      "No patient-level data, so no conclusions about individuals."
    ],
    repo: "05-healthcare-opioid-harms",
    chart: null
  }
];

// Chart format when you have results (shown on the case page):
// chart: { type: "bar", title: "Fatal share by hour", labels: ["0","1"], values: [3.1, 2.8], unit: "%" }
