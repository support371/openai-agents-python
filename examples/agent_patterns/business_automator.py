import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, trace
from examples.auto_mode import input_with_fallback

"""
This example assembles a practical "business automator" stack.

Given project highlights, an orchestrator agent calls specialized sub-agents as tools to produce:
1. a strategic plan,
2. an execution backlog,
3. a deployment and operations runbook,
4. and a prioritized list of automations.
"""


class AutomationCandidate(BaseModel):
    name: str
    objective: str
    trigger: str
    owner: str
    priority: str


class AutomationBlueprint(BaseModel):
    strategic_priorities: list[str]
    recommended_agents: list[str]
    deployment_runbook: list[str]
    first_automations: list[AutomationCandidate]
    first_30_days: list[str]


strategy_agent = Agent(
    name="strategy_agent",
    instructions=(
        "You are a strategy consultant for product and operations teams. "
        "Given project highlights, identify goals, constraints, KPIs, and the top risks. "
        "Return concise, practical recommendations that can guide engineering execution."
    ),
)

execution_planner_agent = Agent(
    name="execution_planner_agent",
    instructions=(
        "You are a delivery lead. Convert strategy into a practical execution plan. "
        "Provide milestones, owner suggestions, dependency notes, and measurable outputs. "
        "Favor a phase-based approach (foundation, pilot, scale)."
    ),
)

deployment_agent = Agent(
    name="deployment_agent",
    instructions=(
        "You are a platform and DevOps architect. Build a deployment-ready runbook for agent systems, "
        "covering environments, observability, testing gates, incident handling, and rollback strategy. "
        "Keep the guidance vendor-neutral and implementation ready."
    ),
)

automation_architect_agent = Agent(
    name="automation_architect_agent",
    instructions=(
        "You design automation workflows for business teams. Recommend high-impact automations first, "
        "then medium-impact ones. For each automation, include objective, trigger, owner role, and "
        "priority rationale. Focus on workflows that reduce manual work and cycle time."
    ),
)

business_automator_orchestrator = Agent(
    name="business_automator_orchestrator",
    instructions=(
        "You are the chief agent architect for a growing business. Always use the provided tools before "
        "finalizing your answer. Build an implementation-ready blueprint with: strategic priorities, "
        "recommended agent roster, deployment runbook, first automations, and a 30-day rollout plan."
    ),
    tools=[
        strategy_agent.as_tool(
            tool_name="build_strategy",
            tool_description="Extract strategy, goals, KPIs, and risks from project highlights.",
        ),
        execution_planner_agent.as_tool(
            tool_name="build_execution_plan",
            tool_description="Convert strategy into milestones and delivery phases.",
        ),
        deployment_agent.as_tool(
            tool_name="build_deployment_runbook",
            tool_description="Define deployment and reliability plan for agent systems.",
        ),
        automation_architect_agent.as_tool(
            tool_name="design_automations",
            tool_description="Recommend prioritized business automations.",
        ),
    ],
    output_type=AutomationBlueprint,
)


async def main() -> None:
    highlights = input_with_fallback(
        "Paste project highlights: ",
        (
            "B2B SaaS startup with long onboarding cycles, fragmented CRM updates, manual weekly KPI reporting, "
            "and frequent launch delays due to unclear handoffs between product, engineering, and GTM teams."
        ),
    )

    with trace("business automator blueprint"):
        result = await Runner.run(business_automator_orchestrator, highlights)

    blueprint = result.final_output_as(AutomationBlueprint)

    print("\n=== Strategic priorities ===")
    for item in blueprint.strategic_priorities:
        print(f"- {item}")

    print("\n=== Recommended agents ===")
    for item in blueprint.recommended_agents:
        print(f"- {item}")

    print("\n=== Deployment runbook ===")
    for item in blueprint.deployment_runbook:
        print(f"- {item}")

    print("\n=== First automations ===")
    for item in blueprint.first_automations:
        print(
            f"- {item.name} ({item.priority})\\n"
            f"  Objective: {item.objective}\\n"
            f"  Trigger: {item.trigger}\\n"
            f"  Owner: {item.owner}"
        )

    print("\n=== First 30 days ===")
    for item in blueprint.first_30_days:
        print(f"- {item}")


if __name__ == "__main__":
    asyncio.run(main())
