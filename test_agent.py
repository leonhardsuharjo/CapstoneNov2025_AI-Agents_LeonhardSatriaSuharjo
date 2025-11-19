''' test_agent.py file that will be used to test agent for setup purposes ''' 
#to be run before running all the other files to ensure all needed libraries actually work perfectly and know which one doesnt work if any

# test_agent.py
# Simple Agent Testing
# Based on: Day 4b "Agent Evaluation"

from supplier_database import get_all_prices_for_component, COMPONENTS
from main import check_component_prices, calculate_price_change

def test_price_check_tool():
    '''Test that price check tool works correctly.'''
    print("\nTest 1: Price Check Tool")
    print("-" * 50)

    result = check_component_prices("ESP32_WIFI")

    assert result["status"] == "success", "Price check should succeed"
    assert len(result["prices"]) == 3, "Should have 3 suppliers"
    print("Price check tool working correctly")
    print(f"   Found prices from {len(result['prices'])} suppliers")

def test_price_change_calculation():
    '''Test that price change calculation works.'''
    print("\nTest 2: Price Change Calculation")
    print("-" * 50)

    # Test normal price increase
    result = calculate_price_change(4.50, 4.20)
    assert result["status"] == "success"
    assert result["change_percent"] > 0
    print(f"Change calculation working")
    print(f"   4.50 vs 4.20 = {result['change_percent']}% change")

    # Test high risk scenario (>10% increase)
    result2 = calculate_price_change(3.40, 2.90)
    assert result2["risk_level"] == "HIGH", "Should detect high risk"
    print(f"Risk detection working")
    print(f"   3.40 vs 2.90 = {result2['change_percent']}% = {result2['risk_level']} RISK")

def test_agent_workflow():
    '''Test the complete agent workflow.'''
    print("\nTest 3: Complete Agent Workflow")
    print("-" * 50)

    # This tests that our agents can work together
    # Step 1: Get prices
    prices = check_component_prices("TEMP_SENSOR")
    assert prices["status"] == "success"
    print("Step 1: Price retrieval works")

    # Step 2: Calculate changes
    for price_data in prices["prices"]:
        change = calculate_price_change(
            price_data["current_price"],
            price_data["last_month_price"]
        )
        print(f"   {price_data['supplier']}: {change['risk_level']} risk")

    print("Step 2: Price comparison works")
    print("Agent workflow complete!")

def run_all_tests():
    '''Run all tests.'''
    print("\n" + "=" * 70)
    print("RUNNING AGENT TESTS")
    print("=" * 70)

    try:
        test_price_check_tool()
        test_price_change_calculation()
        test_agent_workflow()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70 + "\n")
        return True

    except AssertionError as e:
        print(f"\n TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n ERROR: {e}\n")
        return False

if __name__ == "__main__":
    run_all_tests()
