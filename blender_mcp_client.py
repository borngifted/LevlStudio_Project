#!/usr/bin/env python3
"""
Blender MCP Client
Connect to Blender MCP server on port 9876 and integrate with AI-to-3D workflow
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

class BlenderMCPClient:
    """Client for Blender MCP server integration"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9876):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Blender MCP server"""
        test_endpoints = [
            "/health",
            "/status", 
            "/",
            "/tools",
            "/list_tools",
            "/tools/list",
            "/mcp/tools",
            "/api/tools"
        ]
        
        results = {"connected": False, "endpoints_tested": []}
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                req = urllib.request.Request(url)
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    body = response.read().decode('utf-8')
                    
                    result = {
                        "endpoint": endpoint,
                        "status": status,
                        "content_type": content_type,
                        "body_preview": body[:200] if body else "Empty"
                    }
                    
                    if status == 200:
                        results["connected"] = True
                        results["working_endpoint"] = endpoint
                        try:
                            if 'application/json' in content_type:
                                result["parsed_body"] = json.loads(body)
                        except:
                            pass
                    
                    results["endpoints_tested"].append(result)
                    
            except urllib.error.HTTPError as e:
                results["endpoints_tested"].append({
                    "endpoint": endpoint,
                    "error": f"HTTP {e.code}: {e.reason}"
                })
            except Exception as e:
                results["endpoints_tested"].append({
                    "endpoint": endpoint, 
                    "error": str(e)
                })
        
        return results
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from Blender MCP server"""
        endpoints_to_try = [
            "/tools",
            "/list_tools", 
            "/tools/list",
            "/mcp/list_tools",
            "/api/tools"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}{endpoint}"
                req = urllib.request.Request(url)
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        body = response.read().decode('utf-8')
                        try:
                            return {"success": True, "tools": json.loads(body), "endpoint": endpoint}
                        except json.JSONDecodeError:
                            return {"success": False, "error": "Invalid JSON response", "raw": body}
                            
            except Exception as e:
                continue
        
        return {"success": False, "error": "No working tools endpoint found"}
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool on the Blender MCP server"""
        if arguments is None:
            arguments = {}
        
        endpoints_to_try = [
            f"/tools/{tool_name}",
            f"/tool/{tool_name}",
            f"/call/{tool_name}",
            f"/tools/call/{tool_name}",
            "/tools/call",
            "/call_tool"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}{endpoint}"
                
                # Prepare payload
                if endpoint in ["/tools/call", "/call_tool"]:
                    payload = {
                        "tool": tool_name,
                        "arguments": arguments
                    }
                else:
                    payload = arguments
                
                data = json.dumps(payload).encode('utf-8')
                
                req = urllib.request.Request(url, data=data)
                req.add_header('Content-Type', 'application/json')
                req.add_header('Accept', 'application/json')
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    if response.status == 200:
                        body = response.read().decode('utf-8')
                        try:
                            return {"success": True, "result": json.loads(body), "endpoint": endpoint}
                        except json.JSONDecodeError:
                            return {"success": True, "result": body, "endpoint": endpoint}
                            
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                if e.code != 404:  # Don't report 404s, those are expected
                    return {"success": False, "error": f"HTTP {e.code}: {error_body}", "endpoint": endpoint}
            except Exception as e:
                continue
        
        return {"success": False, "error": f"Tool {tool_name} not found or callable"}
    
    def integrate_with_ai_workflow(self, model_path: str, asset_name: str) -> Dict[str, Any]:
        """
        Integrate Blender MCP server with AI-to-3D workflow
        Process AI-generated 3D models through Blender
        """
        
        workflow_steps = []
        
        # Step 1: Test connection
        connection_test = self.test_connection()
        workflow_steps.append({"step": "connection_test", "result": connection_test})
        
        if not connection_test["connected"]:
            return {"success": False, "error": "Cannot connect to Blender MCP server", "steps": workflow_steps}
        
        # Step 2: List available tools
        tools_list = self.list_tools()
        workflow_steps.append({"step": "list_tools", "result": tools_list})
        
        if not tools_list["success"]:
            return {"success": False, "error": "Cannot list Blender tools", "steps": workflow_steps}
        
        # Step 3: Try to process the model
        common_blender_tools = [
            "import_model",
            "import_mesh", 
            "load_model",
            "process_mesh",
            "cleanup_mesh",
            "export_model",
            "export_fbx",
            "ai_to_ue_process"
        ]
        
        available_tools = tools_list.get("tools", {})
        print(f"🔍 Available Blender tools: {list(available_tools.keys()) if isinstance(available_tools, dict) else available_tools}")
        
        # Try processing with available tools
        processing_results = []
        
        for tool_name in common_blender_tools:
            if isinstance(available_tools, dict) and tool_name in available_tools:
                print(f"🔧 Trying to use tool: {tool_name}")
                
                # Call the tool with model processing arguments
                tool_args = {
                    "input_file": model_path,
                    "asset_name": asset_name,
                    "output_dir": "ai_generated_assets/ue_ready",
                    "cleanup": True,
                    "optimize_for_ue": True
                }
                
                result = self.call_tool(tool_name, tool_args)
                processing_results.append({"tool": tool_name, "result": result})
                
                if result["success"]:
                    workflow_steps.append({"step": f"process_with_{tool_name}", "result": result})
                    return {"success": True, "processed_by": tool_name, "result": result, "steps": workflow_steps}
        
        workflow_steps.append({"step": "tool_processing_attempts", "result": processing_results})
        
        return {
            "success": False, 
            "error": "No suitable processing tools found",
            "available_tools": available_tools,
            "steps": workflow_steps
        }


