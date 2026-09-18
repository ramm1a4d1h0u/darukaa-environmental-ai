def analyze_environment(data):

    risks = []
    interacting_factors = []
    candidate_interventions = []


    # ==========================================
    # SOIL ORGANIC CARBON
    # ==========================================

    if (
        data.soil_organic_carbon is not None
        and data.soil_organic_carbon < 0.5
    ):

        risks.append({
            "factor": "low_soil_organic_carbon",
            "severity": "high",
            "reason": (
                "Low soil organic carbon can be associated with "
                "weaker soil structure, lower water-holding capacity "
                "and reduced soil biological activity."
            )
        })

        candidate_interventions.extend([
            "cover_crops",
            "residue_management",
            "agroforestry"
        ])


    # ==========================================
    # LOW RAINFALL / WATER STRESS
    # ==========================================

    if data.rainfall:

        rainfall = data.rainfall.lower()

        if rainfall in [
            "low",
            "very low",
            "drought"
        ]:

            risks.append({
                "factor": "water_stress",
                "severity": "high",
                "reason": (
                    "Low rainfall can increase water stress and "
                    "reduce soil moisture availability."
                )
            })

            candidate_interventions.extend([
                "cover_crops",
                "soil_moisture_conservation"
            ])


    # ==========================================
    # MONOCULTURE
    # ==========================================

    if data.land_use:

        land_use = data.land_use.lower()

        if "monoculture" in land_use:

            risks.append({
                "factor": "monoculture_pressure",
                "severity": "medium",
                "reason": (
                    "Continuous monoculture can place pressure on "
                    "soil biodiversity, nutrient cycling and "
                    "ecosystem diversity."
                )
            })

            candidate_interventions.extend([
                "cover_crops",
                "crop_rotation",
                "crop_diversification",
                "agroforestry"
            ])


    # ==========================================
    # LOW BIODIVERSITY
    # ==========================================

    if (
        data.biodiversity_index is not None
        and data.biodiversity_index < 0.4
    ):

        risks.append({
            "factor": "low_biodiversity",
            "severity": "high",
            "reason": (
                "A low biodiversity index indicates that biodiversity "
                "is an important environmental concern in the provided "
                "scenario."
            )
        })

        candidate_interventions.extend([
            "crop_diversification",
            "pollinator_habitat",
            "agroforestry"
        ])


    # ==========================================
    # MULTI-METRIC INTERACTION 1
    # ==========================================
    # Soil carbon + rainfall + soil moisture

    if (
        data.soil_organic_carbon is not None
        and data.soil_organic_carbon < 0.5
        and data.rainfall
        and data.rainfall.lower()
        in ["low", "very low", "drought"]
    ):

        interacting_factors.append({

            "factors": [
                "soil_organic_carbon",
                "rainfall",
                "soil_moisture"
            ],

            "relationship": (
                "Low soil organic carbon and low rainfall together "
                "increase the importance of soil moisture conservation "
                "because soil carbon is associated with water-holding "
                "capacity while rainfall determines water availability."
            )
        })


    # ==========================================
    # MULTI-METRIC INTERACTION 2
    # ==========================================
    # Soil carbon + monoculture + soil biodiversity

    if (
        data.soil_organic_carbon is not None
        and data.soil_organic_carbon < 0.5
        and data.land_use
        and "monoculture" in data.land_use.lower()
    ):

        interacting_factors.append({

            "factors": [
                "soil_organic_carbon",
                "land_use",
                "soil_biodiversity"
            ],

            "relationship": (
                "Low soil organic carbon combined with continuous "
                "monoculture creates pressure on soil structure, "
                "nutrient cycling and soil biodiversity."
            )
        })


    # ==========================================
    # MULTI-METRIC INTERACTION 3
    # ==========================================
    # Rainfall + monoculture + biodiversity

    if (
        data.rainfall
        and data.rainfall.lower()
        in ["low", "very low", "drought"]

        and data.land_use

        and "monoculture" in data.land_use.lower()
    ):

        interacting_factors.append({

            "factors": [
                "rainfall",
                "land_use",
                "biodiversity"
            ],

            "relationship": (
                "Low water availability combined with a simplified "
                "cropping system can increase environmental vulnerability "
                "and reduce system diversity."
            )
        })


    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================

    candidate_interventions = list(
        dict.fromkeys(candidate_interventions)
    )


    # ==========================================
    # RETURN STRUCTURED REASONING
    # ==========================================

    return {

        "risks": risks,

        "interacting_factors": interacting_factors,

        "candidate_interventions": candidate_interventions

    }