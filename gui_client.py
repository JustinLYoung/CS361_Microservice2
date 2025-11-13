#!/usr/bin/env python3
"""
Calendar Microservice GUI Client
A graphical interface for interacting with the Calendar Microservice.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import zmq
import json
import threading
from datetime import datetime
import queue


class CalendarGUI:
    """
    GUI client for the Calendar Microservice.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Calendar Microservice Client")
        self.root.geometry("900x700")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # ZMQ setup
        self.context = zmq.Context()
        self.socket = None
        self.connected = False
        self.port = 5555
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Create GUI components
        self.create_widgets()
        
        # Start message processing
        self.process_messages()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Calendar Microservice Client", 
                                font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Connection Section
        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(connection_frame, text="Server Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=0, column=1, padx=5)
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", 
                                         command=self.toggle_connection)
        self.connect_button.grid(row=0, column=2, padx=5)
        
        self.status_label = ttk.Label(connection_frame, text="Status: Disconnected", 
                                      foreground="red")
        self.status_label.grid(row=0, column=3, padx=20)
        
        # Event Creation Section
        event_frame = ttk.LabelFrame(main_frame, text="Create Event", padding="10")
        event_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Event Name
        ttk.Label(event_frame, text="Event Name:").grid(row=0, column=0, sticky=tk.W)
        self.event_name_entry = ttk.Entry(event_frame, width=40)
        self.event_name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Event Type
        ttk.Label(event_frame, text="Event Type:").grid(row=1, column=0, sticky=tk.W)
        self.event_type_var = tk.StringVar(value="general")
        self.event_type_combo = ttk.Combobox(event_frame, textvariable=self.event_type_var, 
                                             width=20, state="readonly")
        self.event_type_combo['values'] = ('general', 'meeting', 'deadline', 'reminder', 'appointment')
        self.event_type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Duration
        ttk.Label(event_frame, text="Duration (hours):").grid(row=2, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="1")
        self.duration_spinbox = ttk.Spinbox(event_frame, from_=0.5, to=24, increment=0.5, 
                                           textvariable=self.duration_var, width=10)
        self.duration_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Create Event Button
        self.create_event_button = ttk.Button(event_frame, text="Create Event", 
                                             command=self.create_event, state="disabled")
        self.create_event_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Response Section
        response_frame = ttk.LabelFrame(main_frame, text="Server Response", padding="10")
        response_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=8, width=70, 
                                                       wrap=tk.WORD)
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Events History Section
        history_frame = ttk.LabelFrame(main_frame, text="Events History", padding="10")
        history_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Treeview for events
        columns = ('Event ID', 'Event Name', 'Type', 'Timestamp', 'Duration')
        self.events_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        for col in columns:
            self.events_tree.heading(col, text=col)
            if col == 'Event ID':
                self.events_tree.column(col, width=150)
            elif col == 'Event Name':
                self.events_tree.column(col, width=200)
            else:
                self.events_tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Clear History", 
                  command=self.clear_history).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Health Check", 
                  command=self.health_check).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Exit", 
                  command=self.exit_app).grid(row=0, column=2, padx=5)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def toggle_connection(self):
        """Toggle connection to the microservice."""
        if not self.connected:
            self.connect_to_service()
        else:
            self.disconnect_from_service()
    
    def connect_to_service(self):
        """Connect to the Calendar Microservice."""
        try:
            port = int(self.port_entry.get())
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
            self.socket.connect(f"tcp://localhost:{port}")
            
            self.connected = True
            self.status_label.config(text="Status: Connected", foreground="green")
            self.connect_button.config(text="Disconnect")
            self.create_event_button.config(state="normal")
            
            self.add_message("Connected to Calendar Microservice", "success")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.add_message(f"Connection failed: {str(e)}", "error")
    
    def disconnect_from_service(self):
        """Disconnect from the Calendar Microservice."""
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.connected = False
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_button.config(text="Connect")
        self.create_event_button.config(state="disabled")
        
        self.add_message("Disconnected from Calendar Microservice", "info")
    
    def create_event(self):
        """Create a new event."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the service first.")
            return
        
        event_name = self.event_name_entry.get().strip()
        if not event_name:
            messagebox.showwarning("Invalid Input", "Please enter an event name.")
            return
        
        # Prepare request
        request_data = {
            'action': 'create_event',
            'event_name': event_name,
            'event_type': self.event_type_var.get(),
            'duration_hours': float(self.duration_var.get())
        }
        
        # Send request in a separate thread
        threading.Thread(target=self.send_request, args=(request_data,), daemon=True).start()
    
    def send_request(self, request_data):
        """
        Send request to the microservice (runs in separate thread).
        
        Args:
            request_data: Dictionary with request data
        """
        try:
            # Send request
            request_json = json.dumps(request_data)
            self.socket.send_string(request_json)
            
            # Receive response
            response_json = self.socket.recv_string()
            response_data = json.loads(response_json)
            
            # Queue the response for GUI update
            self.message_queue.put(('response', response_data))
            
        except zmq.error.Again:
            self.message_queue.put(('error', 'Request timeout - is the service running?'))
        except Exception as e:
            self.message_queue.put(('error', f'Request failed: {str(e)}'))
    
    def health_check(self):
        """Perform a health check on the service."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the service first.")
            return
        
        request_data = {'action': 'health_check'}
        threading.Thread(target=self.send_request, args=(request_data,), daemon=True).start()
    
    def process_messages(self):
        """Process messages from the queue (runs in main thread)."""
        try:
            while not self.message_queue.empty():
                msg_type, msg_data = self.message_queue.get_nowait()
                
                if msg_type == 'response':
                    self.handle_response(msg_data)
                elif msg_type == 'error':
                    self.add_message(msg_data, 'error')
                    messagebox.showerror("Error", msg_data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def handle_response(self, response_data):
        """
        Handle response from the microservice.
        
        Args:
            response_data: Dictionary with response data
        """
        # Display response in text area
        response_formatted = json.dumps(response_data, indent=2)
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, response_formatted)
        
        # Add to history if it's an event creation
        if response_data.get('status') == 'success' and 'event_id' in response_data:
            self.events_tree.insert('', 0, values=(
                response_data.get('event_id', ''),
                response_data.get('event_name', ''),
                response_data.get('event_type', ''),
                response_data.get('formatted_time', ''),
                f"{response_data.get('duration_hours', 0)} hours"
            ))
            
            # Clear input fields
            self.event_name_entry.delete(0, tk.END)
            self.event_type_var.set('general')
            self.duration_var.set('1')
            
            self.add_message(f"Event created: {response_data.get('event_name')}", 'success')
    
    def add_message(self, message, msg_type='info'):
        """
        Add a message to the response area.
        
        Args:
            message: Message text
            msg_type: Type of message (info, success, error)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_msg = f"[{timestamp}] {message}\n"
        self.response_text.insert(tk.END, formatted_msg)
        self.response_text.see(tk.END)
    
    def clear_history(self):
        """Clear the events history."""
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        self.add_message("Events history cleared", "info")
    
    def exit_app(self):
        """Exit the application."""
        if self.connected:
            self.disconnect_from_service()
        
        if self.context:
            self.context.term()
        
        self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = CalendarGUI(root)
    
    # Handle window close
    def on_closing():
        app.exit_app()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
