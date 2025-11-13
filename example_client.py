#!/usr/bin/env python3
"""
Example Client for Calendar Microservice
Demonstrates how to programmatically interact with the Calendar Microservice.
"""

import zmq
import json
import time


class CalendarClient:
    """
    A simple client for interacting with the Calendar Microservice.
    """
    
    def __init__(self, port=5555):
        """
        Initialize the client.
        
        Args:
            port (int): Port number of the microservice
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")
        print(f"Connected to Calendar Microservice on port {port}")
    
    def create_event(self, event_name, event_type="general", duration_hours=1):
        """
        Request to create an event and receive a timestamp.
        
        Args:
            event_name (str): Name of the event
            event_type (str): Type of event (general, meeting, deadline, reminder, appointment)
            duration_hours (float): Duration of the event in hours
            
        Returns:
            dict: Response from the microservice
        """
        # Prepare the request
        request_data = {
            'action': 'create_event',
            'event_name': event_name,
            'event_type': event_type,
            'duration_hours': duration_hours
        }
        
        # Send request
        request_json = json.dumps(request_data)
        print(f"\nSending request: {request_json}")
        self.socket.send_string(request_json)
        
        # Receive response
        response_json = self.socket.recv_string()
        response_data = json.loads(response_json)
        print(f"Received response: {json.dumps(response_data, indent=2)}")
        
        return response_data
    
    def health_check(self):
        """
        Perform a health check on the microservice.
        
        Returns:
            dict: Health check response
        """
        request_data = {'action': 'health_check'}
        
        # Send request
        request_json = json.dumps(request_data)
        print(f"\nSending health check request...")
        self.socket.send_string(request_json)
        
        # Receive response
        response_json = self.socket.recv_string()
        response_data = json.loads(response_json)
        print(f"Health check response: {json.dumps(response_data, indent=2)}")
        
        return response_data
    
    def close(self):
        """Close the client connection."""
        self.socket.close()
        self.context.term()
        print("Client connection closed")


def main():
    """
    Example usage of the Calendar Client.
    """
    print("=" * 60)
    print("Calendar Microservice - Example Client")
    print("=" * 60)
    
    # Create client
    client = CalendarClient(port=5555)
    
    try:
        # Example 1: Health Check
        print("\n1. HEALTH CHECK EXAMPLE")
        print("-" * 30)
        health_response = client.health_check()
        
        time.sleep(1)
        
        # Example 2: Create a Meeting
        print("\n2. CREATE MEETING EXAMPLE")
        print("-" * 30)
        meeting_response = client.create_event(
            event_name="Team Standup Meeting",
            event_type="meeting",
            duration_hours=0.5
        )
        
        time.sleep(1)
        
        # Example 3: Create a Deadline
        print("\n3. CREATE DEADLINE EXAMPLE")
        print("-" * 30)
        deadline_response = client.create_event(
            event_name="Project Submission",
            event_type="deadline",
            duration_hours=2
        )
        
        time.sleep(1)
        
        # Example 4: Create a Reminder
        print("\n4. CREATE REMINDER EXAMPLE")
        print("-" * 30)
        reminder_response = client.create_event(
            event_name="Call Client",
            event_type="reminder",
            duration_hours=0.25
        )
        
        time.sleep(1)
        
        # Example 5: Create an Appointment
        print("\n5. CREATE APPOINTMENT EXAMPLE")
        print("-" * 30)
        appointment_response = client.create_event(
            event_name="Doctor's Appointment",
            event_type="appointment",
            duration_hours=1.5
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY OF CREATED EVENTS")
        print("=" * 60)
        
        events = [meeting_response, deadline_response, reminder_response, appointment_response]
        for event in events:
            if event.get('status') == 'success':
                print(f"\n• {event['event_name']}")
                print(f"  ID: {event['event_id']}")
                print(f"  Time: {event['formatted_time']}")
                print(f"  Duration: {event['duration_hours']} hours")
        
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
