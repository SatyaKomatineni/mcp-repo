# MCP Server with Function Calling Support

This guide explains how the extended MCP server implementation supports function calling with Claude Desktop.

## Overview

The extended server adds support for:
1. Registering custom functions
2. Listing available functions
3. Executing function calls
4. Including function information in completions

## How Function Calling Works

Function calling in the MCP protocol follows this general flow:

1. The server registers one or more functions with schemas
2. When the client requests a completion, the server includes information about available functions
3. The assistant (Claude) decides when to use a function and includes a function call in its response
4. The client extracts the function call and sends it to the server
5. The server executes the function and returns the result
6. The client can send the function result back to the assistant

## New Endpoints

### Function Registration

```python
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
```

This endpoint allows you to register a new function with:
- A unique name
- A description
- A JSON Schema for parameters

### Listing Functions

```python
@app.route("/api/mcp/v1/functions", methods=["GET"])
def list_functions():
    return jsonify(list(functions.values())), 200
```

This endpoint returns all registered functions.

### Getting a Function

```python
@app.route("/api/mcp/v1/functions/<function_id>", methods=["GET"])
def get_function(function_id):
    if function_id not in functions:
        return jsonify({"error": "Function not found"}), 404
    
    return jsonify(functions[function_id]), 200
```

This endpoint retrieves a specific function by ID.

### Function Execution

```python
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
```

This endpoint executes a function call with the provided parameters.

### System Configuration

```python
@app.route("/api/mcp/v1/system/config", methods=["GET"])
def get_system_config():
    return jsonify({
        "available_functions": list(functions.values()),
        "version": "0.1.0",
        "name": "Simple MCP Server with Function Support"
    }), 200
```

This endpoint provides system configuration information including available functions.

## Enhanced Completion Endpoint

The completion endpoint has been updated to include function information:

```python
@app.route("/api/mcp/v1/completions", methods=["POST"])
def create_completion():
    # ... [existing code] ...
    
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
    
    # ... [existing code] ...
```

This enhancement:
1. Checks for available functions
2. Includes information about functions in the response
3. Optionally includes a tool call if the client supports it

## Demo Functions

For testing purposes, the server initializes with two demo functions:

1. **get_weather** - Gets weather information for a location
2. **calculate** - Performs a mathematical calculation

```python
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
```

## Using the Server with Claude Desktop

To use this server with Claude Desktop:

1. Run the server:
   ```bash
   python mcp_function_server.py
   ```

2. Configure Claude Desktop to use your server:
   - Open Claude Desktop
   - Go to Settings
   - Look for the "Custom MCP Server" option
   - Enter `http://localhost:5000` as the server URL
   - Save your settings

3. Start a conversation in Claude Desktop
   - The server will inform Claude about available functions
   - Claude will be able to use these functions in the conversation

## Implementing Actual Function Execution

In a production environment, you would want to replace the mock function execution with actual functionality:

```python
# Example of implementing the calculate function
def calculate_function(parameters):
    expression = parameters.get("expression")
    try:
        # Be careful with eval - you may want to use a safer alternative
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Then in the execute_function route:
if function_name == "calculate":
    result = calculate_function(parameters)
    # Return the result
```

## Function Registration API

You can register custom functions using the API:

```bash
curl -X POST http://localhost:5000/api/mcp/v1/functions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_custom_function",
    "description": "Does something amazing",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "First parameter"
        }
      },
      "required": ["param1"]
    }
  }'
```

## Security Considerations

For a production deployment, consider:

1. Adding authentication to protect function registration and execution
2. Validating function parameters against their schema
3. Implementing rate limiting
4. Adding proper error handling and logging
5. Using a sandboxed environment for function execution
