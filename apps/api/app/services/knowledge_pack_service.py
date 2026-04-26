"""Knowledge pack manifest loading and validation."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.knowledge import KNOWLEDGE_TYPES

KNOWLEDGE_PACK_DIR = Path(__file__).resolve().parents[1] / "data" / "knowledge_packs"
DEFAULT_KNOWLEDGE_PACK = KNOWLEDGE_PACK_DIR / "chinese_literature_v1.json"


class KnowledgePackDomain(BaseModel):
    domain: str
    trigger_terms: list[str]
    description: str = ""

    @field_validator("trigger_terms")
    @classmethod
    def validate_trigger_terms(cls, value: list[str]) -> list[str]:
        terms = [term.strip() for term in value if term.strip()]
        if not terms:
            raise ValueError("trigger_terms must not be empty")
        return terms


class KnowledgePackEntry(BaseModel):
    domain: str
    knowledge_type: str
    title: str
    content: str
    source: str
    chapter: str | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("knowledge_type")
    @classmethod
    def validate_knowledge_type(cls, value: str) -> str:
        if value not in KNOWLEDGE_TYPES:
            raise ValueError(f"unsupported knowledge_type: {value}")
        return value


class KnowledgePack(BaseModel):
    pack_id: str
    version: str
    title: str
    description: str = ""
    domains: list[KnowledgePackDomain]
    entries: list[KnowledgePackEntry]

    @model_validator(mode="after")
    def validate_domains(self) -> "KnowledgePack":
        domain_names = {item.domain for item in self.domains}
        if not domain_names:
            raise ValueError("domains must not be empty")
        for entry in self.entries:
            if entry.domain not in domain_names:
                raise ValueError(f"entry domain is not declared: {entry.domain}")
        return self

    @property
    def domain_map(self) -> dict[str, KnowledgePackDomain]:
        return {domain.domain: domain for domain in self.domains}


def load_knowledge_pack(path: Path = DEFAULT_KNOWLEDGE_PACK) -> KnowledgePack:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return KnowledgePack.model_validate(payload)


@lru_cache(maxsize=1)
def load_default_knowledge_pack() -> KnowledgePack:
    return load_knowledge_pack()


def normalize_trigger_text(value: str) -> str:
    lowered = value.lower()
    return re.sub(r"[\s《》<>“”\"'·\-—_，,。.!！?？:：；;（）()、]+", "", lowered)


def find_matched_trigger_terms(topic: str, trigger_terms: list[str]) -> list[str]:
    raw_topic = topic.lower()
    normalized_topic = normalize_trigger_text(topic)
    matches: list[str] = []
    for term in trigger_terms:
        raw_term = term.lower()
        normalized_term = normalize_trigger_text(term)
        if len(normalized_term) <= 1:
            if normalized_topic == normalized_term:
                matches.append(term)
            continue
        if raw_term in raw_topic or normalized_term in normalized_topic:
            matches.append(term)
    return matches


def build_pack_entry_metadata(
    *,
    pack: KnowledgePack,
    entry: KnowledgePackEntry,
    embedding_runtime: dict[str, str],
) -> dict:
    domain = pack.domain_map[entry.domain]
    metadata = dict(entry.metadata)
    metadata.update(
        {
            "pack_id": pack.pack_id,
            "pack_version": pack.version,
            "trigger_terms": domain.trigger_terms,
            "embedding_runtime": embedding_runtime,
        }
    )
    return metadata
