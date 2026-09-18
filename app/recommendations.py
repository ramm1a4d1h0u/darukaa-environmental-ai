from app.rag import search_intervention_evidence


# ============================================================
# INTERVENTION PROFILES
# ============================================================

INTERVENTION_PROFILES = {

    "cover_crops": {
        "name": "Cover crops",
        "addresses": [
            "low_soil_organic_carbon",
            "water_stress",
            "monoculture_pressure"
        ],
        "metrics": [
            "soil_organic_carbon",
            "soil_moisture",
            "soil_biodiversity",
            "nutrient_cycling"
        ],
        "time_horizon": "medium-term",
        "reason": (
            "Cover crops maintain vegetation cover between main crops, "
            "adding organic matter and protecting the soil surface. "
            "They can support soil structure, moisture retention and "
            "soil biological activity while reducing the effects of "
            "continuous monoculture."
        )
    },


    "crop_rotation": {
        "name": "Crop rotation",
        "addresses": [
            "monoculture_pressure",
            "low_soil_organic_carbon"
        ],
        "metrics": [
            "soil_biodiversity",
            "nutrient_cycling",
            "soil_structure",
            "crop_diversity"
        ],
        "time_horizon": "medium-term",
        "reason": (
            "Rotate wheat with other suitable crops, preferably including "
            "crops with different nutrient and root characteristics. "
            "Rotation reduces continuous monoculture and can support "
            "nutrient cycling, soil biological functions and crop diversity."
        )
    },


    "crop_diversification": {
        "name": "Crop diversification",
        "addresses": [
            "monoculture_pressure",
            "low_biodiversity"
        ],
        "metrics": [
            "crop_diversity",
            "biodiversity",
            "pollination",
            "nutrient_cycling"
        ],
        "time_horizon": "medium-term",
        "reason": (
            "Increase the diversity of crops grown across the farm instead "
            "of relying continuously on wheat. Greater crop diversity can "
            "create a more heterogeneous agricultural environment and "
            "support broader ecosystem functions."
        )
    },


    "agroforestry": {
        "name": "Agroforestry",
        "addresses": [
            "low_soil_organic_carbon",
            "water_stress",
            "low_biodiversity",
            "monoculture_pressure"
        ],
        "metrics": [
            "soil_health",
            "water_management",
            "biodiversity",
            "landscape_connectivity"
        ],
        "time_horizon": "long-term",
        "reason": (
            "Integrate suitable trees with crops or livestock where "
            "local conditions permit. Trees can add structural diversity "
            "to agricultural landscapes and support soil health, water "
            "management, biodiversity and habitat connectivity."
        )
    },


    "soil_moisture_conservation": {
        "name": "Soil moisture conservation",
        "addresses": [
            "water_stress"
        ],
        "metrics": [
            "soil_moisture",
            "water_availability",
            "water_productivity"
        ],
        "time_horizon": "short-to-medium-term",
        "reason": (
            "Use soil-management practices that retain available water "
            "and reduce moisture loss. This is particularly relevant "
            "under low-rainfall conditions."
        )
    },


    "residue_management": {
        "name": "Residue management",
        "addresses": [
            "low_soil_organic_carbon",
            "water_stress"
        ],
        "metrics": [
            "soil_organic_carbon",
            "soil_structure",
            "soil_moisture"
        ],
        "time_horizon": "medium-term",
        "reason": (
            "Retain suitable crop residues on the field where practical. "
            "Residues can contribute organic matter and help protect the "
            "soil surface and conserve moisture."
        )
    },


    "pollinator_habitat": {
        "name": "Pollinator habitat",
        "addresses": [
            "low_biodiversity"
        ],
        "metrics": [
            "pollinator_diversity",
            "floral_resources",
            "biodiversity"
        ],
        "time_horizon": "medium-term",
        "reason": (
            "Create or retain suitable flowering habitat around or within "
            "the farm to provide floral resources and support pollinator "
            "diversity."
        )
    }
}


# ============================================================
# EXTRACT EVIDENCE
# ============================================================

def extract_evidence(results):

    evidence = []

    if not results:
        return evidence

    documents = results.get(
        "documents",
        [[]]
    )

    metadatas = results.get(
        "metadatas",
        [[]]
    )

    documents = (
        documents[0]
        if documents
        else []
    )

    metadatas = (
        metadatas[0]
        if metadatas
        else []
    )

    for i, document in enumerate(documents):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        content = document

        if "Content:" in document:

            content = document.split(
                "Content:",
                1
            )[1]

            if "Environmental metrics:" in content:

                content = content.split(
                    "Environmental metrics:",
                    1
                )[0]

        content = content.strip()

        if not content:
            continue

        if len(content) > 900:

            content = (
                content[:900]
                + "..."
            )

        evidence.append({

            "title":
                metadata.get(
                    "title",
                    "Scientific document"
                ),

            "source":
                metadata.get(
                    "source",
                    "Unknown source"
                ),

            "source_url":
                metadata.get(
                    "source_url",
                    ""
                ),

            "evidence_snippet":
                content
        })

    return evidence


# ============================================================
# QUERY RELEVANCE
# ============================================================

