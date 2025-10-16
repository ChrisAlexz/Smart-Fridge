#!/usr/bin/env python3
"""Script to list available Gemini models for your API key."""
import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Run: pip install google-generativeai")
    sys.exit(1)

# Get API key from environment or use the hardcoded one
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBg834MqklKAAIsPsaks7vhk5W5GZtz_xo")

if not API_KEY:
    print("ERROR: No API key found. Set GEMINI_API_KEY environment variable.")
    sys.exit(1)

print(f"Using API Key: {API_KEY[:20]}...")
print("\n" + "=" * 70)

try:
    genai.configure(api_key=API_KEY)
    print("✓ API Key configured successfully\n")
except Exception as e:
    print(f"ERROR configuring API: {e}")
    sys.exit(1)

print("Available Gemini models that support generateContent:\n")
print("=" * 70)

found_models = []

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            found_models.append(model)
            print(f"\n✓ Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description[:80]}...")
            print("-" * 70)
    
    if not found_models:
        print("\n⚠ WARNING: No models found that support generateContent!")
        print("\nAll available models:")
        for model in genai.list_models():
            print(f"  - {model.name}: {model.supported_generation_methods}")
    
except Exception as e:
    print(f"\nERROR listing models: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if found_models:
    print(f"\nFound {len(found_models)} compatible model(s).\n")
    print("To use one of these models, update your .env file with:")
    print("\nGEMINI_MODEL=<model_name>\n")
    print("Where <model_name> is one of:")
    for model in found_models:
        print(f"  - {model.name}")
    
    print("\n\nRECOMMENDED .env configuration:")
    print("-" * 70)
    print(f"GEMINI_API_KEY={API_KEY}")
    print(f"GEMINI_MODEL={found_models[0].name}")
    print("-" * 70)
else:
    print("\n⚠ No compatible models found!")
    print("\nPossible solutions:")
    print("1. Check your API key at: https://makersuite.google.com/app/apikey")
    print("2. Enable the Gemini API in Google Cloud Console")
    print("3. Create a new API key with proper permissions")