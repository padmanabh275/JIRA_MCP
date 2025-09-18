# Creating Epics and Sprints with the Chatbot

This guide explains how to use the Jira Customer Support Chatbot to create epics and sprints through natural language queries.

## 🎯 **Prerequisites**

### **1. Jira Credentials Configured**
Make sure your `.env` file has valid Jira credentials:

```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### **2. Proper Permissions**
Ensure your Jira account has:
- **Create Issues** permission in the target project
- **Manage Sprints** permission for sprint creation
- **Admin** or **Project Lead** role (recommended)

### **3. Valid Project and Board IDs**
You need to know:
- **Project Key**: e.g., `PROJ`, `DEMO`, `TEST`
- **Board ID**: Numeric ID of your Agile board

## 🏗️ **Creating Epics**

### **Method 1: Natural Language Query**

**Examples:**
```
"Create epic in PROJECT-123 with title My New Epic"
"Create epic in DEMO project named User Authentication Feature"
"Create epic in TEST with summary Database Migration Epic"
```

**Format Pattern:**
```
Create epic in [PROJECT_KEY] with title [EPIC_NAME]
```

### **Method 2: Structured Query**

**Examples:**
```
"Create epic project PROJECT-123 title My Epic"
"Create epic project DEMO summary User Stories Epic"
"Create epic project TEST name Sprint Planning Epic"
```

### **Required Parameters:**
- **Project Key**: The Jira project key (e.g., `PROJ`, `DEMO`)
- **Epic Title/Summary**: Descriptive name for the epic

### **Example Queries:**
```
✅ "Create epic in PROJ with title User Authentication"
✅ "Create epic in DEMO project named Mobile App Development"
✅ "Create epic in TEST with summary API Integration Epic"
✅ "Create epic project PROJ title Data Migration Epic"
```

## 🏃 **Creating Sprints**

### **Method 1: Natural Language Query**

**Examples:**
```
"Create sprint in board 123 named Sprint 1"
"Create sprint in board 456 with name Q1 Planning Sprint"
"Create sprint in board 789 named Bug Fix Sprint"
```

**Format Pattern:**
```
Create sprint in board [BOARD_ID] named [SPRINT_NAME]
```

### **Method 2: Structured Query**

**Examples:**
```
"Create sprint board 123 name Sprint 1"
"Create sprint board 456 title Q1 Planning"
"Create sprint board 789 sprint Bug Fix Sprint"
```

### **Required Parameters:**
- **Board ID**: Numeric ID of your Agile board
- **Sprint Name**: Descriptive name for the sprint

### **Example Queries:**
```
✅ "Create sprint in board 123 named Sprint 1"
✅ "Create sprint in board 456 with name Q1 Planning Sprint"
✅ "Create sprint board 789 title Bug Fix Sprint"
✅ "Create sprint in board 101 named User Stories Sprint"
```

## 🔍 **Finding Project Keys and Board IDs**

### **Finding Project Keys:**
1. Go to your Jira instance
2. Navigate to **Projects** → **View all projects**
3. Look for the **Key** column (e.g., `PROJ`, `DEMO`, `TEST`)

### **Finding Board IDs:**
1. Go to **Boards** → **View all boards**
2. Click on your board
3. Look at the URL: `.../secure/RapidBoard.jspa?rapidView=[BOARD_ID]`
4. The number after `rapidView=` is your Board ID

## 🧪 **Testing Epic and Sprint Creation**

### **Test Epic Creation:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create epic in PROJ with title Test Epic"}'
```

### **Test Sprint Creation:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create sprint in board 123 named Test Sprint"}'
```

## ❌ **Common Issues and Solutions**

### **Issue 1: "Project key required"**
**Problem:** No project key found in query
**Solution:** Include project key in your query
```
❌ "Create epic with title My Epic"
✅ "Create epic in PROJ with title My Epic"
```

### **Issue 2: "Epic summary required"**
**Problem:** No epic title/summary found
**Solution:** Include epic name in your query
```
❌ "Create epic in PROJ"
✅ "Create epic in PROJ with title My Epic"
```

### **Issue 3: "Board ID required"**
**Problem:** No board ID found in query
**Solution:** Include board ID in your query
```
❌ "Create sprint named My Sprint"
✅ "Create sprint in board 123 named My Sprint"
```

### **Issue 4: "Sprint name required"**
**Problem:** No sprint name found
**Solution:** Include sprint name in your query
```
❌ "Create sprint in board 123"
✅ "Create sprint in board 123 named My Sprint"
```

### **Issue 5: Authentication Errors**
**Problem:** Invalid Jira credentials
**Solution:** Check your `.env` file
```bash
# Verify these are correct:
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### **Issue 6: Permission Errors**
**Problem:** Insufficient permissions
**Solution:** 
1. Check your Jira permissions
2. Ensure you have "Create Issues" permission
3. Contact your Jira admin

## 🎯 **Best Practices**

### **1. Use Clear, Descriptive Names**
```
✅ "Create epic in PROJ with title User Authentication System"
❌ "Create epic in PROJ with title Epic 1"
```

### **2. Include Project Context**
```
✅ "Create epic in PROJ with title Mobile App Development"
❌ "Create epic with title Mobile App Development"
```

### **3. Use Consistent Naming**
```
✅ "Create sprint in board 123 named Sprint 1"
✅ "Create sprint in board 123 named Sprint 2"
```

### **4. Test with Simple Queries First**
```
1. "Create epic in PROJ with title Test Epic"
2. "Create sprint in board 123 named Test Sprint"
3. Then try more complex queries
```

## 🔄 **Workflow Examples**

### **Complete Epic Creation Workflow:**
1. **Identify Project:** Find your project key (e.g., `PROJ`)
2. **Define Epic:** Come up with a clear epic name
3. **Query Chatbot:** "Create epic in PROJ with title [Your Epic Name]"
4. **Verify Creation:** Check your Jira project for the new epic

### **Complete Sprint Creation Workflow:**
1. **Identify Board:** Find your board ID (e.g., `123`)
2. **Define Sprint:** Come up with a clear sprint name
3. **Query Chatbot:** "Create sprint in board 123 named [Your Sprint Name]"
4. **Verify Creation:** Check your Jira board for the new sprint

## 🎉 **Success Indicators**

You'll know creation was successful when:

### **Epic Creation:**
- ✅ Chatbot responds with "Successfully created epic in project [PROJECT_KEY]"
- ✅ Epic appears in your Jira project
- ✅ Epic has the correct title and project

### **Sprint Creation:**
- ✅ Chatbot responds with "Successfully created sprint '[SPRINT_NAME]' in board [BOARD_ID]"
- ✅ Sprint appears in your Jira board
- ✅ Sprint has the correct name and board

## 🚀 **Advanced Usage**

### **Batch Creation:**
You can create multiple epics/sprints by sending multiple queries:

```bash
# Create multiple epics
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create epic in PROJ with title Epic 1"}'

curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create epic in PROJ with title Epic 2"}'
```

### **Integration with CI/CD:**
You can integrate epic/sprint creation into your development workflow:

```bash
# Create epic for new feature
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create epic in PROJ with title Feature: User Authentication"}'
```

Now you can create epics and sprints through natural language queries! 🎊
