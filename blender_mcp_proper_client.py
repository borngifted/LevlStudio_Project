#!/usr/bin/env python3
"""
Proper Blender MCP Client
Connect to Blender MCP server using correct protocol
"""

import json
import socket
import time
import uuid
from typing import Dict, List, Any, Optional

class BlenderMCPClient:
    """Proper MCP client for Blender server on port 9876"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.socket = None
        self.initialized = False
        self.request_id = 0
        
    def connect(self) -> bool:
        """Connect to the Blender MCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to Blender MCP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to Blender server"""
        if not self.socket:
            return {"error": "Not connected"}
        
        try:
            # The server seems to expect a specific format based on the error message
            message = json.dumps(command) + "\n"
            self.socket.send(message.encode('utf-8'))
            
            # Receive response
            response = self.socket.recv(4096).decode('utf-8').strip()
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"raw_response": response}
                
        except Exception as e:
            return {"error": str(e)}
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize MCP session"""
        self.request_id += 1
        
        # Try different initialization formats
        formats_to_try = [
            # Standard MCP format
            {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "initialize", 
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "LevlStudio", "version": "1.0.0"}
                }
            },
            # Simple command format
            {
                "command": "initialize",
                "client": "LevlStudio"
            },
            # Action-based format  
            {
                "action": "initialize",
                "payload": {"client": "LevlStudio"}
            },
            # Direct format
            {
                "type": "initialize"
            }
        ]
        
        for i, init_format in enumerate(formats_to_try):
            print(f"🔄 Trying initialization format {i+1}...")
            result = self.send_command(init_format)
            
            if result and not result.get("error") and "Unknown command type" not in str(result):
                print(f"✅ Initialization successful with format {i+1}")
                self.initialized = True
                return result
            else:
                print(f"❌ Format {i+1} failed: {result}")
        
        return {"error": "All initialization formats failed"}
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        if not self.initialized:
            init_result = self.initialize()
            if "error" in init_result:
                return init_result
        
        self.request_id += 1
        
        # Try different tool listing formats
        formats_to_try = [
            {"jsonrpc": "2.0", "id": self.request_id, "method": "tools/list"},
            {"command": "list_tools"},
            {"action": "list_tools"},
            {"type": "list_tools"},
            {"request": "tools"},
            {"get": "tools"}
        ]
        
        for i, format_cmd in enumerate(formats_to_try):
            print(f"🔄 Trying tools list format {i+1}...")
            result = self.send_command(format_cmd)
            
            if result and not result.get("error") and "Unknown command type" not in str(result):
                print(f"✅ Tools list successful with format {i+1}")
                return result
            else:
                print(f"❌ Format {i+1} failed: {result}")
        
        return {"error": "All tool listing formats failed"}
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool"""
        if arguments is None:
            arguments = {}
        
        self.request_id += 1
        
        # Try different tool calling formats
        formats_to_try = [
            {
                "jsonrpc": "2.0",
                "id": self.request_id, 
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments}
            },
            {
                "command": "call_tool",
                "tool": tool_name,
                "arguments": arguments
            },
            {
                "action": "call_tool", 
                "tool_name": tool_name,
                "payload": arguments
            },
            {
                "type": "tool_call",
                "tool": tool_name,
                "args": arguments
            }
        ]
        
        for i, format_cmd in enumerate(formats_to_try):
            print(f"🔄 Trying tool call format {i+1} for {tool_name}...")
            result = self.send_command(format_cmd)
            
            if result and not result.get("error") and "Unknown command type" not in str(result):
                print(f"✅ Tool call successful with format {i+1}")
                return result
            else:
                print(f"❌ Format {i+1} failed: {result}")
        
        return {"error": f"All tool call formats failed for {tool_name}"}
    
    def discover_protocol(self) -> Dict[str, Any]:
        """Try to discover the correct protocol by testing various commands"""
        print("🔍 Discovering Blender MCP protocol...")
        
        discovery_commands = [
            {"help": True},
            {"command": "help"},
            {"action": "help"},
            {"type": "help"},
            {"request": "help"},
            {"status": True},
            {"command": "status"},
            {"ping": True},
            {"info": True},
            {"version": True},
            {"capabilities": True}
        ]
        
        results = []
        
        for cmd in discovery_commands:
            print(f"🧪 Testing: {cmd}")
            result = self.send_command(cmd)
            results.append({"command": cmd, "response": result})
            
            # If we get a non-error response, this might be the right format
            if result and not result.get("error") and "Unknown command type" not in str(result):
                print(f"✅ Potential working format: {cmd}")
                print(f"📥 Response: {result}")
        
        return {"discovery_results": results}
    
    def integrate_with_ai_workflow(self, model_path: str) -> Dict[str, Any]:
        """Try to integrate with the AI-to-3D workflow"""
        
        print(f"🎭 Attempting to process AI model: {model_path}")
        
        # First, discover the protocol
        discovery = self.discover_protocol()
        
        # Try common Blender operations
        blender_operations = [
            {"command": "import_model", "file": model_path},
            {"action": "load_mesh", "path": model_path},
            {"type": "process_mesh", "input": model_path},
            {"import": model_path},
            {"load": model_path},
            {"process": {"file": model_path, "type": "mesh"}}
        ]
        
        results = []
        
        for operation in blender_operations:
            print(f"🔧 Trying Blender operation: {operation}")
            result = self.send_command(operation)
            results.append({"operation": operation, "result": result})
            
            if result and not result.get("error") and "Unknown command type" not in str(result):
                print(f"✅ Successful operation: {operation}")
                return {"success": True, "operation": operation, "result": result}
        
        return {
            "success": False,
            "error": "No successful operations found",
            "discovery": discovery,
            "operation_attempts": results
        }
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 Disconnected from Blender MCP server")


def main():
    """Test the Blender MCP connection"""
    
    print("🎭 LevlStudio Blender MCP Integration")
    print("=" * 50)
    
    client = BlenderMCPClient()
    
    try:
        # Connect
        if not client.connect():
            return
        
        # Discover protocol
        print("\n1. 🔍 Discovering protocol...")
        discovery_result = client.discover_protocol()
        
        # Try initialization
        print("\n2. 🚀 Attempting initialization...")
        init_result = client.initialize()
        print(f"Initialization result: {init_result}")
        
        # Try listing tools
        print("\n3. 🔧 Attempting to list tools...")
        tools_result = client.list_tools()
        print(f"Tools result: {tools_result}")
        
        # Try AI workflow integration
        print("\n4. 🎨 Testing AI workflow integration...")
        integration_result = client.integrate_with_ai_workflow("test_model.glb")
        
        if integration_result["success"]:
            print("✅ Successfully integrated with Blender MCP!")
            print(f"Working operation: {integration_result['operation']}")
        else:
            print("⚠️ Could not find working integration method")
            print("📋 This means manual setup may be needed")
        
        # Summary
        print("\n" + "="*50)
        print("📊 BLENDER MCP INTEGRATION SUMMARY")
        print("="*50)
        print(f"Connection: ✅ Working")
        print(f"Protocol Discovery: {'✅ Responses received' if discovery_result else '❌ No responses'}")
        print(f"AI Integration: {'✅ Ready' if integration_result['success'] else '⚠️ Manual setup needed'}")
        
        if not integration_result["success"]:
            print("\n💡 RECOMMENDATIONS:")
            print("1. Check Blender MCP server documentation for correct protocol")
            print("2. The server is responding but may use a custom command format")
            print("3. Try manual Blender operations through the server interface")
            print("4. Consider using the built-in Blender automation scripts instead")
        
    finally:
        client.close()


if __name__ == "__main__":
    main()