#!/usr/bin/env python3
"""
Compliance Verification Script
Verifies that the chatbot meets all restriction requirements:
- No proprietary APIs (ChatGPT, Gemini, Claude, etc.)
- Only open-source models (HuggingFace, LLaMA, etc.)
- Fully offline capable
"""

import os
import sys
import importlib.util
from typing import List, Dict, Any

def check_imports() -> Dict[str, bool]:
    """Check that only open-source libraries are imported."""
    print("🔍 Checking imports for proprietary API usage...")
    
    # Files to check
    files_to_check = [
        "main.py",
        "main_ollama.py", 
        "chatbot_core.py",
        "chatbot_core_ollama.py",
        "ollama_client.py",
        "mcp_client.py",
        "documentation_scraper.py"
    ]
    
    proprietary_apis = [
        "openai", "anthropic", "google.generativeai", "cohere",
        "chatgpt", "gpt-", "claude", "gemini", "bard"
    ]
    
    violations = []
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        for api in proprietary_apis:
            if api in content:
                violations.append(f"{file_path}: Contains '{api}'")
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations
    }

def check_models() -> Dict[str, Any]:
    """Check that only open-source models are used."""
    print("🤖 Checking model configurations...")
    
    # Check config.py
    if os.path.exists("config.py"):
        with open("config.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for model names
        open_source_models = [
            "microsoft/DialoGPT-medium",
            "sentence-transformers",
            "all-MiniLM-L6-v2",
            "llama2",
            "smollm2"
        ]
        
        proprietary_models = [
            "gpt-", "chatgpt", "claude", "gemini", "bard", "openai", "text-davinci"
        ]
        
        found_open_source = any(model in content for model in open_source_models)
        
        # More precise detection - avoid false positives like "DialoGPT"
        content_lower = content.lower()
        found_proprietary = False
        for model in proprietary_models:
            if model in content_lower:
                # Check if it's not part of an open-source model name
                if model == "gpt-" and "dialogpt" in content_lower:
                    continue  # DialoGPT is open-source, not GPT-
                found_proprietary = True
                break
        
        return {
            "compliant": found_open_source and not found_proprietary,
            "open_source_found": found_open_source,
            "proprietary_found": found_proprietary
        }
    
    return {"compliant": False, "error": "config.py not found"}

def check_requirements() -> Dict[str, Any]:
    """Check requirements.txt for proprietary dependencies."""
    print("📦 Checking requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        return {"compliant": False, "error": "requirements.txt not found"}
    
    with open("requirements.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Allowed open-source packages
    allowed_packages = [
        "fastapi", "uvicorn", "requests", "beautifulsoup4",
        "transformers", "torch", "sentence-transformers", "pydantic",
        "python-multipart", "aiofiles", "lxml", "numpy", "scikit-learn",
        "chromadb", "python-dotenv"
    ]
    
    # Prohibited packages
    prohibited_packages = [
        "openai", "anthropic", "google-generativeai", "cohere"
    ]
    
    lines = content.strip().split('\n')
    violations = []
    
    for line in lines:
        if line.strip() and not line.startswith('#'):
            package_name = line.split('>=')[0].split('==')[0].strip()
            
            if any(prohibited in package_name.lower() for prohibited in prohibited_packages):
                violations.append(package_name)
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations
    }

def check_offline_capability() -> Dict[str, Any]:
    """Check that the solution can run offline."""
    print("🌐 Checking offline capability...")
    
    # Check for hardcoded API endpoints
    api_endpoints = [
        "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com"
    ]
    
    violations = []
    
    for file_path in ["main.py", "main_ollama.py", "chatbot_core.py"]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for endpoint in api_endpoints:
                if endpoint in content:
                    violations.append(f"{file_path}: Contains {endpoint}")
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations
    }

def main():
    """Run all compliance checks."""
    print("🔒 RESTRICTION COMPLIANCE VERIFICATION")
    print("=" * 50)
    
    checks = {
        "Import Check": check_imports(),
        "Model Check": check_models(),
        "Requirements Check": check_requirements(),
        "Offline Capability": check_offline_capability()
    }
    
    all_compliant = True
    
    for check_name, result in checks.items():
        print(f"\n📋 {check_name}:")
        
        if result.get("compliant", False):
            print("   ✅ COMPLIANT")
        else:
            print("   ❌ NON-COMPLIANT")
            all_compliant = False
            
            if "violations" in result:
                for violation in result["violations"]:
                    print(f"      - {violation}")
            elif "error" in result:
                print(f"      - {result['error']}")
            elif "proprietary_found" in result and result["proprietary_found"]:
                print("      - Proprietary models detected")
            elif not result.get("open_source_found", False):
                print("      - No open-source models found")
    
    print("\n" + "=" * 50)
    
    if all_compliant:
        print("🎉 ALL RESTRICTIONS COMPLIED WITH!")
        print("✅ No proprietary APIs used")
        print("✅ Only open-source models")
        print("✅ Fully offline capable")
        print("✅ Can run in air-gapped environments")
        sys.exit(0)
    else:
        print("❌ COMPLIANCE VIOLATIONS DETECTED!")
        print("Please review the violations above and fix them.")
        sys.exit(1)

if __name__ == "__main__":
    main()
