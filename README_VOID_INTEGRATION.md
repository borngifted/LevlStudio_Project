# 🚀 Void Editor Integration with LevlStudio Pipeline

This guide shows how to use [Void Editor](https://voideditor.com/) - an open-source AI code editor - to orchestrate your entire UE5 → ComfyUI pipeline with natural language commands.

## 🎯 What is Void Editor?

**Void Editor** is a VS Code-style AI IDE that lets you:
- 🤖 **Chat with AI agents** that can run commands and edit code
- 🔧 **Multi-provider support**: OpenAI, Claude, Gemini, or local models (Ollama)
- 🛡️ **Privacy-focused**: Keep sensitive data local while accessing cloud models
- 🎛️ **Command orchestration**: Chain complex workflows with natural language

Perfect for creative pipelines like ours where you want to say: *"Render Nimble with magical glow style at 1080p"* and have the AI execute the entire workflow.

## 📥 Installation & Setup

### 1. Install Void Editor
1. **Download**: Go to [voideditor.com](https://voideditor.com/) and download the beta for macOS
2. **Install**: Drag to Applications folder
3. **First Run**: Open Void Editor

### 2. Configure AI Providers
1. **Open Settings**: `Cmd+,` or `Void → Preferences`
2. **Add Providers**: Go to `AI Providers` section
3. **Choose Your Setup**:

#### Option A: Cloud Models (Recommended)
```json
{
  "openai": {
    "apiKey": "your-openai-key",
    "model": "gpt-4"
  },
  "anthropic": {
    "apiKey": "your-claude-key", 
    "model": "claude-3-sonnet"
  }
}
```

#### Option B: Local Models (Privacy-First)
```bash
# Install Ollama first
brew install ollama

# Pull a model
ollama pull llama2
ollama pull codellama
```

Then in Void settings:
```json
{
  "ollama": {
    "endpoint": "http://localhost:11434",
    "model": "llama2"
  }
}
```

### 3. Open Your Project
1. **File → Open Folder**
2. **Navigate to**: `/Volumes/Jul_23_2025/LevlStudio_Project`
3. **Open**: The project will load with all Void configurations

## 🎬 Using Void with LevlStudio

### Quick Start Commands

Once you open the project in Void, you can use these natural language commands in the AI chat:

#### 🚀 **Start the Pipeline**
```
"Start the MCP server and check system status"
```
*→ Runs `mcp:start` and `mcp:status` commands*

#### 🎭 **Render a Character**
```
"Render Nimble character with festive night style at 720p"
```
*→ Executes one-click pipeline with proper parameters*

#### 🎨 **Style an Existing Video**
```
"Apply magical glow style to the video in exports/test.mp4"
```
*→ Runs direct ComfyUI workflow*

#### 👥 **Batch Processing**
```
"Render all characters with ice crystal style"
```
*→ Executes batch rendering command*

### Available Commands in Void

| Command | Description | Use Case |
|---------|-------------|----------|
| `🚀 Start LevlStudio MCP Server` | Start pipeline server | Setup |
| `📊 Check Pipeline Status` | System health check | Troubleshooting |
| `🎭 UE → ComfyUI One-Click Pipeline` | Full end-to-end render | Main workflow |
| `🎬 Run ComfyUI Workflow (Direct)` | Style existing video | Quick styling |
| `👥 Batch Render All Characters` | Process multiple assets | Production |
| `🧹 Clean Pipeline Queue` | Clear temp files | Maintenance |

### Example Conversations

#### **Simple Render**
**You**: *"I want to test render Nimble in the empty level"*

**Void AI**: *"I'll run a test render of Nimble in the empty level. Let me start with a quick 720p render using the festive night style."*

*→ Executes: `ue:oneclick` with default parameters*

**Void AI**: *"✅ Command queued! The pipeline will:*
1. *🎭 Spawn BP_Nimble in UE5*
2. *🎬 Create 4-second sequence with camera*
3. *📹 Render at 1280x720, 24fps*
4. *🎨 Apply festive night style in ComfyUI*
5. *📁 Output to: outputs/*

*Remember to click 'Levl Bridge: Run Once' in Unreal Engine!"*

#### **Style Experimentation**
**You**: *"Try the same character with different styles - magical glow and ice crystal"*

**Void AI**: *"I'll render Nimble with both magical glow and ice crystal styles. This will create two versions for comparison."*

*→ Executes multiple `ue:oneclick` commands with different style parameters*

#### **Batch Production**
**You**: *"I need all characters rendered with the candy cane style for the holiday scene"*

**Void AI**: *"Perfect! I'll batch render all available characters (Nimble, Pip, Jingles, Santa, Jax) with the candy cane style. This will take about 15-20 minutes total."*

*→ Executes: `batch:characters` command*

## 🎛️ Advanced Void Features

### 1. **Context Awareness**
Void automatically knows about your:
- 📁 Project structure and files
- 🎨 Available styles and characters  
- ⚙️ Current system status
- 📊 Recent renders and outputs

### 2. **Smart Suggestions**
The AI will suggest optimizations:
- *"For faster iteration, try 720p resolution first"*
- *"Ice crystal style works great with outdoor scenes"*
- *"Your last render is ready - want to view it?"*

### 3. **File Watching**
Void monitors your pipeline and notifies when:
- 🎬 New renders appear in `exports/`
- 🎨 Styled videos complete in `outputs/`
- ⚠️ Errors occur in the bridge

### 4. **Preset Management**
Quick access to common combinations:
```
"Use the nimble-magical preset at HD resolution"
```
*→ Character: BP_Nimble, Style: magical_glow, Resolution: 1920x1080*

## 🔧 Customization

### Adding New Commands
Edit `.void/commands.json` to add custom workflows:

```json
{
  "id": "custom:turntable",
  "label": "🔄 Character Turntable Render", 
  "description": "360° turntable render with multiple styles",
  "shell": "python3 custom_turntable_script.py",
  "cwd": "${workspaceRoot}"
}
```

### Modify AI Behavior
Update `.void/rules.md` to change how the AI agent behaves:

```markdown
## Custom Rules
- Always use 1080p for final renders
- Prefer magical_glow style for hero characters
- Batch process overnight for large jobs
```

## 🚨 Troubleshooting

### **Void Can't Find Commands**
- ✅ Ensure `.void/commands.json` exists in project root
- ✅ Check command syntax is valid JSON
- ✅ Restart Void Editor

### **AI Doesn't Understand Pipeline**
- ✅ Check `.void/rules.md` is loaded
- ✅ Verify AI provider is connected
- ✅ Try: *"Read the pipeline rules and explain the workflow"*

### **Commands Fail to Execute**
- ✅ Check MCP server is running: `mcp:status`
- ✅ Verify ComfyUI is accessible
- ✅ Test individual commands first

## 🎯 Best Practices

### **For Daily Use**
1. **Start session**: *"Check system status and start services"*
2. **Test quickly**: Use 720p resolution for iterations
3. **Batch overnight**: Queue multiple renders for long jobs
4. **Monitor outputs**: Void will notify when renders complete

### **For Production**
1. **Use presets**: Consistent quality with named configurations
2. **Version outputs**: Include timestamps or iteration numbers
3. **Backup settings**: Save custom commands and rules

### **For Collaboration**
1. **Share presets**: Export `.void/` folder for team consistency
2. **Document workflows**: Update rules.md with team conventions
3. **Version control**: Include Void configs in git

## 🎉 What You Can Say to Void

Here are example natural language commands that work with your pipeline:

- *"Start everything and render a quick test"*
- *"Show me all available character and style combinations"*
- *"Render the last character again but with ice crystal style"*
- *"What's the status of my renders?"*
- *"Clean up the pipeline and start fresh"*
- *"Batch render all characters for the holiday scene"*
- *"Apply dark forest style to that video in exports"*
- *"Set up a 1080p render of Santa with festive style"*
- *"Open the outputs folder to see results"*

---

**🚀 Ready to go!** Open Void Editor, load your project, and start creating AI-styled renders with natural language commands!