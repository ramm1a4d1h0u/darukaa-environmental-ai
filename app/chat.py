import re
from typing import Dict, Any

from app.models import EnvironmentalInput
from app.pipeline import run_environmental_analysis
from app.llm_report import generate_scientific_report


conversation_memory: Dict[str, Dict[str, Any]] = {}


def extract_environment_from_text(
    text: str,
    existing: dict
) -> dict:

    env = existing.copy()
    lower = text.lower().strip()

    match = re.search(
        r"(?:soil organic carbon|organic carbon|soc)"
        r"[^\d]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        env["soil_organic_carbon"] = float(match.group(1))

    match = re.search(
        r"(?:soil ph|ph)"
        r"[^\d]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        env["soil_ph"] = float(match.group(1))

    match = re.search(
        r"(?:soil moisture|moisture)"
        r"[^\d]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        env["soil_moisture"] = float(match.group(1))

    match = re.search(
        r"(?:temperature|temp)"
        r"[^\d]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        env["temperature"] = float(match.group(1))

    match = re.search(
        r"(?:biodiversity index|biodiversity)"
        r"[^\d]*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        env["biodiversity_index"] = float(match.group(1))

    standalone_number = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*%?\s*",
        text
    )

    if standalone_number:
        value = float(standalone_number.group(1))
        pending_field = existing.get("_last_question")

        if pending_field == "soil_organic_carbon":
            env["soil_organic_carbon"] = value
        elif pending_field == "soil_moisture":
            env["soil_moisture"] = value
        elif pending_field == "soil_ph":
            env["soil_ph"] = value
        elif pending_field == "temperature":
            env["temperature"] = value
        elif pending_field == "biodiversity_index":
            env["biodiversity_index"] = value

    if "very low rainfall" in lower:
        env["rainfall"] = "very low"
    elif "low rainfall" in lower:
        env["rainfall"] = "low"
    elif "drought" in lower:
        env["rainfall"] = "drought"
    elif "high rainfall" in lower:
        env["rainfall"] = "high"
    elif "normal rainfall" in lower:
        env["rainfall"] = "normal"

    if "monoculture" in lower:
        env["land_use"] = "monoculture"
    elif "mixed farming" in lower:
        env["land_use"] = "mixed farming"
    elif "agroforestry" in lower:
        env["land_use"] = "agroforestry"

    crops = [
        "wheat",
        "rice",
        "maize",
        "corn",
        "soybean",
        "cotton",
        "sugarcane"
    ]

    for crop in crops:
        if crop in lower:
            env["crop"] = crop
            break

    if "semi-arid" in lower:
        env["region"] = "semi-arid"
    elif "semi arid" in lower:
        env["region"] = "semi-arid"
    elif "arid" in lower:
        env["region"] = "arid"
    elif "tropical" in lower:
        env["region"] = "tropical"
    elif "temperate" in lower:
        env["region"] = "temperate"

    env.pop("_last_question", None)

    return env


def update_constraints(
    message: str,
    constraints: dict
) -> dict:

    constraints = constraints.copy()
    query = message.lower()

    no_tree_phrases = [
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

    if any(phrase in query for phrase in no_tree_phrases):
        constraints["no_trees"] = True

    tree_positive_phrases = [
        "i want to plant trees",
        "i am willing to plant trees",
        "trees are okay",
        "trees are fine"
    ]

    if any(phrase in query for phrase in tree_positive_phrases):
        constraints["no_trees"] = False

    return constraints


def get_missing_fields(
    env: dict,
    user_message: str
):
    query = user_message.lower()

    biodiversity_question = any(
        word in query
        for word in [
            "biodiversity",
            "species",
            "ecosystem",
            "pollinator",
            "habitat"
        ]
    )

    if biodiversity_question:
        if env.get("biodiversity_index") is None:
            if env.get("land_use") is None:
                return ["land_use"]
        return []

    soil_question = any(
        word in query
        for word in [
            "soil health",
            "soil",
            "organic carbon",
            "soil carbon"
        ]
    )

    if soil_question:
        if env.get("soil_organic_carbon") is None:
            return ["soil_organic_carbon"]
        return []

    water_question = any(
        word in query
        for word in [
            "water",
            "rainfall",
            "drought",
            "moisture"
        ]
    )

    if water_question:
        if env.get("rainfall") is None:
            return ["rainfall"]

    return []


FIELD_QUESTIONS = {
    "soil_organic_carbon":
        "What is the soil organic carbon (%)?",

    "soil_moisture":
        "What is the current soil moisture (%)?",

    "rainfall":
        "Is the rainfall low, normal, high, or drought-like?",

    "land_use":
        "What is the current land use, for example monoculture?",

    "crop":
        "What crop is currently being grown?",

    "biodiversity_index":
        "Do you have a biodiversity index value?",

    "region":
        "What type of region is this, for example semi-arid?"
}


def is_tradeoff_question(message: str) -> bool:
    query = message.lower()

    words = [
        "trade-off",
        "tradeoff",
        "trade offs",
        "tradeoffs",
        "risk",
        "risks",
        "drawback",
        "drawbacks",
        "disadvantage",
        "disadvantages",
        "downside",
        "downsides",
        "negative effect",
        "negative effects",
        "problem with",
        "problems with"
    ]

    return any(word in query for word in words)


def is_action_plan_question(message: str) -> bool:
    query = message.lower()

    words = [
        "action plan",
        "next 1 year",
        "next year",
        "one year",
        "1-year",
        "12 months",
        "twelve months",
        "year plan"
    ]

    return any(word in query for word in words)


def run_chat_analysis(
    message: str,
    environment: dict,
    constraints: dict
):

    data = EnvironmentalInput(
        user_query=message,
        soil_organic_carbon=environment.get("soil_organic_carbon"),
        soil_ph=environment.get("soil_ph"),
        soil_moisture=environment.get("soil_moisture"),
        rainfall=environment.get("rainfall"),
        temperature=environment.get("temperature"),
        land_use=environment.get("land_use"),
        crop=environment.get("crop"),
        biodiversity_index=environment.get("biodiversity_index"),
        region=environment.get("region")
    )

    analysis = run_environmental_analysis(
        data,
        top_k=5,
        top_n=3,
        user_query=message,
        user_constraints=constraints
    )

    # Preserve conversation-level state explicitly.
    analysis["user_constraints"] = constraints
    analysis["tradeoff_question"] = is_tradeoff_question(message)
    analysis["action_plan_question"] = is_action_plan_question(message)

    return analysis


def chat_with_environmental_scientist(
    session_id: str,
    message: str
):

    if session_id not in conversation_memory:
        conversation_memory[session_id] = {
            "environment": {},
            "messages": [],
            "constraints": {},
            "pending_field": None
        }

    session = conversation_memory[session_id]

    previous_field = session.get("pending_field")

    environment_for_extraction = session["environment"].copy()

    if previous_field:
        environment_for_extraction["_last_question"] = previous_field

    environment = extract_environment_from_text(
        message,
        environment_for_extraction
    )

    constraints = update_constraints(
        message,
        session.get("constraints", {})
    )

    session["environment"] = environment
    session["constraints"] = constraints
    session["pending_field"] = None

    session["messages"].append({
        "role": "user",
        "content": message
    })

    missing = get_missing_fields(
        environment,
        message
    )

    if missing:

        next_field = missing[0]

        reply = (
            "I can analyze the environmental condition, "
            "but I need a little more information first.\n\n"
            + FIELD_QUESTIONS[next_field]
        )

        session["pending_field"] = next_field

        session["messages"].append({
            "role": "assistant",
            "content": reply
        })

        return {
            "type": "clarification",
            "message": reply,
            "environment": environment,
            "missing_fields": missing
        }

    analysis = run_chat_analysis(
        message,
        environment,
        constraints
    )

    report = generate_scientific_report(
        analysis
    )

    session["messages"].append({
        "role": "assistant",
        "content": report
    })

    return {
        "type": "analysis",
        "message": report,
        "environment": environment,
        "constraints": constraints,
        "analysis": analysis,
        "conversation_history": session["messages"]
    }