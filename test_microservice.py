#!/usr/bin/env python3
"""
Test script for Calendar Microservice
Verifies that the microservice is working correctly.
"""

import zmq
import json
import time
import subprocess
import sys
import threading


def start_microservice():
    """Start the microservice in a subprocess."""
    print("Starting Calendar Microservice...")
    process = subprocess.Popen(
        [sys.executable, "calendar_microservice.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Give service time to start
    return process


def test_basic_functionality():
    """Test basic microservice functionality."""
    print("\n" + "=" * 60)
    print("Calendar Microservice Test Suite")
    print("=" * 60)
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
    
    try:
        socket.connect("tcp://localhost:5555")
        print("✓ Connected to microservice")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return False
    
    # Test cases
    test_cases = [
        {
            "name": "Health Check",
            "request": {"action": "health_check"},
            "expected_status": "healthy"
        },
        {
            "name": "Create Meeting Event",
            "request": {
                "action": "create_event",
                "event_name": "Team Standup",
                "event_type": "meeting",
                "duration_hours": 0.5
            },
            "expected_status": "success"
        },
        {
            "name": "Create Deadline Event",
            "request": {
                "action": "create_event",
                "event_name": "Project Submission",
                "event_type": "deadline",
                "duration_hours": 2
            },
            "expected_status": "success"
        },
        {
            "name": "Create Reminder Event",
            "request": {
                "action": "create_event",
                "event_name": "Call Client",
                "event_type": "reminder",
                "duration_hours": 0.25
            },
            "expected_status": "success"
        },
        {
            "name": "Invalid Action",
            "request": {"action": "invalid_action"},
            "expected_status": "error"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n{'=' * 40}")
        print(f"Test: {test['name']}")
        print(f"{'=' * 40}")
        
        try:
            # Send request
            request_json = json.dumps(test['request'])
            print(f"Request: {request_json}")
            socket.send_string(request_json)
            
            # Receive response
            response_json = socket.recv_string()
            response = json.loads(response_json)
            print(f"Response: {json.dumps(response, indent=2)}")
            
            # Verify response
            if response.get('status') == test['expected_status']:
                print(f"✓ Test PASSED: {test['name']}")
                passed += 1
                
                # Additional validations for successful event creation
                if test['expected_status'] == 'success':
                    assert 'event_id' in response, "Missing event_id"
                    assert 'timestamp' in response, "Missing timestamp"
                    assert 'formatted_time' in response, "Missing formatted_time"
                    print(f"  Event ID: {response['event_id']}")
                    print(f"  Scheduled: {response['formatted_time']}")
            else:
                print(f"✗ Test FAILED: {test['name']}")
                print(f"  Expected status: {test['expected_status']}")
                print(f"  Got status: {response.get('status')}")
                failed += 1
                
        except zmq.error.Again:
            print(f"✗ Test FAILED: {test['name']} - Timeout")
            failed += 1
        except Exception as e:
            print(f"✗ Test FAILED: {test['name']} - {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print(f"Total Tests: {len(test_cases)}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    # Cleanup
    socket.close()
    context.term()
    
    return failed == 0


def test_concurrent_requests():
    """Test concurrent request handling."""
    print("\n" + "=" * 60)
    print("Concurrent Request Test")
    print("=" * 60)
    
    results = []
    
    def make_request(event_name, event_type):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")
        
        request = {
            "action": "create_event",
            "event_name": event_name,
            "event_type": event_type,
            "duration_hours": 1
        }
        
        socket.send_string(json.dumps(request))
        response_json = socket.recv_string()
        response = json.loads(response_json)
        
        results.append(response)
        
        socket.close()
        context.term()
    
    # Create threads for concurrent requests
    threads = []
    for i in range(5):
        t = threading.Thread(
            target=make_request,
            args=(f"Concurrent Event {i}", "general")
        )
        threads.append(t)
    
    # Start all threads
    print("Sending 5 concurrent requests...")
    start_time = time.time()
    for t in threads:
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    
    # Check results
    successful = sum(1 for r in results if r.get('status') == 'success')
    print(f"✓ Completed {len(results)} requests in {elapsed:.2f} seconds")
    print(f"  Successful: {successful}/{len(results)}")
    
    # Verify all have unique event IDs
    event_ids = [r.get('event_id') for r in results if 'event_id' in r]
    if len(event_ids) == len(set(event_ids)):
        print("✓ All event IDs are unique")
    else:
        print("✗ Duplicate event IDs detected")
    
    return successful == len(results)


def main():
    """Main test runner."""
    print("Calendar Microservice Test Runner")
    print("=" * 60)
    
    # Check if service is already running
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect("tcp://localhost:5555")
        
        # Try health check
        socket.send_string(json.dumps({"action": "health_check"}))
        response = socket.recv_string()
        print("✓ Microservice is already running")
        
        socket.close()
        context.term()
        
        service_process = None
        
    except:
        print("Microservice not running, starting it...")
        service_process = start_microservice()
    
    try:
        # Run tests
        basic_passed = test_basic_functionality()
        concurrent_passed = test_concurrent_requests()
        
        if basic_passed and concurrent_passed:
            print("\n" + "=" * 60)
            print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            return 1
            
    finally:
        # Stop service if we started it
        if service_process:
            print("\nStopping microservice...")
            service_process.terminate()
            service_process.wait()


if __name__ == "__main__":
    sys.exit(main())
