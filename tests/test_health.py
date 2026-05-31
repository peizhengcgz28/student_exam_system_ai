"""
/health 接口测试
使用 mock 绕过真实 AI 调用
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_ok():
    """AI 可用时，/health 应返回 200 和 status=ok"""
    with patch("app.routers.health.ai_client.ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = "OK"
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["ai_available"] is True
    assert data["ai_reply"] == "OK"


@pytest.mark.asyncio
async def test_health_ai_failure():
    """AI 不可用时，/health 应返回 503"""
    with patch("app.routers.health.ai_client.ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.side_effect = Exception("连接超时")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")

    assert resp.status_code == 503
    data = resp.json()
    assert data["detail"]["ai_available"] is False
    assert "连接超时" in data["detail"]["error"]
