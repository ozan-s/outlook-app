"""Test defensive COM iteration patterns.

This test ensures that COM collection iteration doesn't rely on the Count property
which can be unreliable, and instead uses defensive iteration patterns.
"""

def test_defensive_iteration_pattern():
    """Test that defensive iteration handles COM collections safely."""
    
    # Mock COM collection that demonstrates the Count issue
    class MockCOMCollection:
        def __init__(self, items, unreliable_count=None):
            self._items = items
            self._unreliable_count = unreliable_count or len(items)
        
        @property 
        def Count(self):
            return self._unreliable_count
        
        def __getitem__(self, index):
            # COM collections are 1-indexed
            if index < 1 or index > len(self._items):
                raise Exception(f"Index {index} out of range")
            return self._items[index - 1]
    
    # Test case: Count says 5 but only 3 items accessible
    problematic_collection = MockCOMCollection(
        items=["Item1", "Item2", "Item3"],
        unreliable_count=5  # Count lies!
    )
    
    # Old approach (Count-based) - would fail
    def count_based_iteration(collection):
        results = []
        errors = []
        for i in range(1, collection.Count + 1):
            try:
                item = collection[i]
                results.append(item)
            except Exception as e:
                errors.append(f"Error at index {i}: {e}")
        return results, errors
    
    # New approach (defensive) - should handle gracefully  
    def defensive_iteration(collection):
        results = []
        errors = []
        index = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while consecutive_failures < max_consecutive_failures:
            try:
                item = collection[index]
                results.append(item)
                consecutive_failures = 0  # Reset on success
                index += 1
            except Exception as e:
                errors.append(f"Skipping inaccessible item at index {index}: {e}")
                consecutive_failures += 1
                index += 1
                
                # Safety check: don't iterate forever
                if index > collection.Count + max_consecutive_failures:
                    break
        
        return results, errors
    
    # Test both approaches
    count_results, count_errors = count_based_iteration(problematic_collection)
    defensive_results, defensive_errors = defensive_iteration(problematic_collection)
    
    # Count-based should have failures
    assert len(count_errors) == 2  # Failed on indices 4 and 5
    assert len(count_results) == 3  # But got the 3 real items
    
    # Defensive should handle gracefully
    print(f"Defensive results: {len(defensive_results)}, errors: {len(defensive_errors)}")
    print(f"Defensive errors: {defensive_errors}")
    assert len(defensive_results) == 3  # Got all real items
    assert len(defensive_errors) >= 2   # Recorded the failures (might be more due to consecutive failure limit)
    assert defensive_results == ["Item1", "Item2", "Item3"]


def test_defensive_iteration_stops_correctly():
    """Test that defensive iteration stops after consecutive failures."""
    
    # Mock COM collection that demonstrates the Count issue
    class MockCOMCollection:
        def __init__(self, items, unreliable_count=None):
            self._items = items
            self._unreliable_count = unreliable_count or len(items)
        
        @property 
        def Count(self):
            return self._unreliable_count
        
        def __getitem__(self, index):
            # COM collections are 1-indexed
            if index < 1 or index > len(self._items):
                raise Exception(f"Index {index} out of range")
            return self._items[index - 1]
    
    # Test case: 2 real items, Count says 10
    collection = MockCOMCollection(["Item1", "Item2"], 10)
    
    def defensive_iteration(collection):
        results = []
        errors = []
        index = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while consecutive_failures < max_consecutive_failures:
            try:
                item = collection[index]
                results.append(item)
                consecutive_failures = 0
                index += 1
            except Exception as e:
                errors.append(f"Skipping inaccessible item at index {index}: {e}")
                consecutive_failures += 1
                index += 1
                
                # Safety check: don't iterate forever
                if index > collection.Count + max_consecutive_failures:
                    break
        
        return results, errors
    
    results, errors = defensive_iteration(collection)
    
    # Should get both real items
    assert len(results) == 2
    assert results == ["Item1", "Item2"]
    
    # Should stop after 3 consecutive failures
    assert len(errors) == 3
    assert "index 3" in errors[0]
    assert "index 4" in errors[1] 
    assert "index 5" in errors[2]


if __name__ == '__main__':
    test_defensive_iteration_pattern()
    test_defensive_iteration_stops_correctly()
    print("All defensive iteration tests passed!")