def query_relevance_score(
    profile,
    user_query
):

    if not user_query:
        return 0

    query = user_query.lower()

    score = 0


    # --------------------------------------------------------
    # BIODIVERSITY
    # --------------------------------------------------------

    if any(
        word in query
        for word in [
            "biodiversity",
            "species",
            "ecosystem",
            "pollinator",
            "habitat"
        ]
    ):

        biodiversity_metrics = {

            "biodiversity",
            "soil_biodiversity",
            "pollination",
            "pollinator_diversity",
            "crop_diversity",
            "landscape_connectivity"
        }

        for metric in profile["metrics"]:

            if metric in biodiversity_metrics:
                score += 3


    # --------------------------------------------------------
    # SOIL
    # --------------------------------------------------------

    if "soil" in query:

        soil_terms = {

            "soil_organic_carbon",
            "soil_moisture",
            "soil_biodiversity",
            "soil_structure",
            "soil_health",
            "nutrient_cycling"
        }

        for metric in profile["metrics"]:

            if metric in soil_terms:
                score += 1


    # --------------------------------------------------------
    # WATER
    # --------------------------------------------------------

    if any(
        word in query
        for word in [
            "water",
            "rainfall",
            "drought",
            "moisture"
        ]
    ):

        water_terms = {

            "soil_moisture",
            "water_availability",
            "water_productivity",
            "water_management"
        }

        for metric in profile["metrics"]:

            if metric in water_terms:
                score += 2


    return score


# ============================================================
# USER CONSTRAINT DETECTION
# ============================================================

def has_no_tree_constraint(
    user_query: str
) -> bool:

    if not user_query:
        return False

    query = user_query.lower()

    phrases = [

        "don't want to plant trees",
        "do not want to plant trees",
        "dont want to plant trees",

        "don't want trees",
        "do not want trees",
        "dont want trees",

        "no trees",
        "without trees",

        "avoid trees",
        "avoid planting trees",

        "not interested in trees"
    ]

    return any(
        phrase in query
        for phrase in phrases
    )


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    reasoning,
    retrieved_results=None,
    top_n=3,
    user_query=None
):

    risks = reasoning.get(
        "risks",
        []
    )

    candidate_interventions = reasoning.get(
        "candidate_interventions",
        []
    )

    user_constraints = reasoning.get(
        "user_constraints",
        {}
    )


    # --------------------------------------------------------
    # CHECK NO-TREE CONSTRAINT
    # --------------------------------------------------------

    no_trees = (

        user_constraints.get(
            "no_trees",
            False
        )

        or

        has_no_tree_constraint(
            user_query
        )
    )


    # --------------------------------------------------------
    # REMOVE AGROFORESTRY
    # --------------------------------------------------------

    if no_trees:

        candidate_interventions = [

            intervention

            for intervention
            in candidate_interventions

            if intervention != "agroforestry"

        ]


    detected_risks = {

        risk["factor"]

        for risk in risks
    }


    recommendations = []


    # ========================================================
    # PROCESS CANDIDATES
    # ========================================================

    for intervention_id in candidate_interventions:

        profile = INTERVENTION_PROFILES.get(
            intervention_id
        )

        if not profile:
            continue


        # ----------------------------------------------------
        # EXTRA SAFETY FILTER
        # ----------------------------------------------------

        if (
            no_trees
            and intervention_id == "agroforestry"
        ):
            continue


        # ----------------------------------------------------
        # MATCH RISKS
        # ----------------------------------------------------

        matched_risks = [

            risk

            for risk in detected_risks

            if risk in profile["addresses"]

        ]

        if not matched_risks:
            continue


        # ----------------------------------------------------
        # RISK COVERAGE
        # ----------------------------------------------------

        risk_coverage_score = len(
            matched_risks
        )


        # ----------------------------------------------------
        # QUERY RELEVANCE
        # ----------------------------------------------------

        relevance_score = query_relevance_score(

            profile,

            user_query

        )


        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        total_score = (

            risk_coverage_score * 10

            + relevance_score

        )


        # ----------------------------------------------------
        # SCIENTIFIC EVIDENCE
        # ----------------------------------------------------

        evidence_results = (
            search_intervention_evidence(

                intervention_id.replace(
                    "_",
                    " "
                ),

                top_k=3

            )
        )


        evidence = extract_evidence(

            evidence_results

        )


        # ----------------------------------------------------
        # RISK → METRIC
        # ----------------------------------------------------

        risk_metric_mapping = {}


        for risk in risks:

            factor = risk["factor"]


            if factor not in profile["addresses"]:
                continue


            if factor == "low_soil_organic_carbon":

                metrics = [

                    "soil_organic_carbon",

                    "soil_structure"

                ]


            elif factor == "water_stress":

                metrics = [

                    "soil_moisture",

                    "water_availability"

                ]


            elif factor == "monoculture_pressure":

                metrics = [

                    "soil_biodiversity",

                    "nutrient_cycling",

                    "crop_diversity"

                ]


            elif factor == "low_biodiversity":

                metrics = [

                    "biodiversity",

                    "species_diversity"

                ]


            else:

                metrics = profile["metrics"]


            risk_metric_mapping[factor] = {

                "severity":
                    risk["severity"],

                "metrics":
                    metrics
            }


        # ----------------------------------------------------
        # BUILD RESULT
        # ----------------------------------------------------

        recommendations.append({

            "intervention":
                profile["name"],

            "intervention_id":
                intervention_id,

            "score":
                total_score,

            "risk_coverage_score":
                risk_coverage_score,

            "query_relevance_score":
                relevance_score,

            "matched_risks":
                matched_risks,

            "risk_metric_mapping":
                risk_metric_mapping,

            "metrics":
                profile["metrics"],

            "time_horizon":
                profile["time_horizon"],

            "reason":
                profile["reason"],

            "evidence":
                evidence
        })


    # ========================================================
    # SORT
    # ========================================================

    recommendations.sort(

        key=lambda x: x["score"],

        reverse=True

    )


    # ========================================================
    # RETURN
    # ========================================================

    return recommendations[:top_n]