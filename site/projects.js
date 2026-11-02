// All case-study content lives here. The site renders from this file.
// Any field set to null shows as a dashed "to fill in" placeholder, so nothing looks finished
// until you have run the analysis and typed in your own numbers.
window.PROFILE = {
  name: "Your Name",
  headline: "I turn Canadian public data into Power BI reports people can act on.",
  intro: "Graduate certificate in Business Insights and Analytics, B.Tech in Information Technology. I work in SQL, Power BI, DAX, Excel and Python. Each project below is a short story: the question, the data, what I found, and what I would recommend.",
  email: "mailto:you@example.com",
  linkedin: "https://www.linkedin.com/in/your-profile",
  resume: "resume.pdf",
  certs: [
    { label: "PL-300 Power BI Data Analyst", url: null },
    { label: "DP-600 Fabric Analytics Engineer", url: null }
  ],
  tools: "SQL · MySQL · Power BI · DAX · Power Query · Excel · Python · Fabric"
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
    tools: ["Power BI", "DAX", "SQL", "Python"],
    headline: { value: null, label: "months until credit growth responds most to a rate change (lag with the strongest correlation)" },
    question: "When the Bank of Canada moves rates, how long before household borrowing and debt-service burden change, and in which credit categories?",
    data: "Daily rates from the Bank of Canada Valet API rolled up to months. Monthly household credit liabilities by category, plus quarterly credit summary and debt-service indicators, from Statistics Canada. Market-level data only: no customer or account records.",
    approach: [
      "Load rates and the three Statistics Canada tables into SQLite with a repeatable script.",
      "Build a month-level model in Power BI: one date table, rates, credit, debt service.",
      "Compare YoY credit growth with rate changes at lags of 0 to 12 months, with a lag slicer.",
      "Document every DAX measure and its definition."
    ],
    found: [],
    recommend: [],
    limits: [
      "Correlation is not causation: many things move at once when rates change.",
      "The data is national and aggregated, so it says nothing about individual borrowers or default risk.",
      "I did not find a Statistics Canada table with delinquency or arrears, so the project does not report it."
    ],
    repo: "01-banking-household-credit",
    chart: null
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
            labels: ["General Pruning", "Storm Clean Up", "Tree Emergency Clean-Up", "General Tree Maintenance", "Stemming", "Dangerous Private Tree Investigation", "By-Law Contravention Invest", "Residential or Park Tree Removal"],
            values: [66.2, 29.8, 37.0, 62.0, 68.2, 2.6, 11.7, 73.3], unit: "% still open", suffix: "%"
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
        { name: "Open %", dax: "DIVIDE ( CALCULATE ( [Requests], requests[status_group] = \"Open\" ), [Requests] )" },
        { name: "Requests YoY %", dax: "DIVIDE ( [Requests] - [Requests PY], [Requests PY] )" },
        { name: "Taxonomy Era", dax: "IF ( early > 0 && late > 0, \"In both periods\", IF ( early > 0, \"2023-24 only\", \"2025 only\" ) )" }
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
