#!/usr/bin/env python
import sys
import warnings
import argparse
from typing import List
from enum import Enum
import os
from dotenv import load_dotenv

# Load environment variables at the start
load_dotenv()

# Set model configuration
os.environ["MODEL_NAME"] = os.getenv("MODEL_NAME", "anthropic/claude-3-sonnet-20240229")
os.environ["MODEL_PROVIDER"] = os.getenv("MODEL_PROVIDER", "anthropic")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

from testcontainers_demo_generator.crew import TestcontainersDemoGenerator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class SupportedLanguage(str, Enum):
    JAVA = "java"
    PYTHON = "python"
    CSHARP = "csharp"
    NODE = "node"
    GO = "go"

class SupportedService(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    KAFKA = "kafka"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"

def parse_args():
    parser = argparse.ArgumentParser(description='Generate Testcontainers demo projects')
    
    parser.add_argument(
        '--language', '-l',
        type=str,
        choices=[lang.value for lang in SupportedLanguage],
        required=True,
        help='Programming language for the demo'
    )
    
    parser.add_argument(
        '--services', '-s',
        type=str,
        nargs='+',
        choices=[service.value for service in SupportedService],
        required=True,
        help='Services to include in the demo (space-separated)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='demo_implementation.md',
        help='Output file path (default: demo_implementation.md)'
    )

    return parser.parse_args()

def run():
    args = parse_args()
    inputs = {
        'language': args.language,
        'services': ' '.join(args.services)
    }
    
    generator = TestcontainersDemoGenerator(
        language=args.language,
        services=' '.join(args.services)
    )
    
    # Run the crew and get the result
    result = generator.crew().kickoff()
    
    # Write the result to the specified output file
    with open(args.output, 'w') as f:
        f.write("# Testcontainers Demo Implementation\n\n")
        f.write(f"Generated for {args.language.upper()} with {', '.join(args.services)}\n\n")
        # Convert CrewOutput to string by getting its final answer
        f.write(str(result.final_answer) if hasattr(result, 'final_answer') else str(result))
    
    print(f"\nDemo implementation has been written to {args.output}")

if __name__ == "__main__":
    run()
