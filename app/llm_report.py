import os
import json
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Check your .env file."
    )


client = genai.Client(
    api_key=api_key
)


MODEL_NAME = "gemini-3.5-flash-lite"


def generate_scientific_report(reasoning_package):

    user_question = reasoning_package.get(
        "user_query",
        "No specific user question was provided."
    )

    user_constraints = reasoning_package.get(
        "user_constraints",
        {}
    )

    action_plan_question = reasoning_package.get(
        "action_plan_question",
        False
    )

    tradeoff_question = reasoning_package.get(
        "tradeoff_question",
        False
    )

    no_trees = user_constraints.get(
        "no_trees",
        False
    )

    prompt = f"""
You are the environmental intelligence assistant
for the Darukaa Earth biodiversity system.

Your task is to answer the user's environmental question
using ONLY the structured environmental assessment and
scientific evidence provided by the system.

The reasoning engine has already performed:
- environmental risk detection
- multi-metric reasoning
- intervention selection
- scientific evidence retrieval

You must explain the results clearly.

==================================================
USER QUESTION
==================================================

{user_question}


==================================================
USER CONSTRAINTS
==================================================

{json.dumps(user_constraints, indent=2)}

IMPORTANT:

If no_trees is true:

- The user does NOT want tree planting.
- NEVER recommend agroforestry.
- NEVER mention agroforestry as an option.
- NEVER include tree planting in an action plan.
- NEVER suggest trees as an alternative.
- Respect this constraint throughout the entire answer.


==================================================
REQUEST TYPE
==================================================

Action plan requested:
{action_plan_question}

Trade-off discussion requested:
{tradeoff_question}


==================================================
STRUCTURED ENVIRONMENTAL ASSESSMENT
==================================================

{json.dumps(reasoning_package, indent=2)}


==================================================
SCIENTIFIC RULES
==================================================

1. Directly answer the user's question.

2. Use ONLY information contained in the
   structured environmental assessment.

3. Do NOT invent scientific evidence.

4. Do NOT invent sources, papers, reports, URLs,
   measurements, statistics, or numerical estimates.

5. Do NOT introduce recommendations that are not
   present in the recommendation engine output.

6. Do NOT change environmental measurements.

7. Clearly distinguish:
   - observed conditions
   - inferred risks
   - recommendations

8. Explain relationships between MULTIPLE
   environmental variables.

9. For every recommendation explain:
   - What to do
   - Why it is relevant
   - Which metrics may be affected
   - Time horizon
   - Scientific evidence

10. Use cautious scientific language:
   "may help"
   "can support"
   "may contribute to"
   "is associated with"

11. Do not create numerical improvement estimates.

12. If measurements are missing, explicitly say so.

13. Do not rank recommendations using your own judgment.

14. Do not introduce interventions outside
    the recommendation engine output.

15. Respect all user constraints.

==================================================
TRADE-OFF HANDLING
==================================================

If the user asks about risks, drawbacks,
disadvantages, negative effects, or trade-offs:

DO NOT simply repeat the recommendations.

Create a dedicated:

## Trade-offs and Limitations

For each relevant recommendation from the
structured assessment:

- identify a potential ecological or implementation
  trade-off only if it is supported by the provided
  information
- explain why it may occur
- identify the metric potentially affected
- state whether it depends on local conditions
- identify missing information

Do NOT invent numerical impacts.

If the provided evidence does not contain enough
information to establish a specific trade-off,
say that the available evidence is insufficient
to determine it rather than inventing one.


==================================================
1-YEAR ACTION PLAN HANDLING
==================================================

If the user asks for a 1-year action plan:

DO NOT return the normal recommendation format alone.

Create:

## 1-Year Action Plan

Use four phases:

### Months 0–3
### Months 3–6
### Months 6–9
### Months 9–12

Only use interventions present in the
recommendation engine output.

For each phase include:

- Action
- Environmental metric to monitor
- Reason it is relevant
- Evidence source when provided

Do NOT invent exact application rates,
fertilizer quantities, irrigation amounts,
planting densities, species, or dates.

If the system does not provide enough information
to specify an exact operational detail, explicitly
say that local agronomic planning is required.

The action plan should be practical but scientifically
cautious.

If no_trees is true, absolutely no tree-related
intervention may appear anywhere in the plan.


==================================================
NORMAL RESPONSE FORMAT
==================================================

If this is NOT an action-plan question:

## 1. Environmental Situation

Briefly describe the relevant environmental conditions.

--------------------------------------------------

## 2. Key Risks

Explain the risks identified by the reasoning engine.

For each risk:
- severity
- reasoning

Do not create additional risks.

--------------------------------------------------

## 3. Multi-Metric Reasoning

Explain how the provided environmental variables
interact.

Focus on relationships among:
- rainfall
- soil moisture
- soil organic carbon
- land use
- biodiversity
- crop system

Only discuss variables present in the assessment.

--------------------------------------------------

## 4. Recommended Interventions

Present the recommendations supplied by the
recommendation engine.

For each:

### Intervention

**What to do:**

**Why it is relevant:**

**Metrics affected:**

**Time horizon:**

Do not add interventions.

--------------------------------------------------

## 5. Scientific Evidence

For each recommendation list only evidence
provided by the retrieval system.

Use:

**Source:** provided source

**Evidence:** provided evidence

**Reference:** provided URL

--------------------------------------------------

If this IS an action-plan question:

Use:

## 1. Current Environmental Situation

## 2. Key Risks

## 3. Multi-Metric Reasoning

## 4. 1-Year Action Plan

### Months 0–3

### Months 3–6

### Months 6–9

### Months 9–12

## 5. Scientific Evidence

## 6. Monitoring and Missing Information


==================================================
FINAL CHECK
==================================================

Before answering verify:

- The user's actual question was answered.
- User constraints are respected.
- If no_trees is true, ZERO agroforestry/tree recommendations appear.
- Every intervention came from the recommendation engine.
- Every scientific source came from retrieved evidence.
- No measurements were changed.
- No unsupported numbers were added.
- Multi-metric reasoning is included.
- Missing information is acknowledged.
- Trade-off questions have a dedicated trade-off section.
- Action-plan questions have a four-phase 1-year plan.
"""


    for attempt in range(2):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response and response.text:
                return response.text

            return (
                "## AI Scientific Assessment\n\n"
                "The structured environmental analysis completed "
                "successfully, but the narrative response was empty."
            )

        except Exception as e:

            error_text = str(e).lower()

            if (
                "429" in error_text
                or "quota" in error_text
                or "404" in error_text
                or "not found" in error_text
            ):
                return (
                    "## AI Scientific Assessment\n\n"
                    "The AI narrative generation service is "
                    "temporarily unavailable.\n\n"
                    "The structured environmental risks, "
                    "multi-metric reasoning, recommendations, "
                    "user constraints, and retrieved scientific "
                    "evidence are still available in the analysis."
                )

            if attempt == 0:
                time.sleep(2)

    return (
        "## AI Scientific Assessment\n\n"
        "The AI narrative generation service is temporarily "
        "unavailable."
    )