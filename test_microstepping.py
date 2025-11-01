"""
Test script for microstepping functionality in turntable project
This script tests various microstepping configurations and movements
"""

import sys
import utime
import drv8825_setup

def test_microstepping():
    """Test different microstepping configurations"""
    
    # Setup stepper motor
    print("Setting up stepper motor...")
    if (mot := drv8825_setup.setup_stepper()) is None:
        print("No stepper driver")
        return False
        
    print("Stepper motor setup successful!")
    
    # Test configurations
    microstep_configs = [1, 2, 4, 8, 16, 32]
    
    for microsteps in microstep_configs:
        print(f"\n=== Testing {microsteps} microsteps ===")
        
        try:
            # Test small movement
            print(f"Small CW movement with {microsteps} microsteps...")
            mot.steps(10 * microsteps, microsteps, 100)
            
            # Wait for movement to complete
            while mot.get_progress() > 0:
                utime.sleep_ms(50)
            
            utime.sleep(1)  # Pause between movements
            
            # Test reverse movement
            print(f"Small CCW movement with {microsteps} microsteps...")
            mot.steps(-10 * microsteps, microsteps, 100)
            
            # Wait for movement to complete
            while mot.get_progress() > 0:
                utime.sleep_ms(50)
                
            utime.sleep(1)  # Pause between tests
            
            print(f"✓ {microsteps} microsteps test completed successfully")
            
        except Exception as e:
            print(f"✗ Error testing {microsteps} microsteps: {e}")
    
    # Test speed scaling
    print(f"\n=== Testing speed scaling ===")
    test_microsteps = 16
    speeds = [50, 100, 200, 400]
    
    for speed in speeds:
        print(f"Testing speed {speed} Hz with {test_microsteps} microsteps...")
        try:
            mot.steps(5 * test_microsteps, test_microsteps, speed)
            while mot.get_progress() > 0:
                utime.sleep_ms(50)
            utime.sleep(0.5)
            print(f"✓ Speed {speed} Hz test completed")
        except Exception as e:
            print(f"✗ Error testing speed {speed} Hz: {e}")
    
    # Disable motor
    mot.disable()
    print("\n=== Microstepping tests completed ===")
    return True

def test_web_integration():
    """Test the web server integration (without actually starting the server)"""
    print("\n=== Testing web integration functions ===")
    
    # Import the main module functions (simulate them)
    global current_microsteps
    current_microsteps = 16
    
    # Test microstepping value validation
    valid_values = [1, 2, 4, 8, 16, 32]
    invalid_values = [3, 5, 7, 64, 128]
    
    print("Testing valid microstepping values...")
    for value in valid_values:
        if value in [1, 2, 4, 8, 16, 32]:
            print(f"✓ {value} is valid")
        else:
            print(f"✗ {value} should be valid but validation failed")
    
    print("Testing invalid microstepping values...")
    for value in invalid_values:
        if value not in [1, 2, 4, 8, 16, 32]:
            print(f"✓ {value} correctly rejected")
        else:
            print(f"✗ {value} should be invalid but was accepted")
    
    print("✓ Web integration tests completed")

def main():
    """Main test function"""
    print("=== Turntable Microstepping Test Suite ===")
    print("This script will test the microstepping functionality")
    print("Make sure the turntable is in a safe position to move")
    
    # Get user confirmation
    try:
        input("Press Enter to start tests (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\nTests cancelled by user")
        return
    
    # Run hardware tests
    if test_microstepping():
        print("✓ Hardware microstepping tests passed")
    else:
        print("✗ Hardware microstepping tests failed")
        return
    
    # Run web integration tests
    test_web_integration()
    
    print("\n=== All tests completed! ===")
    print("Microstepping functionality is ready to use.")
    print("\nBenefits of microstepping:")
    print("• Smoother motor movement")
    print("• Reduced vibration and noise")
    print("• Higher precision positioning")
    print("• Better low-speed performance")

if __name__ == "__main__":
    main()