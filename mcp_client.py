"""Model Context Protocol (MCP) client for Jira APIs."""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import config

@dataclass
class MCPRequest:
    """MCP request structure."""
    method: str
    url: str
    headers: Dict[str, str]
    data: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse:
    """MCP response structure."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class JiraMCPClient:
    """MCP client for Jira Epic and Sprint APIs."""
    
    def __init__(self):
        self.base_url = config.JIRA_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication if available
        if config.JIRA_API_TOKEN and config.JIRA_EMAIL:
            self.headers["Authorization"] = f"Basic {self._encode_auth()}"
    
    def _encode_auth(self) -> str:
        """Encode authentication credentials."""
        import base64
        credentials = f"{config.JIRA_EMAIL}:{config.JIRA_API_TOKEN}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _make_request(self, request: MCPRequest) -> MCPResponse:
        """Make an MCP request to Jira API."""
        try:
            response = requests.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                json=request.data,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202, 204]:
                return MCPResponse(
                    success=True,
                    data=response.json() if response.content else {}
                )
            else:
                return MCPResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                error=f"Request failed: {str(e)}"
            )
    
    # Epic API Methods
    def get_epics(self, project_key: Optional[str] = None) -> MCPResponse:
        """Get all epics or epics for a specific project."""
        url = f"{self.base_url}/rest/api/3/search"
        
        jql = "issuetype = Epic"
        if project_key:
            jql += f" AND project = {project_key}"
        
        request = MCPRequest(
            method="POST",
            url=url,
            headers=self.headers,
            data={
                "jql": jql,
                "fields": ["summary", "description", "status", "assignee", "created", "updated"],
                "maxResults": 100
            }
        )
        
        return self._make_request(request)
    
    def get_epic(self, epic_key: str) -> MCPResponse:
        """Get a specific epic by key."""
        url = f"{self.base_url}/rest/api/3/issue/{epic_key}"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers
        )
        
        return self._make_request(request)
    
    def create_epic(self, project_key: str, summary: str, description: str = "") -> MCPResponse:
        """Create a new epic."""
        url = f"{self.base_url}/rest/api/3/issue"
        
        # Convert description to Atlassian Document Format if provided
        adf_description = None
        if description:
            adf_description = {
                "version": 1,
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
        
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": "Epic"}
        }
        
        if adf_description:
            fields["description"] = adf_description
        
        request = MCPRequest(
            method="POST",
            url=url,
            headers=self.headers,
            data={"fields": fields}
        )
        
        return self._make_request(request)
    
    def update_epic(self, epic_key: str, updates: Dict[str, Any]) -> MCPResponse:
        """Update an epic."""
        url = f"{self.base_url}/rest/api/3/issue/{epic_key}"
        
        request = MCPRequest(
            method="PUT",
            url=url,
            headers=self.headers,
            data={"fields": updates}
        )
        
        return self._make_request(request)
    
    # Board API Methods
    def get_boards(self) -> MCPResponse:
        """Get all boards."""
        url = f"{self.base_url}/rest/agile/1.0/board"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers
        )
        
        return self._make_request(request)
    
    def get_board(self, board_id: int) -> MCPResponse:
        """Get a specific board."""
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers
        )
        
        return self._make_request(request)
    
    # Sprint API Methods
    def get_sprints(self, board_id: Optional[int] = None) -> MCPResponse:
        """Get all sprints or sprints for a specific board."""
        if board_id:
            url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
        else:
            url = f"{self.base_url}/rest/agile/1.0/sprint"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers
        )
        
        return self._make_request(request)
    
    def get_sprint(self, sprint_id: int) -> MCPResponse:
        """Get a specific sprint by ID."""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers
        )
        
        return self._make_request(request)
    
    def create_sprint(self, name: str, board_id: int, start_date: str = None, end_date: str = None) -> MCPResponse:
        """Create a new sprint."""
        url = f"{self.base_url}/rest/agile/1.0/sprint"
        
        data = {
            "name": name,
            "originBoardId": board_id
        }
        
        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date
        
        request = MCPRequest(
            method="POST",
            url=url,
            headers=self.headers,
            data=data
        )
        
        return self._make_request(request)
    
    def update_sprint(self, sprint_id: int, updates: Dict[str, Any]) -> MCPResponse:
        """Update a sprint."""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}"
        
        request = MCPRequest(
            method="PUT",
            url=url,
            headers=self.headers,
            data=updates
        )
        
        return self._make_request(request)
    
    def get_sprint_issues(self, sprint_id: int) -> MCPResponse:
        """Get all issues in a sprint."""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        
        request = MCPRequest(
            method="GET",
            url=url,
            headers=self.headers,
            data={
                "fields": ["summary", "description", "status", "assignee", "issuetype"],
                "maxResults": 1000
            }
        )
        
        return self._make_request(request)

class MCPManager:
    """Manager class for handling MCP operations."""
    
    def __init__(self):
        self.client = JiraMCPClient()
    
    def handle_epic_query(self, query: str) -> Dict[str, Any]:
        """Handle epic-related queries."""
        query_lower = query.lower()
        
        if "list" in query_lower or "show" in query_lower or "get all" in query_lower:
            return self._handle_list_epics(query)
        elif "create" in query_lower or "add" in query_lower or "new" in query_lower:
            return self._handle_create_epic(query)
        elif "update" in query_lower or "modify" in query_lower or "change" in query_lower:
            return self._handle_update_epic(query)
        else:
            return self._handle_get_epic(query)
    
    def handle_sprint_query(self, query: str) -> Dict[str, Any]:
        """Handle sprint-related queries."""
        query_lower = query.lower()
        
        if "list" in query_lower or "show" in query_lower or "get all" in query_lower:
            return self._handle_list_sprints(query)
        elif "create" in query_lower or "add" in query_lower or "new" in query_lower:
            return self._handle_create_sprint(query)
        elif "update" in query_lower or "modify" in query_lower or "change" in query_lower:
            return self._handle_update_sprint(query)
        else:
            return self._handle_get_sprint(query)
    
    def handle_board_query(self, query: str) -> Dict[str, Any]:
        """Handle board-related queries."""
        query_lower = query.lower()
        
        if "list" in query_lower or "show" in query_lower or "get all" in query_lower:
            return self._handle_list_boards(query)
        else:
            return self._handle_get_board(query)
    
    def _handle_list_epics(self, query: str) -> Dict[str, Any]:
        """Handle listing epics."""
        response = self.client.get_epics()
        
        if response.success and response.data:
            epics = response.data.get("issues", [])
            return {
                "source": "mcp",
                "type": "epic_list",
                "data": epics,
                "message": f"Found {len(epics)} epics"
            }
        else:
            return {
                "source": "mcp_error",
                "error": response.error,
                "message": "Failed to retrieve epics"
            }
    
    def _handle_get_epic(self, query: str) -> Dict[str, Any]:
        """Handle getting a specific epic."""
        # Extract epic key from query (simplified)
        words = query.split()
        epic_key = None
        
        for word in words:
            if word.upper().startswith("EPIC-") or word.upper().startswith("PROJ-"):
                epic_key = word.upper()
                break
        
        if not epic_key:
            return {
                "source": "mcp_error",
                "error": "No epic key found in query",
                "message": "Please specify an epic key (e.g., EPIC-123)"
            }
        
        response = self.client.get_epic(epic_key)
        
        if response.success:
            return {
                "source": "mcp",
                "type": "epic_detail",
                "data": response.data,
                "message": f"Retrieved epic {epic_key}"
            }
        else:
            return {
                "source": "mcp_error",
                "error": response.error,
                "message": f"Failed to retrieve epic {epic_key}"
            }
    
    def _handle_create_epic(self, query: str) -> Dict[str, Any]:
        """Handle creating an epic."""
        # Extract parameters from query (simplified parsing)
        query_lower = query.lower()
        
        # Look for project key patterns
        project_key = None
        if "project" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "project" and i + 1 < len(words):
                    project_key = words[i + 1].upper()
                    break
        
        # Also look for "in [PROJECT]" pattern
        if not project_key and "in" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "in" and i + 1 < len(words):
                    potential_key = words[i + 1].upper()
                    # Check if it looks like a project key (letters and numbers)
                    if any(c.isalpha() for c in potential_key) and len(potential_key) <= 10:
                        project_key = potential_key
                        break
        
        # Look for summary/title
        summary = None
        if "title" in query_lower or "summary" in query_lower or "name" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["title", "summary", "name"] and i + 1 < len(words):
                    # Extract text after the keyword
                    summary = " ".join(words[i + 1:])
                    break
        
        # If no explicit parameters found, try to extract from context
        if not project_key and not summary:
            # Look for common patterns
            if "create epic" in query_lower:
                # Try to extract project and summary from the query
                parts = query.split("create epic")[1].strip().split()
                if len(parts) >= 2:
                    project_key = parts[0].upper()
                    summary = " ".join(parts[1:])
        
        # Validate required parameters
        if not project_key:
            return {
                "source": "mcp_error",
                "error": "Project key required",
                "message": "To create an epic, please specify a project key. Example: 'Create epic in PROJECT-123 with title My Epic'"
            }
        
        if not summary:
            return {
                "source": "mcp_error",
                "error": "Epic summary required",
                "message": "To create an epic, please provide a summary/title. Example: 'Create epic in PROJECT-123 with title My Epic'"
            }
        
        # Attempt to create the epic
        try:
            response = self.client.create_epic(project_key, summary, "")
            
            if response.success:
                return {
                    "source": "mcp",
                    "type": "epic_created",
                    "data": response.data,
                    "message": f"Successfully created epic in project {project_key}"
                }
            else:
                return {
                    "source": "mcp_error",
                    "error": response.error,
                    "message": f"Failed to create epic: {response.error}"
                }
        except Exception as e:
            return {
                "source": "mcp_error",
                "error": str(e),
                "message": f"Error creating epic: {str(e)}"
            }
    
    def _handle_update_epic(self, query: str) -> Dict[str, Any]:
        """Handle updating an epic."""
        return {
            "source": "mcp_error",
            "error": "Epic update requires additional parameters",
            "message": "To update an epic, please provide: epic key and fields to update"
        }
    
    def _handle_list_sprints(self, query: str) -> Dict[str, Any]:
        """Handle listing sprints."""
        response = self.client.get_sprints()
        
        if response.success and response.data:
            sprints = response.data.get("values", [])
            return {
                "source": "mcp",
                "type": "sprint_list",
                "data": sprints,
                "message": f"Found {len(sprints)} sprints"
            }
        else:
            return {
                "source": "mcp_error",
                "error": response.error,
                "message": "Failed to retrieve sprints"
            }
    
    def _handle_get_sprint(self, query: str) -> Dict[str, Any]:
        """Handle getting a specific sprint."""
        # Extract sprint ID from query (simplified)
        words = query.split()
        sprint_id = None
        
        for word in words:
            if word.isdigit():
                sprint_id = int(word)
                break
        
        if not sprint_id:
            return {
                "source": "mcp_error",
                "error": "No sprint ID found in query",
                "message": "Please specify a sprint ID"
            }
        
        response = self.client.get_sprint(sprint_id)
        
        if response.success:
            return {
                "source": "mcp",
                "type": "sprint_detail",
                "data": response.data,
                "message": f"Retrieved sprint {sprint_id}"
            }
        else:
            return {
                "source": "mcp_error",
                "error": response.error,
                "message": f"Failed to retrieve sprint {sprint_id}"
            }
    
    def _handle_create_sprint(self, query: str) -> Dict[str, Any]:
        """Handle creating a sprint."""
        # Extract parameters from query (simplified parsing)
        query_lower = query.lower()
        
        # Look for sprint name
        sprint_name = None
        if "named" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "named" and i + 1 < len(words):
                    # Extract text after "named" but stop before "in board"
                    remaining_words = words[i + 1:]
                    # Stop at "in board" if found
                    sprint_words = []
                    for j, w in enumerate(remaining_words):
                        if w.lower() == "in" and j + 1 < len(remaining_words) and remaining_words[j + 1].lower() == "board":
                            break
                        sprint_words.append(w)
                    sprint_name = " ".join(sprint_words)
                    break
        
        # Look for board ID
        board_id = None
        if "board" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "board" and i + 1 < len(words):
                    try:
                        board_id = int(words[i + 1])
                        break
                    except ValueError:
                        pass
        
        # Also look for "in board [ID]" pattern
        if not board_id and "in" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "in" and i + 1 < len(words) and words[i + 1].lower() == "board" and i + 2 < len(words):
                    try:
                        board_id = int(words[i + 2])
                        break
                    except ValueError:
                        pass
        
        # If no explicit parameters found, try to extract from context
        if not sprint_name and not board_id:
            if "create sprint" in query_lower:
                parts = query.split("create sprint")[1].strip().split()
                if len(parts) >= 2:
                    try:
                        board_id = int(parts[0])
                        sprint_name = " ".join(parts[1:])
                    except ValueError:
                        sprint_name = " ".join(parts)
        
        # Validate required parameters
        if not sprint_name:
            return {
                "source": "mcp_error",
                "error": "Sprint name required",
                "message": "To create a sprint, please provide a name. Example: 'Create sprint named Sprint 1'"
            }
        
        if not board_id:
            return {
                "source": "mcp_error",
                "error": "Board ID required",
                "message": "To create a sprint, please provide a board ID. Example: 'Create sprint in board 123 named Sprint 1'"
            }
        
        # Attempt to create the sprint
        try:
            response = self.client.create_sprint(sprint_name, board_id)
            
            if response.success:
                return {
                    "source": "mcp",
                    "type": "sprint_created",
                    "data": response.data,
                    "message": f"Successfully created sprint '{sprint_name}' in board {board_id}"
                }
            else:
                return {
                    "source": "mcp_error",
                    "error": response.error,
                    "message": f"Failed to create sprint: {response.error}"
                }
        except Exception as e:
            return {
                "source": "mcp_error",
                "error": str(e),
                "message": f"Error creating sprint: {str(e)}"
            }
    
    def _handle_update_sprint(self, query: str) -> Dict[str, Any]:
        """Handle updating a sprint."""
        return {
            "source": "mcp_error",
            "error": "Sprint update requires additional parameters",
            "message": "To update a sprint, please provide: sprint ID and fields to update"
        }
    
    def _handle_list_boards(self, query: str) -> Dict[str, Any]:
        """Handle listing boards."""
        try:
            response = self.client.get_boards()
            
            if response.success:
                boards_data = response.data.get("values", [])
                boards_info = []
                
                for board in boards_data:
                    board_info = {
                        "id": board.get("id"),
                        "name": board.get("name"),
                        "type": board.get("type"),
                        "location": board.get("location", {}).get("projectKey", "Unknown")
                    }
                    boards_info.append(board_info)
                
                return {
                    "source": "mcp",
                    "type": "boards_list",
                    "data": boards_info,
                    "message": f"Found {len(boards_info)} boards"
                }
            else:
                return {
                    "source": "mcp_error",
                    "error": response.error,
                    "message": f"Failed to retrieve boards: {response.error}"
                }
                
        except Exception as e:
            return {
                "source": "mcp_error",
                "error": str(e),
                "message": f"Error retrieving boards: {str(e)}"
            }
    
    def _handle_get_board(self, query: str) -> Dict[str, Any]:
        """Handle getting a specific board."""
        # Extract board ID from query
        query_lower = query.lower()
        board_id = None
        
        # Look for board ID patterns
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() == "board" and i + 1 < len(words):
                try:
                    board_id = int(words[i + 1])
                    break
                except ValueError:
                    continue
        
        if not board_id:
            return {
                "source": "mcp_error",
                "error": "Board ID required",
                "message": "To get board details, please specify a board ID. Example: 'Show board 123'"
            }
        
        try:
            response = self.client.get_board(board_id)
            
            if response.success:
                board_data = response.data
                return {
                    "source": "mcp",
                    "type": "board_details",
                    "data": board_data,
                    "message": f"Board details for board {board_id}"
                }
            else:
                return {
                    "source": "mcp_error",
                    "error": response.error,
                    "message": f"Failed to retrieve board {board_id}: {response.error}"
                }
                
        except Exception as e:
            return {
                "source": "mcp_error",
                "error": str(e),
                "message": f"Error retrieving board {board_id}: {str(e)}"
            }
