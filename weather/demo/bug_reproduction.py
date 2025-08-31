#!/usr/bin/env python3
"""
🐛 ARCADE BUG REPRODUCTION SCRIPT

This script demonstrates a critical serialization bug in Arcade's runtime:
- Empty List[Dict] works fine
- Non-empty List[Dict] returns None instead of the actual data

This is a minimal reproduction case for the Arcade engineering team.
"""

try:
    from arcadepy import Arcade
    ARCADE_AVAILABLE = True
except ImportError:
    ARCADE_AVAILABLE = False
    print("❌ Install: pip install arcadepy")


def demonstrate_arcade_list_dict_bug():
    """Minimal reproduction of the List[Dict] serialization bug."""
    
    if not ARCADE_AVAILABLE:
        return
    
    print("🐛 ARCADE SERIALIZATION BUG REPRODUCTION")
    print("=" * 50)
    print("Bug: Non-empty List[Dict[str, Any]] returns None in Arcade runtime")
    print("Expected: Should return the actual list data")
    print()
    
    # Initialize client
    client = Arcade(api_key="arc_o19usaCegaoBJDD3xqmQGYktA8hm3syPBeLQeGdSgDtuJR4QsHnK")
    
    print("🧪 Testing different return types:")
    print("-" * 30)
    
    # Test 1: String - WORKS
    try:
        result = client.tools.execute(
            tool_name="Weather_BugDemoEmptyList",
            input={"location": "test"},
            user_id="bug_report"
        )
        status = "✅ WORKS" if result.output.value is not None else "❌ FAILS"
        print(f"{status} Empty List[Dict]:     {result.output.value}")
    except Exception as e:
        print(f"❌ Empty List[Dict]:     ERROR - {e}")
    
    # Test 2: Non-empty List[Dict] - FAILS!
    try:
        result = client.tools.execute(
            tool_name="Weather_BugDemoNonEmptyList", 
            input={"location": "test"},
            user_id="bug_report"
        )
        status = "✅ WORKS" if result.output.value is not None else "❌ FAILS"
        print(f"{status} Non-empty List[Dict]: {result.output.value}")
    except Exception as e:
        print(f"❌ Non-empty List[Dict]: ERROR - {e}")
    
    print()
    print("🎯 BUG ANALYSIS:")
    print("   ✅ Empty List[Dict] serializes correctly")
    print("   ❌ Non-empty List[Dict] returns None (serialization failure)")
    print("   💡 Workaround: Use Dict with list inside: {'data': [...]}")
    print()
    print("📧 Please report this to Arcade engineering team!")
    print("🔧 Environment: Python 3.13, macOS, Arcade CLI latest")


if __name__ == "__main__":
    demonstrate_arcade_list_dict_bug()