def main():
    """Test Blender MCP integration"""
    
    print("🎭 Connecting to Blender MCP Server on port 9876...")
    print("=" * 60)
    
    client = BlenderMCPClient(port=9876)
    
    # Test connection
    print("1. Testing connection...")
    connection_result = client.test_connection()
    
    if connection_result["connected"]:
        print("✅ Connected to Blender MCP server!")
        print(f"🔗 Working endpoint: {connection_result.get('working_endpoint', 'Unknown')}")
    else:
        print("❌ Could not connect to Blender MCP server")
        print("📋 Endpoints tested:")
        for test in connection_result["endpoints_tested"]:
            status = test.get("status", "Error")
            error = test.get("error", "")
            print(f"   {test['endpoint']}: {status} {error}")
        return
    
    # List tools
    print("\n2. Listing available tools...")
    tools_result = client.list_tools()
    
    if tools_result["success"]:
        tools = tools_result["tools"]
        print(f"✅ Found tools via endpoint: {tools_result['endpoint']}")
        
        if isinstance(tools, dict):
            print(f"📋 Available tools ({len(tools)}):")
            for tool_name, tool_info in tools.items():
                description = tool_info.get("description", "No description") if isinstance(tool_info, dict) else "Tool available"
                print(f"   🔧 {tool_name}: {description}")
        elif isinstance(tools, list):
            print(f"📋 Available tools ({len(tools)}):")
            for tool in tools:
                if isinstance(tool, dict):
                    name = tool.get("name", tool.get("id", "Unknown"))
                    desc = tool.get("description", "No description")
                    print(f"   🔧 {name}: {desc}")
                else:
                    print(f"   🔧 {tool}")
        else:
            print(f"📋 Tools response: {tools}")
    else:
        print(f"❌ Could not list tools: {tools_result['error']}")
        return
    
    # Test integration with example model
    print("\n3. Testing AI-to-3D workflow integration...")
    
    # Use an example model path (this would be from our AI pipeline)
    test_model = "ai_generated_assets/3d_models/delivery_van.glb"
    integration_result = client.integrate_with_ai_workflow(test_model, "delivery_van")
    
    if integration_result["success"]:
        print(f"✅ Successfully processed model with: {integration_result['processed_by']}")
        print(f"📁 Result: {integration_result['result']}")
    else:
        print(f"⚠️  Integration test: {integration_result['error']}")
        if "available_tools" in integration_result:
            print(f"🔧 Available tools for manual integration: {integration_result['available_tools']}")
    
    print("\n🎯 Blender MCP Integration Summary:")
    print(f"   Connection: {'✅ Working' if connection_result['connected'] else '❌ Failed'}")
    print(f"   Tools: {'✅ Available' if tools_result['success'] else '❌ Not accessible'}")
    print(f"   AI Integration: {'✅ Ready' if integration_result['success'] else '⚠️ Manual setup needed'}")
    
    return {
        "connection": connection_result,
        "tools": tools_result,
        "integration": integration_result
    }


if __name__ == "__main__":
    main()