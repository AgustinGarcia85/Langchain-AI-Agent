"""
Configuration file for the PRP: LangChain + Daytona Agent System

This file contains configurable parameters that can be modified
without changing the main agent system code.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0")),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
    "api_key": os.getenv("OPENAI_API_KEY"),
}

# Daytona Configuration
DAYTONA_CONFIG = {
    "api_key": os.getenv("DAYTONA_API_KEY"),
    "server_url": os.getenv("DAYTONA_SERVER_URL", "https://api.daytona.io"),
    "timeout": int(os.getenv("DAYTONA_TIMEOUT", "30")),
    "max_retries": int(os.getenv("DAYTONA_MAX_RETRIES", "3")),
}

# Agent Configuration
AGENT_CONFIG = {
    "planner": {
        "max_steps": int(os.getenv("PLANNER_MAX_STEPS", "10")),
        "step_format": os.getenv("PLANNER_STEP_FORMAT", "numbered"),
        "include_descriptions": os.getenv("PLANNER_INCLUDE_DESCRIPTIONS", "true").lower() == "true",
    },
    "executor": {
        "command_timeout": int(os.getenv("EXECUTOR_TIMEOUT", "60")),
        "allow_dangerous_commands": os.getenv("EXECUTOR_ALLOW_DANGEROUS", "false").lower() == "true",
        "max_output_size": int(os.getenv("EXECUTOR_MAX_OUTPUT", "10000")),
    },
    "reviewer": {
        "review_threshold": float(os.getenv("REVIEWER_THRESHOLD", "0.7")),
        "auto_retry_failed": os.getenv("REVIEWER_AUTO_RETRY", "true").lower() == "true",
        "max_review_length": int(os.getenv("REVIEWER_MAX_LENGTH", "500")),
    },
    "orchestrator": {
        "max_concurrent_steps": int(os.getenv("ORCHESTRATOR_MAX_CONCURRENT", "1")),
        "enable_parallel_execution": os.getenv("ORCHESTRATOR_PARALLEL", "false").lower() == "true",
        "auto_optimize_workflow": os.getenv("ORCHESTRATOR_AUTO_OPTIMIZE", "true").lower() == "true",
    }
}

# Memory Configuration
MEMORY_CONFIG = {
    "max_memory_size": int(os.getenv("MEMORY_MAX_SIZE", "1000")),
    "memory_type": os.getenv("MEMORY_TYPE", "conversation_buffer"),
    "enable_persistence": os.getenv("MEMORY_PERSISTENCE", "false").lower() == "true",
    "persistence_file": os.getenv("MEMORY_PERSISTENCE_FILE", "agent_memory.json"),
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    "file": os.getenv("LOG_FILE", "agent_system.log"),
    "console_output": os.getenv("LOG_CONSOLE", "true").lower() == "true",
}

# Security Configuration
SECURITY_CONFIG = {
    "allowed_commands": os.getenv("SECURITY_ALLOWED_COMMANDS", "").split(",") if os.getenv("SECURITY_ALLOWED_COMMANDS") else [],
    "blocked_commands": os.getenv("SECURITY_BLOCKED_COMMANDS", "rm -rf,dd,format").split(","),
    "max_command_length": int(os.getenv("SECURITY_MAX_CMD_LENGTH", "1000")),
    "enable_command_validation": os.getenv("SECURITY_VALIDATION", "true").lower() == "true",
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "enable_caching": os.getenv("PERFORMANCE_CACHING", "true").lower() == "true",
    "cache_ttl": int(os.getenv("PERFORMANCE_CACHE_TTL", "3600")),
    "max_workers": int(os.getenv("PERFORMANCE_MAX_WORKERS", "4")),
    "enable_profiling": os.getenv("PERFORMANCE_PROFILING", "false").lower() == "true",
}

def get_config(section=None):
    """
    Get configuration for a specific section or all configuration
    
    Args:
        section (str, optional): Configuration section name
        
    Returns:
        dict: Configuration dictionary
    """
    if section:
        if section.upper() == "OPENAI":
            return OPENAI_CONFIG
        elif section.upper() == "DAYTONA":
            return DAYTONA_CONFIG
        elif section.upper() == "AGENT":
            return AGENT_CONFIG
        elif section.upper() == "MEMORY":
            return MEMORY_CONFIG
        elif section.upper() == "LOGGING":
            return LOGGING_CONFIG
        elif section.upper() == "SECURITY":
            return SECURITY_CONFIG
        elif section.upper() == "PERFORMANCE":
            return PERFORMANCE_CONFIG
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    return {
        "openai": OPENAI_CONFIG,
        "daytona": DAYTONA_CONFIG,
        "agent": AGENT_CONFIG,
        "memory": MEMORY_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "performance": PERFORMANCE_CONFIG,
    }

def validate_config():
    """
    Validate that all required configuration values are present
    
    Returns:
        tuple: (is_valid, missing_keys)
    """
    required_keys = {
        "openai": ["api_key"],
        "daytona": ["api_key", "server_url"],
    }
    
    missing_keys = []
    
    for section, keys in required_keys.items():
        config = get_config(section)
        for key in keys:
            if not config.get(key):
                missing_keys.append(f"{section}.{key}")
    
    return len(missing_keys) == 0, missing_keys

def print_config_summary():
    """Print a summary of the current configuration"""
    print("🔧 Agent System Configuration Summary")
    print("=" * 50)
    
    config = get_config()
    
    for section, settings in config.items():
        print(f"\n📋 {section.upper()}:")
        for key, value in settings.items():
            # Mask sensitive values
            if "key" in key.lower() and value:
                display_value = f"{value[:8]}..." if len(str(value)) > 8 else "***"
            else:
                display_value = value
            print(f"   {key}: {display_value}")
    
    # Validate configuration
    is_valid, missing = validate_config()
    print(f"\n✅ Configuration Status: {'Valid' if is_valid else 'Invalid'}")
    if missing:
        print(f"❌ Missing required keys: {', '.join(missing)}")

if __name__ == "__main__":
    print_config_summary()