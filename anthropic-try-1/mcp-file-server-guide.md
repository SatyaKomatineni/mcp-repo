# MCP Server with File System Integration

This guide explains how to use the MCP server that integrates with the file system, allowing Claude Desktop to access and manipulate text files.

## Overview

This MCP server implementation allows Claude Desktop to:

1. List available text files
2. Read the content of text files
3. Search for text across all files
4. Write to text files (create or update)

The server makes these capabilities available through function calling, which Claude Desktop can use during conversations.

## Setup Instructions

### Prerequisites

- Python 3.6+
- Flask

### Installation

1. Save the server code to a file (e.g., `mcp_file_server.py`)

2. Install required dependencies:
   ```bash
   pip install flask
   ```

3. Run the server:
   ```bash
   python mcp_file_server.py
   ```

4. The server will create a `./resources` directory and populate it with sample files

### Connecting with Claude Desktop

1. Open Claude Desktop
2. Go to Settings
3. Look for the "Custom MCP Server" option
4. Enter `http://localhost:5000` as the server URL
5. Save your settings

## Using File Functions in Conversations

Once connected, you can ask Claude about files and it will use the available functions to help you. Here are some example prompts:

### Listing Files

"What files do you have access to?"

Claude will use the `list_files` function to show you all available text files in the resources directory.

### Reading Files

"Can you show me the content of welcome.txt?"

Claude will use the `read_file` function to display the content of the specified file.

### Searching Across Files

"Can you search all files for the word 'sample'?"

Claude will use the `search_files` function to find all occurrences of "sample" across all files.

### Writing to Files

"Create a new file named notes.txt with the following content: This is my first note."

Claude will use the `write_file` function to create or update the specified file with the provided content.

## File Functions Reference

### list_files

Lists all available text files in the resources directory.

**Parameters:** None

**Returns:**
- `success`: Boolean indicating success or failure
- `files`: Array of filenames
- `count`: Number of files

**Example request:**
```json
{
  "name": "list_files",
  "parameters": {}
}
```

### read_file

Reads the content of a specified text file.

**Parameters:**
- `filename`: Name of the file to read (including extension)

**Returns:**
- `success`: Boolean indicating success or failure
- `filename`: Name of the file
- `content`: Content of the file
- `size`: Size of the content in characters

**Example request:**
```json
{
  "name": "read_file",
  "parameters": {
    "filename": "welcome.txt"
  }
}
```

### search_files

Searches for text across all files.

**Parameters:**
- `query`: Text to search for

**Returns:**
- `success`: Boolean indicating success or failure
- `query`: The search query
- `results`: Array of objects with filename and match count
- `total_matches`: Number of files with matches

**Example request:**
```json
{
  "name": "search_files",
  "parameters": {
    "query": "sample"
  }
}
```

### write_file

Writes content to a text file (creates or overwrites).

**Parameters:**
- `filename`: Name of the file to write (including extension)
- `content`: Content to write to the file

**Returns:**
- `success`: Boolean indicating success or failure
- `filename`: Name of the file
- `size`: Size of the content in characters
- `message`: Success message

**Example request:**
```json
{
  "name": "write_file",
  "parameters": {
    "filename": "notes.txt",
    "content": "This is my first note."
  }
}
```

## Sample Files

The server creates three sample files on startup:

1. **welcome.txt**: A welcome message
2. **instructions.txt**: Basic instructions on using the file functions
3. **sample_data.txt**: Sample text for testing the search functionality

## Directory Structure

By default, all files are stored in the `./resources` directory relative to where the server is running. You can change this by modifying the `FILE_DIRECTORY` variable in the code.

## Security Considerations

This implementation has several limitations and security considerations:

1. **No Authentication**: Anyone with access to the server can read and write files
2. **Limited to Text Files**: The implementation is designed for text files only
3. **No Directory Traversal Protection**: There's minimal protection against accessing files outside the resources directory
4. **No File Size Limits**: Large files could cause performance issues

For production use, you should add:
- Authentication
- Input validation
- Resource limits
- Proper error handling

## Extending the Implementation

You can extend this implementation in several ways:

1. **Support for more file types**: Add functions for handling binary files, PDFs, etc.
2. **File metadata**: Add functions to get file creation/modification dates
3. **Directory management**: Add functions to create/delete directories
4. **File operations**: Add functions for copying, moving, or deleting files
5. **File sharing**: Add capabilities to share files with others

## Troubleshooting

If you encounter issues:

1. Check the server logs for errors
2. Ensure the resources directory exists and is writable
3. Verify file permissions
4. Make sure the server URL is correctly configured in Claude Desktop

## Example Conversation with Claude

Here's an example conversation showing how Claude might use these file functions:

**User**: What files do you have access to?

**Claude**: Let me check the available files for you.

[Claude uses the list_files function]

I found 3 files in the resources directory:
- welcome.txt
- instructions.txt
- sample_data.txt

Would you like me to show you the content of any of these files?

**User**: Yes, please show me the content of welcome.txt.

**Claude**: I'll retrieve the content of welcome.txt for you.

[Claude uses the read_file function]

Here's the content of welcome.txt:

Welcome to the MCP File Server!

This is a sample text file that demonstrates how the MCP server can access files on the filesystem.

**User**: Can you search all files for the word "sample"?

**Claude**: I'll search all files for the word "sample".

[Claude uses the search_files function]

I found "sample" in the following files:
- welcome.txt: 1 match
- sample_data.txt: 2 matches

Would you like me to show the content of any of these files to see the context?
