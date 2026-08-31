from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """课程示例的严格基础模型：拒绝模型偷偷添加的字段。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TimelineEvent(StrictModel):
    timestamp: str = Field(min_length=1, description="材料中出现的时间；未知时写 unknown")
    event: str = Field(min_length=1, description="该时间点发生的事实")


class ActionItem(StrictModel):
    action: str = Field(min_length=1, description="下一步可执行动作")
    owner: str = Field(min_length=1, description="负责人；材料缺失时写 unknown")
    deadline: str = Field(min_length=1, description="截止时间；材料缺失时写 unknown")


class IncidentSummary(StrictModel):
    """LLM 输出进入事故系统前必须满足的结构契约。"""

    status: Literal["complete", "insufficient_context"]
    impact: str = Field(min_length=1, max_length=300)
    timeline: list[TimelineEvent] = Field(max_length=5)
    confirmed_root_cause: str = Field(min_length=1, max_length=500)
    unknowns: list[str] = Field(max_length=10)
    actions: list[ActionItem] = Field(max_length=10)
    confidence: float = Field(ge=0.0, le=1.0)
