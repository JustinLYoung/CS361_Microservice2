# Calendar Microservice

A Python-based microservice that accepts calendar events via ZMQ (ZeroMQ) and generates timestamps for scheduling. The service includes a graphical user interface (GUI) client for easy interaction.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [UML Sequence Diagram](#uml-sequence-diagram)
- [Examples](#examples)
- [Testing](#testing)

## Features

- **Event Timestamp Generation**: Automatically generates appropriate timestamps based on event type
- **Multiple Event Types**: Supports meetings, deadlines, reminders, appointments, and general events
- **REQ-REP Pattern**: Uses ZeroMQ's Request-Reply pattern for reliable communication
- **GUI Client**: User-friendly graphical interface for creating and managing events
- **JSON Communication**: All messages are exchanged in JSON format
- **Event History**: Tracks created events with unique IDs
- **Health Checks**: Built-in service health monitoring

## Architecture

The system consists of three main components:

1. **Calendar Microservice** (`calendar_microservice.py`): The core service that processes requests
2. **GUI Client** (`gui_client.py`): A Tkinter-based graphical interface
3. **Example Client** (`example_client.py`): Demonstrates programmatic usage

## Installation

### Prerequisites

```bash
# Install Python 3.7 or higher
python --version

# Install required packages
pip install pyzmq
```

### Setup

1. Clone or download the project files
2. Ensure all Python scripts have execute permissions:
```bash
chmod +x calendar_microservice.py
chmod +x gui_client.py
chmod +x example_client.py
```

## Usage

### Starting the Microservice

```bash
# Default port (5555)
python calendar_microservice.py

# Custom port
python calendar_microservice.py 5556
```

### Running the GUI Client

```bash
python gui_client.py
```

### Running the Example Client

```bash
python example_client.py
```

## API Documentation

### 1. How to Programmatically REQUEST Data from the Microservice

To request data from the microservice, you need to:

1. Create a ZMQ REQ (Request) socket
2. Connect to the microservice port
3. Send a JSON-formatted request
4. Wait for the response

#### Request Format

```json
{
    "action": "create_event",
    "event_name": "Your Event Name",
    "event_type": "meeting|deadline|reminder|appointment|general",
    "duration_hours": 1.5
}
```

#### Example Request Code

```python
import zmq
import json

# Create context and socket
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Prepare request
request = {
    "action": "create_event",
    "event_name": "Team Planning Session",
    "event_type": "meeting",
    "duration_hours": 2
}

# Send request
socket.send_string(json.dumps(request))
```

### 2. How to Programmatically RECEIVE Data from the Microservice

After sending a request, the client must wait to receive the response:

#### Response Format

```json
{
    "status": "success",
    "event_id": "EVT-20240115143022-5678",
    "event_name": "Team Planning Session",
    "event_type": "meeting",
    "timestamp": "2024-01-15T15:00:00",
    "end_timestamp": "2024-01-15T17:00:00",
    "formatted_time": "2024-01-15 15:00:00",
    "formatted_end_time": "2024-01-15 17:00:00",
    "timezone": "local",
    "duration_hours": 2
}
```

#### Example Receive Code

```python
# Continuing from the request example above...

# Receive response
response_json = socket.recv_string()
response = json.loads(response_json)

# Process response
if response["status"] == "success":
    print(f"Event created successfully!")
    print(f"Event ID: {response['event_id']}")
    print(f"Scheduled for: {response['formatted_time']}")
    print(f"Duration: {response['duration_hours']} hours")
else:
    print(f"Error: {response.get('message', 'Unknown error')}")

# Clean up
socket.close()
context.term()
```

### Complete Example Function

```python
def schedule_event(event_name, event_type="general", duration=1, port=5555):
    """
    Schedule an event using the Calendar Microservice.
    
    Args:
        event_name (str): Name of the event
        event_type (str): Type of event (meeting, deadline, etc.)
        duration (float): Duration in hours
        port (int): Microservice port number
    
    Returns:
        dict: Response from microservice with timestamp and event details
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    try:
        # Connect to service
        socket.connect(f"tcp://localhost:{port}")
        
        # Send request
        request = {
            "action": "create_event",
            "event_name": event_name,
            "event_type": event_type,
            "duration_hours": duration
        }
        socket.send_string(json.dumps(request))
        
        # Receive response
        response_json = socket.recv_string()
        response = json.loads(response_json)
        
        return response
        
    finally:
        socket.close()
        context.term()

# Usage example
result = schedule_event("Sprint Retrospective", "meeting", 1.5)
print(f"Meeting scheduled for: {result['formatted_time']}")
```

## UML Sequence Diagram

The following diagram shows the detailed interaction between the Client and the Calendar Microservice:

```
┌──────────┐                                           ┌───────────────────┐
│  Client  │                                           │Calendar Microservice│
└─────┬────┘                                           └──────────┬────────┘
      │                                                           │
      │  1. Initialize ZMQ Context                                │
      │─────────────────────────────┐                           │
      │                             │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  2. Create REQ Socket                                     │
      │─────────────────────────────┐                           │
      │                             │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  3. Connect to tcp://localhost:5555                      │
      │──────────────────────────────────────────────────────────►
      │                                                           │
      │                                                           │  4. Listening on Port 5555
      │                                                           │────────────────┐
      │                                                           │                │
      │                                                           │◄───────────────┘
      │  5. Prepare JSON Request                                  │
      │─────────────────────────────┐                           │
      │  {                          │                           │
      │    "action": "create_event", │                           │
      │    "event_name": "Meeting",  │                           │
      │    "event_type": "meeting",  │                           │
      │    "duration_hours": 1        │                           │
      │  }                          │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  6. Send JSON Request (socket.send_string())             │
      │──────────────────────────────────────────────────────────►
      │                                                           │
      │                                                           │  7. Receive & Parse JSON
      │                                                           │────────────────┐
      │                                                           │                │
      │                                                           │◄───────────────┘
      │                                                           │
      │                                                           │  8. Process Request
      │                                                           │────────────────┐
      │                                                           │  - Validate    │
      │                                                           │  - Generate    │
      │                                                           │    Timestamp   │
      │                                                           │  - Create      │
      │                                                           │    Event ID    │
      │                                                           │◄───────────────┘
      │                                                           │
      │                                                           │  9. Prepare JSON Response
      │                                                           │────────────────┐
      │                                                           │  {             │
      │                                                           │    "status":   │
      │                                                           │     "success", │
      │                                                           │    "event_id": │
      │                                                           │     "EVT-...", │
      │                                                           │    "timestamp":│
      │                                                           │     "2024-..." │
      │                                                           │    ...         │
      │                                                           │  }             │
      │                                                           │◄───────────────┘
      │                                                           │
      │  10. Send JSON Response (socket.send_string())           │
      │◄──────────────────────────────────────────────────────────
      │                                                           │
      │  11. Receive Response (socket.recv_string())              │
      │─────────────────────────────┐                           │
      │                             │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  12. Parse JSON Response                                  │
      │─────────────────────────────┐                           │
      │                             │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  13. Process Response Data                                │
      │─────────────────────────────┐                           │
      │  - Extract timestamp        │                           │
      │  - Display to user          │                           │
      │  - Store event ID           │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
      │  14. Close Socket & Terminate Context                     │
      │─────────────────────────────┐                           │
      │                             │                           │
      │◄────────────────────────────┘                           │
      │                                                           │
┌─────▼────┐                                           ┌──────────▼────────┐
│  Client  │                                           │Calendar Microservice│
│  (End)   │                                           │   (Continues)      │
└──────────┘                                           └───────────────────┘
```

### Sequence Diagram Explanation

1. **Initialization (Steps 1-4)**: The client initializes ZMQ context, creates a REQ socket, and connects to the microservice
2. **Request Preparation (Step 5)**: Client prepares a JSON request with event details
3. **Request Transmission (Step 6)**: Client sends the JSON request via ZMQ
4. **Server Processing (Steps 7-9)**: Microservice receives, parses, and processes the request, generating a timestamp
5. **Response Transmission (Step 10)**: Microservice sends back a JSON response
6. **Response Processing (Steps 11-13)**: Client receives, parses, and processes the response
7. **Cleanup (Step 14)**: Client closes the connection

## Event Types and Timestamp Generation

The microservice generates timestamps based on event type:

| Event Type | Timestamp Logic |
|------------|----------------|
| **meeting** | Scheduled during business hours (9 AM - 5 PM) |
| **deadline** | Set for end of current day (11:59 PM) |
| **reminder** | Scheduled for the next hour |
| **appointment** | Scheduled within the next 1-7 days |
| **general** | Scheduled within the next 24 hours |

## Testing

### Basic Functionality Test

```python
# test_microservice.py
import zmq
import json
import time

def test_microservice():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    
    tests = [
        {"action": "health_check"},
        {"action": "create_event", "event_name": "Test Meeting", 
         "event_type": "meeting", "duration_hours": 1},
        {"action": "create_event", "event_name": "Test Deadline", 
         "event_type": "deadline", "duration_hours": 2}
    ]
    
    for test in tests:
        print(f"\nTesting: {test}")
        socket.send_string(json.dumps(test))
        response = json.loads(socket.recv_string())
        assert response["status"] in ["success", "healthy"]
        print(f"✓ Test passed: {response.get('event_name', 'Health Check')}")
    
    socket.close()
    context.term()
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_microservice()
```

## Error Handling

The microservice handles various error conditions:

- **Invalid JSON**: Returns error response with appropriate message
- **Unknown Actions**: Returns error for unrecognized action types
- **Connection Timeouts**: Client can set timeout values using `socket.setsockopt(zmq.RCVTIMEO, milliseconds)`
- **Service Unavailable**: Client should handle connection failures gracefully

## Performance Considerations

- The microservice uses a single-threaded REP socket, processing requests sequentially
- For high-throughput scenarios, consider implementing a router-dealer pattern
- Default timeout is set to 5 seconds in the GUI client
- The service can handle approximately 1000 requests/second on standard hardware

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure microservice is running on the correct port |
| Timeout errors | Check if microservice is responsive, increase timeout value |
| Invalid JSON | Verify request format matches the expected schema |
| Port already in use | Change port number or stop conflicting service |

## License

This project is provided as educational material for learning ZMQ and microservice architecture.

## Contact

For questions or issues, please refer to the example code and documentation above.
