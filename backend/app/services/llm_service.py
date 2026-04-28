"""LLM服务模块."""

from __future__ import annotations

import os
from typing import Optional

from hello_agents import HelloAgentsLLM

from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def _sync_llm_env() -> dict[str, Optional[str]]:
    """
    将项目配置显式同步到环境变量，避免底层库回退默认模型。

    优先级: LLM_* > OPENAI_* > settings 默认值
    """
    settings = get_settings()

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or settings.openai_api_key
    base_url = (
        os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or settings.openai_base_url
    )
    model = (
        os.getenv("LLM_MODEL")
        or os.getenv("LLM_MODEL_ID")
        or os.getenv("OPENAI_MODEL")
        or settings.openai_model
    )
    # 不强制 provider，未配置时交给底层自动识别
    provider = os.getenv("LLM_PROVIDER") or None

    if api_key:
        os.environ["LLM_API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    if base_url:
        os.environ["LLM_BASE_URL"] = base_url
        os.environ["OPENAI_BASE_URL"] = base_url
    if model:
        os.environ["LLM_MODEL"] = model
        # hello_agents 当前版本读取 LLM_MODEL_ID
        os.environ["LLM_MODEL_ID"] = model
        os.environ["OPENAI_MODEL"] = model

    if provider:
        os.environ["LLM_PROVIDER"] = provider
    return {"provider": provider, "model": model, "base_url": base_url}


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例(单例模式)
    
    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance

    if _llm_instance is None:
        effective = _sync_llm_env()
        timeout = int(os.getenv("LLM_TIMEOUT", "120"))
        llm_kwargs = {
            "model": effective["model"],
            "api_key": os.getenv("LLM_API_KEY"),
            "base_url": effective["base_url"],
            "timeout": timeout,
        }
        if effective["provider"]:
            llm_kwargs["provider"] = effective["provider"]

        _llm_instance = HelloAgentsLLM(**llm_kwargs)

        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型(实例): {_llm_instance.model}")
        print(f"   模型(期望): {effective['model']}")
        print(f"   Base URL: {effective['base_url']}")

    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None

