from app.rag import search_knowledge
from app.reasoning import analyze_environment
from app.recommendations import generate_recommendations


def run_environmental_analysis(
    data,
    top_k=5,
    top_n=3,
    user_query=None,
    user_constraints=None
):
    user_constraints = user_constraints or {}

    query_parts = []

    if user_query:
        query_parts.append(
            f"user question: {user_query}"
        )

    if data.soil_organic_carbon is not None:
        query_parts.append(
            f"soil organic carbon {data.soil_organic_carbon}%"
        )

    if data.soil_ph is not None:
        query_parts.append(
            f"soil pH {data.soil_ph}"
        )

    if data.soil_moisture is not None:
        query_parts.append(
            f"soil moisture {data.soil_moisture}%"
        )

    if data.rainfall:
        query_parts.append(
            f"rainfall {data.rainfall}"
        )

    if data.temperature is not None:
        query_parts.append(
            f"temperature {data.temperature} C"
        )

    if data.land_use:
        query_parts.append(
            f"land use {data.land_use}"
        )

    if data.crop:
        query_parts.append(
            f"crop {data.crop}"
        )

    if data.biodiversity_index is not None:
        query_parts.append(
            f"biodiversity index {data.biodiversity_index}"
        )

    if data.region:
        query_parts.append(
            f"region {data.region}"
        )

    query = (
        "Environmental conditions and user question: "
        + ", ".join(query_parts)
        + ". Identify relevant scientific knowledge "
          "and biodiversity or land-management interventions."
    )

    retrieved_results = search_knowledge(
        query,
        top_k=top_k
    )

    reasoning = analyze_environment(data)

    # IMPORTANT:
    # Pass conversation constraints into the recommendation engine
    # BEFORE recommendations are generated.
    reasoning["user_constraints"] = user_constraints

    recommendations = generate_recommendations(
        reasoning,
        retrieved_results,
        top_n=top_n,
        user_query=user_query
    )

    environmental_state = data.model_dump()

    reasoning_package = {
        "environment": environmental_state,
        "user_query": user_query,
        "retrieval_query": query,
        "user_constraints": user_constraints,
        "risks": reasoning["risks"],
        "interacting_factors": reasoning["interacting_factors"],
        "candidate_interventions": reasoning["candidate_interventions"],
        "recommendations": recommendations
    }

    return reasoning_package