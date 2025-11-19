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

