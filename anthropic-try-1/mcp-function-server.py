from flask import Flask, request, jsonify
import uuid
import json
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory storage
conversations = {}
messages = {}
functions = {}  # Store registered functions

@app.route("/api/mcp/v1/conversations", methods=["POST"])
def create_conversation():
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = {
        "id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "title": "New Conversation",
        "metadata": {}
    }
    
    logging.info(f"Created conversation: {conversation_id}")
    return jsonify(conversations[conversation_id]), 201

@app.route("/api/mcp/v1/conversations", methods=["GET"])
def list_conversations():
    return jsonify(list(conversations.values())), 200

@app.route("/api/mcp/v1/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    return jsonify(conversations[conversation_id]), 200

@app.route("/api/mcp/v1/conversations/<conversation_id>/messages", methods=["POST"])
def create_message(conversation_id):
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    data = request.get_json()
    
    # Validate request
    if "role" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    message_id = str(uuid.uuid4())
    messages[message_id] = {
        "id": message_id,
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "role": data["role"],
        "content": data["content"],
        "metadata": data.get("metadata", {})
    }
    
    # Update conversation
    conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
    
    logging.info(f"Created message: {message_id} in conversation: {conversation_id}")
    return jsonify(messages[message_id]), 201

@app.route("/api/mcp/v1/conversations/<conversation_id>/messages", methods=["GET"])
def list_messages(conversation_id):
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    # Filter messages by conversation_id
    conversation_messages = [msg for msg in messages.values() if msg["conversation_id"] == conversation_id]
    return jsonify(conversation_messages), 200

# New endpoints for function registration and handling

@app.route("/api/mcp/v1/functions", methods=["POST"])
def register_function():
    data = request.get_json()
    
    # Validate request
    required_fields = ["name", "description", "parameters"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    function_id = data.get("name")
    functions[function_id] = {
        "name": data["name"],
        "description": data["description"],
        "parameters": data["parameters"]
    }
    
    logging.info(f"Registered function: {function_id}")
    return jsonify(functions[function_id]), 201

@app.route("/api/mcp/v1/functions", methods=["GET"])
def list_functions():
    return jsonify(list(functions.values())), 200

@app.route("/api/mcp/v1/functions/<function_id>", methods=["GET"])
def get_function(function_id):
    if function_id not in functions:
        return jsonify({"error": "Function not found"}), 404
    
    return jsonify(functions[function_id]), 200

@app.route("/api/mcp/v1/function_calls", methods=["POST"])
def execute_function():
    data = request.get_json()
    
    # Validate request
    if "name" not in data or "parameters" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    function_name = data["name"]
    parameters = data["parameters"]
    
    if function_name not in functions:
        return jsonify({"error": f"Function not found: {function_name}"}), 404
    
    # In a real implementation, you would execute the function here
    # For this demo, we'll just echo back that we received the call
    
    result = {
        "id": str(uuid.uuid4()),
        "function": function_name,
        "result": f"Executed {function_name} with parameters: {json.dumps(parameters)}",
        "timestamp": datetime.now().isoformat()
    }
    
    logging.info(f"Executed function: {function_name}")
    return jsonify(result), 200

@app.route("/api/mcp/v1/completions", methods=["POST"])
def create_completion():
    data = request.get_json()
    
    # Validate request
    if "conversation_id" not in data or "messages" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    conversation_id = data["conversation_id"]
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    available_functions = list(functions.values()) if functions else []
    
    # Here you would normally process the messages and generate a response
    # For this demo, we'll create a response that includes function info if available
    
    message_id = str(uuid.uuid4())
    
    # Create a response that mentions available functions
    content = "This is a simulated response from the MCP server."
    
    if available_functions:
        content += f" I see you have {len(available_functions)} functions available: "
        content += ", ".join([func["name"] for func in available_functions])
        content += ". You can ask me to use these functions in our conversation."
    
    response_message = {
        "id": message_id,
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "role": "assistant",
        "content": content,
        "metadata": {}
    }
    
    # If there's a tool_calls field in the request, we can include available functions
    if data.get("tool_choice") != "none" and available_functions:
        # This indicates to the client that there are available functions
        response_message["tool_calls"] = [
            {
                "id": str(uuid.uuid4()),
                "type": "function",
                "function": {
                    "name": available_functions[0]["name"],
                    "arguments": "{}"  # Empty arguments as an example
                }
            }
        ]
    
    # Store the message
    messages[message_id] = response_message
    
    # Update conversation
    conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
    
    logging.info(f"Created completion message: {message_id} in conversation: {conversation_id}")
    return jsonify(response_message), 201

# Add a system configuration endpoint that provides available functions
@app.route("/api/mcp/v1/system/config", methods=["GET"])
def get_system_config():
    return jsonify({
        "available_functions": list(functions.values()),
        "version": "0.1.0",
        "name": "Simple MCP Server with Function Support"
    }), 200

# Demo functions for testing
def initialize_demo_functions():
    # Weather function
    functions["get_weather"] = {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature"
                }
            },
            "required": ["location"]
        }
    }
    
    # Calculator function
    functions["calculate"] = {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }

if __name__ == "__main__":
    # Initialize demo functions
    initialize_demo_functions()
    
    app.run(debug=True, host="0.0.0.0", port=5000)
