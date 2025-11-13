#!/usr/bin/env python3
"""
Calendar Microservice
A ZMQ-based microservice that accepts events and returns timestamps.
"""

import zmq
import json
import logging
from datetime import datetime, timedelta
import random
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalendarMicroservice:
    """
    A microservice that processes calendar events and generates timestamps.
    """
    
    def __init__(self, port=5555):
        """
        Initialize the Calendar Microservice.
        
        Args:
            port (int): Port number for ZMQ socket
        """
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)  # REP socket for request-reply pattern
        self.socket.bind(f"tcp://*:{port}")
        logger.info(f"Calendar Microservice started on port {port}")
        
    def generate_timestamp(self, event_data):
        """
        Generate a timestamp based on the event data.
        
        Args:
            event_data (dict): Event information
            
        Returns:
            dict: Response with timestamp and event details
        """
        try:
            event_name = event_data.get('event_name', 'Unknown Event')
            event_type = event_data.get('event_type', 'general')
            duration_hours = event_data.get('duration_hours', 1)
            
            # Generate timestamp based on event type
            now = datetime.now()
            
            if event_type == 'meeting':
                # Schedule meetings during business hours
                timestamp = self._get_next_business_hour(now)
            elif event_type == 'deadline':
                # Set deadlines for end of day
                timestamp = now.replace(hour=23, minute=59, second=59)
            elif event_type == 'reminder':
                # Set reminders for next hour
                timestamp = now + timedelta(hours=1)
            elif event_type == 'appointment':
                # Schedule appointments in the next 1-7 days
                days_ahead = random.randint(1, 7)
                timestamp = now + timedelta(days=days_ahead)
                timestamp = timestamp.replace(hour=random.randint(9, 17), minute=0, second=0)
            else:
                # Default: schedule within next 24 hours
                timestamp = now + timedelta(hours=random.randint(1, 24))
            
            # Calculate end time
            end_timestamp = timestamp + timedelta(hours=duration_hours)
            
            response = {
                'status': 'success',
                'event_id': self._generate_event_id(),
                'event_name': event_name,
                'event_type': event_type,
                'timestamp': timestamp.isoformat(),
                'end_timestamp': end_timestamp.isoformat(),
                'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'formatted_end_time': end_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': 'local',
                'duration_hours': duration_hours
            }
            
            logger.info(f"Generated timestamp for event '{event_name}': {timestamp}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating timestamp: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_next_business_hour(self, current_time):
        """Get the next available business hour (9 AM - 5 PM)."""
        if current_time.hour < 9:
            return current_time.replace(hour=9, minute=0, second=0)
        elif current_time.hour >= 17:
            # Next business day at 9 AM
            next_day = current_time + timedelta(days=1)
            return next_day.replace(hour=9, minute=0, second=0)
        else:
            # Next hour during business hours
            return current_time + timedelta(hours=1)
    
    def _generate_event_id(self):
        """Generate a unique event ID."""
        return f"EVT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
    
    def run(self):
        """
        Run the microservice main loop.
        """
        logger.info("Calendar Microservice is ready to accept requests...")
        
        try:
            while True:
                # Wait for request
                message = self.socket.recv_string()
                logger.info(f"Received request: {message}")
                
                try:
                    # Parse JSON request
                    request_data = json.loads(message)
                    
                    # Process the request
                    if request_data.get('action') == 'create_event':
                        response = self.generate_timestamp(request_data)
                    elif request_data.get('action') == 'health_check':
                        response = {
                            'status': 'healthy',
                            'service': 'Calendar Microservice',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        response = {
                            'status': 'error',
                            'message': f"Unknown action: {request_data.get('action')}"
                        }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    response = {
                        'status': 'error',
                        'message': 'Invalid JSON format'
                    }
                
                # Send response
                response_json = json.dumps(response)
                self.socket.send_string(response_json)
                logger.info(f"Sent response: {response_json[:100]}...")
                
        except KeyboardInterrupt:
            logger.info("Shutting down Calendar Microservice...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.socket.close()
        self.context.term()
        logger.info("Calendar Microservice shutdown complete")


def main():
    """Main entry point."""
    # Get port from command line argument if provided
    port = 5555
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Create and run the microservice
    service = CalendarMicroservice(port=port)
    service.run()


if __name__ == "__main__":
    main()
