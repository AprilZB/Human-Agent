with open(r'C:\Users\Administrator\.gemini\antigravity\project-memory\README.md', 'r', encoding='utf-8') as f:
    content = f.read()

rule_text = '''
## Global Rules & Constraints (For AI Agents)

> **CRITICAL - SERVER ENVIRONMENT RULE:**
> This machine (10.11.100.151) is a **Shared Development Environment**. There are many background services and microservices running simultaneously (e.g., Node.js, Python, PM2, Docker). 
> **DO NOT USE commands like Stop-Process, 	askkill, or any other port-killing scripts indiscriminately without EXPLICIT permission from the user.** If you encounter a "Port in use" error, do NOT auto-kill the process. Inform the user and ask for instructions before terminating any service.

'''

if 'Global Rules' not in content:
    content = content.replace("## How to Use Project Memory", rule_text + "## How to Use Project Memory")
    with open(r'C:\Users\Administrator\.gemini\antigravity\project-memory\README.md', 'w', encoding='utf-8') as f:
        f.write(content)
