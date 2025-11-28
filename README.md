# CrewAI Multi-Agent System Debugger

An AI-powered debugging assistant for CrewAI multi-agent systems. Upload your CrewAI files, paste error logs, and get expert analysis with conversational follow-up support.

![CrewAI Debugger](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)

## 🌟 Features

### 📁 Comprehensive File Analysis
- **agents.yaml** - Validates role definitions, goals, and tool assignments
- **tasks.yaml** - Checks task descriptions, dependencies, and agent assignments
- **crew.py** - Verifies crew configuration and instantiation
- **main.py** - Validates execution flow and error handling
- **tools.py** - (Optional) Analyzes custom tool implementations

### 🐛 Error Log Analysis
- Paste runtime errors and stack traces
- Get root cause analysis
- Receive targeted fix recommendations
- Understand error propagation

### 💬 Conversational Debugging
- Ask follow-up questions about the analysis
- Request clarifications on specific issues
- Get step-by-step implementation guidance
- Iterative problem-solving support

### 📊 Expert Analysis Coverage
1. **Agents Validation** - Role clarity, goal alignment, LLM configuration
2. **Tasks Validation** - Description completeness, expected outputs, dependencies
3. **Tools Validation** - Error handling, return types, API key management
4. **Crew Configuration** - Process type validation, manager LLM setup
5. **Execution Flow** - Input handling, kickoff validation, output processing
6. **Cross-file Consistency** - Naming conventions, tool references, data flow

##  Quick Start

### Local Development

1. **Clone the repository**
```bash
   git clone <your-repo-url>
   cd crewai-debugger
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Set up environment variables**
   
   Create a `.streamlit/secrets.toml` file:
```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
```

4. **Run the application**
```bash
   streamlit run streamlit_app.py
```

5. **Open your browser**
   
   Navigate to `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Fork/Push this repository to GitHub**

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Create a new app**
   - Connect your GitHub repository
   - Set the main file path: `streamlit_app.py`
   - Choose Python 3.9+

4. **Add secrets**
   
   In the app settings, go to "Secrets" and add:
```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key-here"
```

5. **Deploy!** 🎉

## 📖 How to Use

### Step 1: Upload Files
- Upload required files: `agents.yaml`, `tasks.yaml`, `crew.py`, `main.py`
- Optionally upload `tools.py` if you have custom tools
- Paste any error logs you're experiencing

### Step 2: Start Debugging Session
- Click "Start Debugging Session"
- The AI will analyze your system and provide a comprehensive report

### Step 3: Interactive Chat
- Ask questions about the analysis
- Request clarification on specific issues
- Get help implementing recommended fixes
- Iterate until your issues are resolved

### Step 4: Export Results
- Download the entire conversation as a markdown file
- Share with your team or save for documentation

## 🎯 Example Use Cases

### Scenario 1: Runtime Error
```
Upload your files → Paste the error traceback → 
Get root cause analysis → Ask for step-by-step fix → 
Implement solution → Verify with AI
```

### Scenario 2: Configuration Issues
```
Upload your files → AI identifies misconfigurations → 
Ask about specific agents/tasks → Get code corrections → 
Request best practices → Optimize your setup
```

### Scenario 3: Performance Optimization
```
Upload working code → Ask "How can I improve this?" → 
Get optimization recommendations → Discuss trade-offs → 
Implement improvements
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **AI Engine**: Claude Sonnet 4 (Anthropic)
- **Language**: Python 3.9+
- **Deployment**: Streamlit Cloud

## 📋 File Structure
```
crewai-debugger/
│
├── streamlit_app.py          # Main application file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .streamlit/
│   └── config.toml           # Streamlit configuration
│   └── secrets.toml          # API keys (local only, not in repo)
└── .gitignore                # Git ignore file
```

## 🔒 Security & Privacy

- API keys are stored securely in Streamlit secrets
- Your code files are processed in-memory only
- No data is stored permanently
- Each session is isolated
- Export conversations for your records

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/crewai-debugger/issues) page
2. Create a new issue with detailed information
3. Contact the maintainer

## 🙏 Acknowledgments

- **CrewAI** - For the amazing multi-agent framework
- **Anthropic** - For Claude AI API
- **Streamlit** - For the excellent Python web framework

## 📊 Roadmap

- [ ] Support for more CrewAI file types
- [ ] Integration with GitHub for direct repo analysis
- [ ] Custom analysis templates
- [ ] Multi-language support
- [ ] Code diff visualization
- [ ] Automated fix suggestions with code generation

## 🔗 Links

- [CrewAI Documentation](https://docs.crewai.com/)
- [Anthropic Claude API](https://www.anthropic.com/api)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ for the CrewAI community**

*Debugging made intelligent, one conversation at a time.*
```

## Additional Files You Should Create:

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
*.log
