"""
Curated seed data — 25 real Indian government schemes for farmers.

Each scheme dict has:
  scheme_name, ministry, description, benefits, eligibility_criteria,
  category_tags (list), state_applicability (list — empty = all-India),
  apply_url, income_limit (int|None), gender_specific (str|None),
  age_limit (dict|None)
"""

SEED_SCHEMES: list[dict] = [
    # ── 1. PM-KISAN ──────────────────────────────────────────────────────────
    {
        "scheme_name": "PM-KISAN Samman Nidhi",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Direct income support of ₹6,000/year in 3 installments to all land-holding farmer families.",
        "benefits": "₹6,000 per year (₹2,000 × 3 installments) directly to bank account",
        "eligibility_criteria": "All land-holding farmer families with cultivable land. Excludes income-tax payers and institutional land holders.",
        "category_tags": ["income_support", "all_farmers", "marginal", "small"],
        "state_applicability": [],  # All India
        "apply_url": "https://pmkisan.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 2. PMFBY ─────────────────────────────────────────────────────────────
    {
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Comprehensive crop insurance at very low premiums — 2% for Kharif, 1.5% for Rabi, 5% for horticulture.",
        "benefits": "Crop insurance at subsidized premium (2% Kharif, 1.5% Rabi). Full sum insured on crop loss.",
        "eligibility_criteria": "All farmers growing notified crops in notified areas. Both loanee and non-loanee farmers eligible.",
        "category_tags": ["crop_insurance", "all_farmers", "marginal", "small", "medium", "large"],
        "state_applicability": [],
        "apply_url": "https://pmfby.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 3. Kisan Credit Card ─────────────────────────────────────────────────
    {
        "scheme_name": "Kisan Credit Card (KCC)",
        "ministry": "NABARD / Department of Financial Services",
        "description": "Short-term credit for crop production, post-harvest, and consumption needs at subsidized interest (4% p.a.).",
        "benefits": "Credit up to ₹3 lakh at 4% interest. Flexible repayment. Also covers animal husbandry & fisheries.",
        "eligibility_criteria": "All farmers — individual, joint, tenant, oral lessees, SHGs. Must have crop/allied activity.",
        "category_tags": ["credit", "loan", "all_farmers", "marginal", "small", "medium"],
        "state_applicability": [],
        "apply_url": "https://www.nabard.org/content.aspx?id=498",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 4. Soil Health Card ──────────────────────────────────────────────────
    {
        "scheme_name": "Soil Health Card Scheme",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Free soil testing with nutrient-specific fertilizer recommendations to improve productivity.",
        "benefits": "Free soil analysis report with crop-wise fertilizer recommendations every 2 years.",
        "eligibility_criteria": "All farmers with cultivable land.",
        "category_tags": ["soil_health", "advisory", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://soilhealth.dac.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 5. PM-KUSUM ──────────────────────────────────────────────────────────
    {
        "scheme_name": "PM-KUSUM (Solar Pump Scheme)",
        "ministry": "Ministry of New & Renewable Energy",
        "description": "Subsidized solar pumps and solar power plants on barren/fallow land for farmers.",
        "benefits": "60% subsidy on solar pumps (up to 7.5 HP). Extra income by selling surplus power to grid.",
        "eligibility_criteria": "All farmers for component B (standalone solar pumps). Land-holding required.",
        "category_tags": ["solar", "irrigation", "energy", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://pmkusum.mnre.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 6. eNAM ──────────────────────────────────────────────────────────────
    {
        "scheme_name": "e-NAM (National Agriculture Market)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Online trading platform for agricultural commodities across states — better price discovery.",
        "benefits": "Pan-India market access. Transparent bidding. Direct buyer-seller connection. Reduced middlemen charges.",
        "eligibility_criteria": "All farmers with Aadhaar-linked bank account. Operate through registered mandis.",
        "category_tags": ["market", "trading", "price_discovery", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://enam.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 7. PMKSY ─────────────────────────────────────────────────────────────
    {
        "scheme_name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Subsidies for micro-irrigation (drip, sprinkler) — 'Har Khet Ko Paani' and 'Per Drop More Crop'.",
        "benefits": "55% subsidy for small/marginal farmers, 45% for others on drip & sprinkler systems.",
        "eligibility_criteria": "All farmers. Higher subsidy for small & marginal farmers. Land ownership proof needed.",
        "category_tags": ["irrigation", "water", "drip", "sprinkler", "marginal", "small"],
        "state_applicability": [],
        "apply_url": "https://pmksy.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 8. PMJDY ─────────────────────────────────────────────────────────────
    {
        "scheme_name": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "ministry": "Ministry of Finance",
        "description": "Zero-balance bank account with RuPay card, overdraft facility, and accident insurance.",
        "benefits": "Zero-balance account. ₹10,000 overdraft. ₹2 lakh accident insurance. ₹30,000 life cover.",
        "eligibility_criteria": "Any Indian citizen above 10 years. No minimum balance required.",
        "category_tags": ["banking", "financial_inclusion", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://pmjdy.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": {"min": 10},
    },

    # ── 9. PMJJBY ────────────────────────────────────────────────────────────
    {
        "scheme_name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "ministry": "Ministry of Finance",
        "description": "Life insurance cover of ₹2 lakh at just ₹436/year premium.",
        "benefits": "₹2 lakh life cover. Premium auto-debited. Covers death due to any cause.",
        "eligibility_criteria": "Age 18-50 years. Must have a bank account with Aadhaar linkage.",
        "category_tags": ["insurance", "life_cover", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://www.jansuraksha.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": {"min": 18, "max": 50},
    },

    # ── 10. PMSBY ────────────────────────────────────────────────────────────
    {
        "scheme_name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "ministry": "Ministry of Finance",
        "description": "Accident insurance cover of ₹2 lakh at only ₹20/year.",
        "benefits": "₹2 lakh for accidental death. ₹1 lakh for partial disability. Just ₹20/year.",
        "eligibility_criteria": "Age 18-70 years with a bank account.",
        "category_tags": ["insurance", "accident", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://www.jansuraksha.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": {"min": 18, "max": 70},
    },

    # ── 11. PM-SYM (Pension) ─────────────────────────────────────────────────
    {
        "scheme_name": "PM-SYM (Shram Yogi Maandhan) / PM-KMY",
        "ministry": "Ministry of Labour & Employment / Agriculture",
        "description": "Pension scheme for small & marginal farmers — ₹3,000/month pension after age 60.",
        "benefits": "₹3,000/month pension after 60. Govt matches contribution. Family pension for spouse.",
        "eligibility_criteria": "Age 18-40 years. Small/marginal farmer with land < 2 hectares. Income < ₹15,000/month.",
        "category_tags": ["pension", "social_security", "marginal", "small"],
        "state_applicability": [],
        "apply_url": "https://maandhan.in/",
        "income_limit": 180000,
        "gender_specific": None,
        "age_limit": {"min": 18, "max": 40},
    },

    # ── 12. National Mission on Sustainable Agriculture ──────────────────────
    {
        "scheme_name": "National Mission on Sustainable Agriculture (NMSA)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Promotes sustainable practices — organic farming, resource conservation, climate-resilient crops.",
        "benefits": "Training, subsidies for organic inputs, & support for soil health management.",
        "eligibility_criteria": "All farmers. Priority to rainfed areas & climate-vulnerable regions.",
        "category_tags": ["organic", "sustainable", "climate", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://nmsa.dac.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 13. Paramparagat Krishi Vikas Yojana (Organic) ───────────────────────
    {
        "scheme_name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Supports organic farming clusters with ₹50,000/hectare over 3 years.",
        "benefits": "₹50,000/hectare for 3 years. Organic certification support. Market linkage.",
        "eligibility_criteria": "Cluster of 50+ farmers with at least 50 acres. Focus on chemical-free farming.",
        "category_tags": ["organic", "cluster", "marginal", "small", "medium"],
        "state_applicability": [],
        "apply_url": "https://pgsindia-ncof.gov.in/pkvy/Index.aspx",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 14. Agriculture Infrastructure Fund ──────────────────────────────────
    {
        "scheme_name": "Agriculture Infrastructure Fund (AIF)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "₹1 lakh crore financing for post-harvest infrastructure — cold storage, warehouses, processing units.",
        "benefits": "3% interest subvention on loans up to ₹2 crore. CGTMSE credit guarantee.",
        "eligibility_criteria": "Farmers, FPOs, PACS, agri-entrepreneurs. For post-harvest management infrastructure.",
        "category_tags": ["infrastructure", "cold_storage", "warehouse", "FPO"],
        "state_applicability": [],
        "apply_url": "https://agriinfra.dac.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 15. Mahila Kisan Sashaktikaran Pariyojana ────────────────────────────
    {
        "scheme_name": "Mahila Kisan Sashaktikaran Pariyojana (MKSP)",
        "ministry": "Ministry of Rural Development",
        "description": "Empowers women farmers through skill training, resource access, and sustainable agriculture practices.",
        "benefits": "Free training, seed/input kits, SHG formation support, market linkage for women farmers.",
        "eligibility_criteria": "Women farmers, especially from SC/ST, BPL, and landless categories.",
        "category_tags": ["women", "training", "empowerment", "marginal"],
        "state_applicability": [],
        "apply_url": "https://nrlm.gov.in/",
        "income_limit": None,
        "gender_specific": "Female",
        "age_limit": None,
    },

    # ── 16. National Horticulture Mission ────────────────────────────────────
    {
        "scheme_name": "Mission for Integrated Development of Horticulture (MIDH)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Financial assistance for developing horticulture — fruits, vegetables, flowers, spices, plantation crops.",
        "benefits": "40-50% subsidy on establishing new orchards, protected cultivation, and micro-irrigation.",
        "eligibility_criteria": "Farmers, FPOs growing horticulture crops.",
        "category_tags": ["horticulture", "fruits", "vegetables", "flowers", "spices", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://midh.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 17. Sub-Mission on Agricultural Mechanization ────────────────────────
    {
        "scheme_name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Subsidies on purchase of farm equipment — tractors, tillers, harvesters, drones.",
        "benefits": "40-50% subsidy on farm machinery for SC/ST/small/marginal; 25-40% for others.",
        "eligibility_criteria": "All farmers. Higher subsidy for small, marginal, SC/ST, women farmers.",
        "category_tags": ["machinery", "tractor", "equipment", "marginal", "small"],
        "state_applicability": [],
        "apply_url": "https://agrimachinery.nic.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 18. Rashtriya Krishi Vikas Yojana ────────────────────────────────────
    {
        "scheme_name": "Rashtriya Krishi Vikas Yojana (RKVY-RAFTAAR)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Incentivises states to increase agriculture sector growth through innovative projects.",
        "benefits": "Funding for value addition, agri-startups (up to ₹25 lakh), and infrastructure.",
        "eligibility_criteria": "Farmers, FPOs, agri-entrepreneurs via state agriculture departments.",
        "category_tags": ["startup", "innovation", "value_addition", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://rkvy.nic.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 19. National Food Security Mission ───────────────────────────────────
    {
        "scheme_name": "National Food Security Mission (NFSM)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Subsidized improved seeds, micronutrients, and demonstrations for pulses, rice, wheat, coarse cereals.",
        "benefits": "50-100% subsidy on seeds, INM/IPM inputs, cropping system demonstrations.",
        "eligibility_criteria": "Farmers in NFSM districts growing targeted crops (rice, wheat, pulses, nutri-cereals).",
        "category_tags": ["seeds", "pulses", "rice", "wheat", "cereals", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://nfsm.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 20. Micro Irrigation Fund ────────────────────────────────────────────
    {
        "scheme_name": "Micro Irrigation Fund (MIF)",
        "ministry": "Ministry of Agriculture / NABARD",
        "description": "₹5,000 crore corpus fund for states to expand micro-irrigation coverage.",
        "benefits": "State-level subsidies for drip & sprinkler above PMKSY. Additional 10-15% incentive.",
        "eligibility_criteria": "All farmers in states that have availed MIF. Contact district agriculture office.",
        "category_tags": ["irrigation", "drip", "sprinkler", "water_saving", "all_farmers"],
        "state_applicability": [],
        "apply_url": "https://pmksy.gov.in/microirrigation/index.aspx",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 21. Agri-Clinics & Agri-Business Centres (ACABC) ─────────────────────
    {
        "scheme_name": "Agri-Clinics & Agri-Business Centres (ACABC)",
        "ministry": "Ministry of Agriculture & Farmers' Welfare",
        "description": "Supports agri-graduates/diploma holders to start agri-advisory ventures. Up to ₹20 lakh loan at subsidized rate.",
        "benefits": "Up to ₹20 lakh composite loan. 44% subsidy for general, 36% back-end+interest subvention for SC/ST/women.",
        "eligibility_criteria": "Agriculture graduates, diploma holders, intermediate in agriculture. Age: 18+.",
        "category_tags": ["startup", "agri_business", "youth", "graduate"],
        "state_applicability": [],
        "apply_url": "https://www.acabcmis.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": {"min": 18},
    },

    # ── 22. Mukhyamantri Kisan Sahay Yojana (Gujarat) ────────────────────────
    {
        "scheme_name": "Mukhyamantri Kisan Sahay Yojana",
        "ministry": "Government of Gujarat",
        "description": "State-level crop insurance alternate for Gujarat farmers — no premium required!",
        "benefits": "Up to ₹25,000/hectare for 33-60% crop loss; ₹35,000/hectare for >60% loss. Free of cost.",
        "eligibility_criteria": "All 8-A land holders in Gujarat. Enrolled automatically via revenue records.",
        "category_tags": ["crop_insurance", "state_scheme", "all_farmers"],
        "state_applicability": ["Gujarat"],
        "apply_url": "https://ikhedut.gujarat.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 23. Rythu Bandhu (Telangana) ─────────────────────────────────────────
    {
        "scheme_name": "Rythu Bandhu Investment Support",
        "ministry": "Government of Telangana",
        "description": "₹10,000/acre/year (₹5,000 each in Kharif & Rabi) direct investment support to all land-owning farmers.",
        "benefits": "₹10,000/acre/year directly to farmer's bank. No conditions on usage.",
        "eligibility_criteria": "All pattadar (land-owning) farmers in Telangana. No income/size restriction.",
        "category_tags": ["income_support", "state_scheme", "all_farmers"],
        "state_applicability": ["Telangana"],
        "apply_url": "https://rythubandhu.telangana.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 24. YSR Rythu Bharosa (Andhra Pradesh) ───────────────────────────────
    {
        "scheme_name": "YSR Rythu Bharosa - PM Kisan",
        "ministry": "Government of Andhra Pradesh",
        "description": "₹13,500/year combined investment support (state ₹7,500 + PM-KISAN ₹6,000) for farmers.",
        "benefits": "₹13,500/year total. ₹7,500 from state + ₹6,000 PM-KISAN. Landless tenant farmers also eligible for ₹15,000 via YSRRC.",
        "eligibility_criteria": "All farmer families in AP. Tenant farmers via YSRRC component (₹15,000/year).",
        "category_tags": ["income_support", "state_scheme", "marginal", "small", "tenant"],
        "state_applicability": ["Andhra Pradesh"],
        "apply_url": "https://ysrrythubharosa.ap.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },

    # ── 25. Kalia Yojana (Odisha) ────────────────────────────────────────────
    {
        "scheme_name": "KALIA Yojana",
        "ministry": "Government of Odisha",
        "description": "₹10,000/year financial assistance (₹5,000 × 2) for small/marginal farmers and landless agri-labourers.",
        "benefits": "₹10,000/year for cultivation. ₹12,500 life insurance. ₹2 lakh accidental cover.",
        "eligibility_criteria": "Small/marginal farmers and landless agri-labourers in Odisha.",
        "category_tags": ["income_support", "state_scheme", "marginal", "small", "landless"],
        "state_applicability": ["Odisha"],
        "apply_url": "https://kfrms.odisha.gov.in/",
        "income_limit": None,
        "gender_specific": None,
        "age_limit": None,
    },
]


def get_all_schemes() -> list[dict]:
    """Return the full list of curated government schemes."""
    return SEED_SCHEMES


def filter_schemes_by_state(state: str) -> list[dict]:
    """Return schemes applicable to a given state (including all-India schemes)."""
    state_lower = state.strip().lower()
    return [
        s for s in SEED_SCHEMES
        if not s["state_applicability"]  # all-India
        or any(st.lower() == state_lower for st in s["state_applicability"])
    ]


def filter_schemes_by_tags(tags: list[str]) -> list[dict]:
    """Return schemes that match any of the given category tags."""
    tag_set = {t.lower() for t in tags}
    return [
        s for s in SEED_SCHEMES
        if tag_set & {t.lower() for t in s["category_tags"]}
    ]
