"""Omni2 database models - existing tables we'll read from."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Omni2 users table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)  # Changed from username to name
    role = Column(String, nullable=False, default="read_only")
    slack_user_id = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    is_super_admin = Column(Boolean, default=False, nullable=False)
    password_hash = Column(String)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)


class MCPServer(Base):
    """Omni2 MCP servers table."""
    __tablename__ = "mcp_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_healthy = Column(Boolean, default=None)
    last_health_check = Column(DateTime)
    last_seen = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)
    version = Column(String)
    capabilities = Column(JSON)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class MCPTool(Base):
    """Omni2 MCP tools table."""
    __tablename__ = "mcp_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Omni2 audit logs table - tracks user interactions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    question = Column(Text)
    request_type = Column(String)  # 'chat', 'tool', etc.
    message = Column(Text)
    message_preview = Column(String)
    iterations = Column(Integer)
    tool_calls_count = Column(Integer)
    tools_used = Column(JSON)  # Array in Postgres
    mcps_accessed = Column(JSON)  # Array in Postgres
    databases_accessed = Column(JSON)  # Array in Postgres
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    tokens_cached = Column(Integer)
    cost_estimate = Column(Float)  # THIS EXISTS!
    mcp_target = Column(String)
    tool_called = Column(String)
    tool_params = Column(JSON)
    success = Column(Boolean, nullable=False, default=True)
    status = Column(String)
    warning = Column(String)
    duration_ms = Column(Integer)
    result_summary = Column(Text)
    response_preview = Column(Text)
    error_message = Column(Text)
    error_id = Column(String)
    slack_channel = Column(String)
    slack_user_id = Column(String)
    slack_message_ts = Column(String)
    slack_thread_ts = Column(String)
    llm_confidence = Column(Float)
    llm_reasoning = Column(Text)
    llm_tokens_used = Column(Integer)
    ip_address = Column(String)
    user_agent = Column(Text)
    was_blocked = Column(Boolean)
    block_reason = Column(Text)
    created_at = Column(DateTime, index=True)


class Session(Base):
    """Omni2 sessions table."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
