from flask import Flask, request, jsonify
import uuid
import json
import logging
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory storage
conversations = {}
messages = {}
functions = {}

# Configuration for file resources
FILE_DIRECTORY = "./resources"  # Directory containing text files
if not os.path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY)

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

# File resource functions

def register_file_functions():
    """Register functions for interacting with text files"""
    
    # Function to list available files
    functions["list_files"] = {
        "name": "list_files",
        "description": "List all available text files in the resources directory",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    # Function to read a file
    functions["read_file"] = {
        "name": "read_file",
        "description": "Read the content of a text file",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to read (including extension)"
                }
            },
            "required": ["filename"]
        }
    }
    
    # Function to search within files
    functions["search_files"] = {
        "name": "search_files",
        "description": "Search for text across all files",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for"
                }
            },
            "required": ["query"]
        }
    }
    
    # Function to write to a file
    functions["write_file"] = {
        "name": "write_file",
        "description": "Write content to a text file (creates or overwrites)",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to write (including extension)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["filename", "content"]
        }
    }

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
    
    result = {"success": False, "error": "Function execution not implemented"}
    
    try:
        # Implement file-based functions
        if function_name == "list_files":
            files = [f for f in os.listdir(FILE_DIRECTORY) if os.path.isfile(os.path.join(FILE_DIRECTORY, f))]
            result = {
                "success": True,
                "files": files,
                "count": len(files)
            }
        
        elif function_name == "read_file":
            filename = parameters.get("filename")
            if not filename:
                result = {"success": False, "error": "Filename is required"}
            else:
                file_path = os.path.join(FILE_DIRECTORY, filename)
                if not os.path.exists(file_path):
                    result = {"success": False, "error": f"File not found: {filename}"}
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    result = {
                        "success": True,
                        "filename": filename,
                        "content": content,
                        "size": len(content)
                    }
        
        elif function_name == "search_files":
            query = parameters.get("query")
            if not query:
                result = {"success": False, "error": "Search query is required"}
            else:
                search_results = []
                for filename in os.listdir(FILE_DIRECTORY):
                    file_path = os.path.join(FILE_DIRECTORY, filename)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                if query.lower() in content.lower():
                                    search_results.append({
                                        "filename": filename,
                                        "matches": content.lower().count(query.lower())
                                    })
                        except Exception as e:
                            logging.error(f"Error reading file {filename}: {str(e)}")
                
                result = {
                    "success": True,
                    "query": query,
                    "results": search_results,
                    "total_matches": len(search_results)
                }
        
        elif function_name == "write_file":
            filename = parameters.get("filename")
            content = parameters.get("content")
            
            if not filename or content is None:
                result = {"success": False, "error": "Filename and content are required"}
            else:
                file_path = os.path.join(FILE_DIRECTORY, filename)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                result = {
                    "success": True,
                    "filename": filename,
                    "size": len(content),
                    "message": f"Successfully wrote to {filename}"
                }
        
        else:
            result = {"success": False, "error": f"Function implementation not found for {function_name}"}
    
    except Exception as e:
        result = {"success": False, "error": str(e)}
    
    response = {
        "id": str(uuid.uuid4()),
        "function": function_name,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    
    logging.info(f"Executed function: {function_name}")
    return jsonify(response), 200

@app.route("/api/mcp/v1/completions", methods=["POST"])
def create_completion():
    data = request.get_json()
    
    # Validate request
    if "conversation_id" not in data or "messages" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    conversation_id = data["conversation_id"]
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    user_messages = [msg for msg in data["messages"] if msg.get("role") == "user"]
    latest_user_message = user_messages[-1]["content"] if user_messages else ""
    
    # Check if the message might be asking about files
    file_related_keywords = ["file", "document", "text", "read", "write", "search", "list"]
    is_file_related = any(keyword in latest_user_message.lower() for keyword in file_related_keywords)
    
    message_id = str(uuid.uuid4())
    
    # Generate a response based on the context
    content = "This is a simulated response from the MCP server."
    
    if is_file_related:
        content = "I notice you're asking about files. I can help you with that using my file functions. "
        content += "I can list files, read file content, search across files, or write to files. "
        content += "Would you like me to perform any of these operations for you?"
    
    response_message = {
        "id": message_id,
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "role": "assistant",
        "content": content,
        "metadata": {}
    }
    
    # Store the message
    messages[message_id] = response_message
    
    # Update conversation
    conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
    
    logging.info(f"Created completion message: {message_id} in conversation: {conversation_id}")
    return jsonify(response_message), 201

@app.route("/api/mcp/v1/system/config", methods=["GET"])
def get_system_config():
    return jsonify({
        "available_functions": list(functions.values()),
        "version": "0.1.0",
        "name": "MCP Server with File System Integration",
        "file_directory": FILE_DIRECTORY
    }), 200

# Create a sample text file for testing
def create_sample_files():
    sample_files = {
        "welcome.txt": "Welcome to the MCP File Server!\n\nThis is a sample text file that demonstrates how the MCP server can access files on the filesystem.",
        "instructions.txt": "MCP File Server Instructions:\n\n1. Use the list_files function to see available files\n2. Use read_file to view file contents\n3. Use search_files to find text across files\n4. Use write_file to create or update files",
        "sample_data.txt": "This is some sample data that can be used for testing the search functionality. Try searching for terms like 'sample', 'data', or 'testing'."
    }
    
    for filename, content in sample_files.items():
        file_path = os.path.join(FILE_DIRECTORY, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    
    logging.info(f"Created {len(sample_files)} sample files in {FILE_DIRECTORY}")

if __name__ == "__main__":
    # Register file functions
    register_file_functions()
    
    # Create sample files
    create_sample_files()
    
    app.run(debug=True, host="0.0.0.0", port=5000)
