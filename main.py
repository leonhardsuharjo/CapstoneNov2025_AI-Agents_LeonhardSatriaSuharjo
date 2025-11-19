'''' main.py file == py file that will host main AI agent module'''

''' program structure in steps recapped: 
1. Install dependencies.
2. Configure Gemini API key. -- setup in local laptop 
3. Import ADK and Gemini components.
4. Build and define agents.
5. Set agent instructions and tools.
6. Run agent pipeline in cell order.
'''
#learning notebook involved in this code == notebook 2a on the custom function tools 

#main libraries import 
import os
from google.genai import types
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

# Import our supplier database -- MUST finish database.py first
from supplier_database import get_all_prices_for_component, COMPONENTS

# --- ---
# CUSTOM FUNCTION TOOLS (From Day 2a Notebook)
# --- ---

# TOOL 1: Check prices across all suppliers
# SOURCE: Day 2a, Section 2.1 "Building Custom Function Tools"
# Pattern: Dictionary returns with status field (Best Practice from Day 2a)
def check_component_prices(component_code: str) -> dict:
    '''Checks current prices for a component across all suppliers.

    This tool retrieves pricing data from the supplier database.

    Args:
        component_code: The component code (e.g., "ESP32_WIFI")

    Returns:
        Dictionary with status and pricing data from all suppliers.
    '''
    # Call database function
    result = get_all_prices_for_component(component_code)

    if result["status"] == "error":
        return result

    return {
        "status": "success",
        "component": result["component_name"],
        "prices": result["prices"]
    }


# TOOL 2: Calculate price change percentage
# SOURCE: Day 2a, Section 2.1 "Building Custom Function Tools"  
# Pattern: Type hints + clear docstring (Best Practice from Day 2a)
def calculate_price_change(current_price: float, last_month_price: float) -> dict:
    '''Calculate percentage change in price.

    Args:
        current_price: Current price in EUR
        last_month_price: Last month's price in EUR

    Returns:
        Dictionary with change percentage and risk level.
    '''
    if last_month_price == 0:
        return {
            "status": "error",
            "error_message": "Cannot calculate change - last month price is zero"
        }

    # Calculate percentage change
    change_percent = ((current_price - last_month_price) / last_month_price) * 100

    # Determine risk level
    # >10% increase = HIGH RISK to tender commitments
    # 5-10% increase = MEDIUM RISK
    # <5% increase = LOW RISK
    if change_percent > 10:
        risk = "HIGH"
        alert = " ALERT: Price spike detected!"
    elif change_percent > 5:
        risk = "MEDIUM"
        alert = " WARNING: Moderate price increase"
    else:
        risk = "LOW"
        alert = " Price stable"

    return {
        "status": "success",
        "change_percent": round(change_percent, 2),
        "risk_level": risk,
        "alert": alert
    }

# --- ---
# MULTI-AGENT SYSTEM (From Day 1b Notebook)
# --- ---

# Configure retry options (from both Day 1b and Day 2a)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# AGENT 1: Price Check Agent
# SOURCE: Day 1b, Section 3.1 "Sequential Workflows"
# Pattern: output_key stores result in state for next agent
price_check_agent = Agent(
    name="PriceCheckAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction='''You are a price monitoring specialist.

    Use the check_component_prices tool to get current prices from all suppliers.
    Present the findings clearly with supplier names and prices.
    ''',
    tools=[FunctionTool(check_component_prices)],
    output_key="price_data"  # <-- From Day 1b: stores result in state
)

# AGENT 2: Comparison Agent  
# SOURCE: Day 1b, Section 3.1 "Sequential Workflows"
# Pattern: Uses {price_data} from previous agent's output_key
comparison_agent = Agent(
    name="ComparisonAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction='''You are a price comparison analyst.

    Given price data: {price_data}

    Use the calculate_price_change tool for each supplier to:
    1. Calculate price change from last month
    2. Identify risk level
    3. Find the best (lowest) current price

    Present your analysis clearly.
    ''',
    tools=[FunctionTool(calculate_price_change)],
    output_key="comparison_results"  # <-- Stores for next agent
)

# AGENT 3: Recommendation Agent
# SOURCE: Day 1b, Section 3.1 "Sequential Workflows"
# Pattern: Final agent that generates user-facing recommendation
recommendation_agent = Agent(
    name="RecommendationAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction='''You are a procurement advisor.

    Given comparison results: {comparison_results}

    Provide clear recommendation:
    1. Which supplier to use (lowest current price)
    2. Any price spike alerts (>10% increase)
    3. Impact on tender commitments

    Format:
    RECOMMENDATION: [Supplier Name]
    CURRENT PRICE: €X.XX
    ALERTS: [Any price spike warnings]
    RATIONALE: [Why this choice]
    ''',
    output_key="final_recommendation"
)

# SEQUENTIAL AGENT - Runs agents in ORDER
# SOURCE: Day 1b, Section 3 "Sequential Workflows - The Assembly Line"
# Pattern: Guaranteed order execution - PriceCheck → Comparison → Recommendation
root_agent = SequentialAgent(
    name="SupplyChainMonitor",
    sub_agents=[price_check_agent, comparison_agent, recommendation_agent]
)

# --- ---
# RUNNER (From both Day 1b and Day 2a)
# --- --- 

def run_price_monitor(component_code: str):
    '''Run the price monitoring agent system.'''

    print(f"\n{'='*70}")
    print(f"SMART MATERIAL PRICE MONITOR")
    print(f"Component: {COMPONENTS.get(component_code, 'Unknown')}")
    print(f"{'='*70}\n")

    # Create runner - SOURCE: Day 1b Section 3
    runner = InMemoryRunner(agent=root_agent)

    # Run agent with user query
    import asyncio

    async def async_run():
        response = await runner.run_debug(
            f"Check prices for component: {component_code}"
        )
        return response

    # Execute
    response = asyncio.run(async_run())

    print(f"\n{'='*70}")
    print("MONITORING COMPLETE")
    print(f"{'='*70}\n")

# --- ---
# MAIN EXECUTION 
# --- --- 

if __name__ == "__main__":
    # Set API key
    if "GOOGLE_API_KEY" not in os.environ:
        api_key = input("Enter your GOOGLE_API_KEY: ").strip()
        os.environ["GOOGLE_API_KEY"] = api_key

    print("\nAvailable components:")
    for code, name in COMPONENTS.items():
        print(f"  {code}: {name}")

    # Get user input
    component = input("\nEnter component code to monitor (or press Enter for ESP32_WIFI): ").strip()
    if not component:
        component = "ESP32_WIFI"

    # Run the agent system
    run_price_monitor(component)