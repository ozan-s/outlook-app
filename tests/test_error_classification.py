"""Test error classification logic for COM interface validation.

This test ensures that we properly classify expected vs problematic errors,
and don't use inappropriate error thresholds like 30%.
"""

def test_error_classification_logic():
    """Test that errors are properly classified as expected vs problematic."""
    
    # Sample error scenarios
    test_scenarios = [
        {
            "total_folders": 10,
            "errors": [
                "Skipping inaccessible folder at index 4: Permission denied",
                "Skipping inaccessible folder at index 7: Network timeout"
            ],
            "expected_status": "success",
            "reason": "Minor access issues are expected in enterprise environments"
        },
        {
            "total_folders": 5,
            "errors": [
                "Cannot connect to MAPI namespace",
                "Outlook.Application failed to initialize",
                "COM connection lost"
            ],
            "expected_status": "failed",
            "reason": "System-level failures indicate real problems"
        },
        {
            "total_folders": 0,
            "errors": [
                "No folders found",
                "MAPI namespace is empty"
            ],
            "expected_status": "failed", 
            "reason": "No folders found indicates configuration problem"
        },
        {
            "total_folders": 50,
            "errors": [
                f"Skipping inaccessible folder at index {i}: Access denied" 
                for i in range(10, 20)  # 10 access denied errors
            ],
            "expected_status": "success",
            "reason": "Many folders found, some access issues normal"
        }
    ]
    
    def classify_test_result(total_folders, errors):
        """Classify test result based on folder count and error types."""
        total_errors = len(errors)
        
        # Rule 1: If no folders found, it's a failure
        if total_folders == 0:
            return "failed", "No folders accessible"
        
        # Rule 2: Check for system-level errors
        system_errors = [
            "MAPI", "COM connection", "Application failed", 
            "namespace", "Cannot connect"
        ]
        
        for error in errors:
            for system_error in system_errors:
                if system_error.lower() in error.lower():
                    return "failed", f"System-level error detected: {system_error}"
        
        # Rule 3: If we have folders and only access/permission errors, it's success
        access_errors = ["access", "permission", "inaccessible", "denied"]
        all_access_errors = all(
            any(access_word in error.lower() for access_word in access_errors)
            for error in errors
        )
        
        if total_folders > 0 and all_access_errors:
            return "success", f"Found {total_folders} folders with {total_errors} minor access issues"
        
        # Rule 4: Mixed errors - use a reasonable threshold (not 30%!)
        if total_folders > 0:
            error_ratio = total_errors / (total_folders + total_errors)
            if error_ratio < 0.1:  # Less than 10% error rate
                return "success", f"Found {total_folders} folders with {total_errors} minor errors"
            else:
                return "failed", f"Too many errors: {total_errors} errors for {total_folders} folders"
        
        return "failed", "Unable to classify result"
    
    # Test each scenario
    for scenario in test_scenarios:
        status, reason = classify_test_result(scenario["total_folders"], scenario["errors"]) 
        
        print(f"Scenario: {scenario['reason']}")
        print(f"  Expected: {scenario['expected_status']}, Got: {status}")
        print(f"  Reason: {reason}")
        
        assert status == scenario["expected_status"], f"Wrong classification for: {scenario['reason']}"


def test_30_percent_threshold_is_inappropriate():
    """Test that 30% error threshold is too high and should be replaced."""
    
    # Scenario: 10 folders found, 3 errors (30% error rate) 
    # Old logic: PASS (30% threshold)
    # New logic: Should probably still pass but with lower threshold
    
    total_folders = 10
    errors = [
        "Skipping inaccessible folder at index 4: Access denied",
        "Skipping inaccessible folder at index 7: Permission denied", 
        "Skipping inaccessible folder at index 9: Network timeout"
    ]
    
    # Old approach - 30% threshold
    def old_classification(total_folders, errors):
        error_ratio = len(errors) / max(total_folders + len(errors), 1)
        if error_ratio > 0.3:  # 30% threshold
            return "failed"
        return "success"
    
    # New approach - better logic
    def new_classification(total_folders, errors):
        if total_folders == 0:
            return "failed"
        
        # Check error types first
        access_errors = ["access", "permission", "denied", "network", "timeout"]
        all_minor_errors = all(
            any(keyword in error.lower() for keyword in access_errors)
            for error in errors
        )
        
        if all_minor_errors:
            return "success"  # Minor errors are acceptable
        
        # Use lower threshold for unknown error types
        error_ratio = len(errors) / (total_folders + len(errors))
        return "success" if error_ratio < 0.1 else "failed"
    
    old_result = old_classification(total_folders, errors)
    new_result = new_classification(total_folders, errors)
    
    # Both should pass this scenario (minor access errors)
    assert old_result == "success", "Old 30% threshold should pass this scenario"
    assert new_result == "success", "New classification should pass minor access errors"
    
    # But new approach should be more strict with unknown errors
    unknown_errors = [
        "Unknown error type 1",
        "System crashed",
        "Unexpected exception"
    ]
    
    old_unknown = old_classification(total_folders, unknown_errors)
    new_unknown = new_classification(total_folders, unknown_errors)
    
    # Old approach might pass, new should be more careful
    assert new_unknown == "failed", "New classification should be strict with unknown errors"


if __name__ == '__main__':
    test_error_classification_logic()
    test_30_percent_threshold_is_inappropriate()
    print("All error classification tests passed!")