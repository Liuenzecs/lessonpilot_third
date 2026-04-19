"""导入红楼梦知识库的种子数据脚本。

用法：cd apps/api && python -m scripts.seed_knowledge
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models.knowledge import KnowledgeChunk
from app.services.knowledge_service import (
    build_embedding_error_message,
    estimate_tokens,
    get_embedding_runtime_metadata,
    get_embeddings,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 红楼梦知识数据
# ---------------------------------------------------------------------------

KNOWLEDGE_ENTRIES: list[dict] = [
    # ── 人物档案 ──
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "贾宝玉人物分析",
        "content": "贾宝玉是《红楼梦》的男主人公，荣国府贾政之子。他性格叛逆，厌恶封建礼教和功名利禄，自称“不通世务，怕读文章”。他崇尚真情，对女性充满尊重和同情，认为“女儿是水作的骨肉，男人是泥作的骨肉”。宝玉与林黛玉的爱情是全书主线。他最终在家族衰败后出家为僧。贾宝玉是曹雪芹理想人格的化身，体现了对封建正统的反叛和对真善美的追求。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "贾宝玉", "importance": "primary"},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "林黛玉人物分析",
        "content": "林黛玉是《红楼梦》的女主人公之一，金陵十二钗之首。她是林如海与贾敏之女，幼年丧母后寄居贾府外祖母家。黛玉才华横溢，擅长诗词，性格多愁善感、敏感自尊。她与贾宝玉志趣相投，追求真情和自由，二人产生了深深的爱情。但黛玉体弱多病，最终在宝玉与宝钗成婚之际泪尽而逝。“黛玉葬花”是全书最经典的场景之一，她借落花感叹自身命运的悲凉。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "林黛玉", "importance": "primary"},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "薛宝钗人物分析",
        "content": "薛宝钗是金陵十二钗之一，薛姨妈之女。她容貌丰美、举止端庄、博学多才，深谙世故人情。她佩戴金锁，与宝玉的通灵宝玉有“金玉良缘”之说。宝钗处事圆融，善于笼络人心，与黛玉的率真形成对比。她最终与宝玉成婚，但宝玉心中始终只有黛玉，婚后不久宝玉便出家，宝钗独守空闺。宝钗是封建礼教标准下的完美女性形象。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "薛宝钗", "importance": "primary"},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "王熙凤人物分析",
        "content": "王熙凤是贾琏之妻，荣国府的实际管家人。她精明强干、口才了得，被誉为“凤辣子”。她善于权谋，手段泼辣，管理贾府上下数百人的日常事务。但同时她也贪财弄权，放高利贷，逼死人命。“机关算尽太聪明，反算了卿卿性命”是她命运的真实写照。她最终在贾府败落后病死。王熙凤是《红楼梦》中最生动、最复杂的女性形象之一。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "王熙凤", "importance": "primary"},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "贾母人物分析",
        "content": "贾母是贾府最高长辈，贾代善之妻，宝玉的祖母。她在贾府中地位最高，儿孙满堂。贾母慈爱宽厚，尤其疼爱宝玉和黛玉。她喜欢热闹，爱听戏、赏花、品茶。贾母是封建大家族中慈祥长辈的代表，她对宝玉的溺爱也间接纵容了宝玉的叛逆性格。她在贾府衰败前去世，未能目睹家族最终的结局。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "贾母", "importance": "primary"},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "character_profile",
        "title": "刘姥姥人物分析",
        "content": "刘姥姥是一个质朴善良的农村老妇人，与贾府有远亲关系。她三次进贾府：第一次为求生计来打秋风，第二次携瓜果蔬菜来感谢贾府并游览大观园，第三次在贾府败落后救出巧姐。刘姥姥以她的朴实和幽默成为全书最接地气的人物，也是见证贾府兴衰的重要线索人物。她的三进荣国府是小说结构中的重要节点。",
        "source": "红楼梦人物辞典",
        "chapter": "全书",
        "metadata": {"character": "刘姥姥", "importance": "secondary"},
    },
    # ── 情节摘要 ──
    {
        "domain": "红楼梦",
        "knowledge_type": "plot_summary",
        "title": "黛玉进贾府（第三回）",
        "content": "林黛玉因母亲贾敏病逝，父亲林如海将她送往京城外祖母家（贾府）寄居。黛玉初进贾府，处处小心谨慎，感受到贾府的富贵繁华与森严规矩。她第一次见到了外祖母（贾母）、王熙凤、贾宝玉等人。宝玉见黛玉后惊呼“这个妹妹我曾见过的”，得知黛玉无玉后摔玉，表现出对黛玉的特殊亲近。此回通过黛玉之眼展现了贾府全貌，也为宝黛爱情埋下伏笔。",
        "source": "红楼梦第三回",
        "chapter": "第三回",
        "metadata": {"characters": ["林黛玉", "贾宝玉", "贾母", "王熙凤"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "plot_summary",
        "title": "黛玉葬花（第二十七回）",
        "content": "芒种节这天，众姐妹在园中饯花。黛玉因前夜被晴雯拒于门外，又见宝玉与宝钗说笑，心生伤感。她独自一人来到花冢前，将落花掩埋，并吟出著名的《葬花吟》：“花谢花飞花满天，红消香断有谁怜？”“侬今葬花人笑痴，他年葬侬知是谁？一朝春尽红颜老，花落人亡两不知。”此段借落花隐喻黛玉自身命运的悲剧，是全书最动人心魄的段落之一，也是理解黛玉性格和命运的关键情节。",
        "source": "红楼梦第二十七回",
        "chapter": "第二十七回",
        "metadata": {"characters": ["林黛玉"], "poems": ["葬花吟"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "plot_summary",
        "title": "宝玉挨打（第三十三回）",
        "content": "贾环向贾政告密说宝玉逼死金钏儿，加之贾政此前已对宝玉结交蒋玉菡（琪官）不满，怒不可遏，将宝玉绑在凳上重打。宝玉被打得皮开肉绽。王夫人、贾母闻讯赶来，贾母痛斥贾政。众姐妹和丫鬟纷纷前来探望，黛玉哭得双眼红肿，宝钗送来伤药。此事反映了宝玉与封建父权的尖锐冲突，也展现了不同人物对宝玉的态度。宝玉挨打后更加坚定了不走仕途经济之路的决心。",
        "source": "红楼梦第三十三回",
        "chapter": "第三十三回",
        "metadata": {"characters": ["贾宝玉", "贾政", "贾母", "林黛玉", "薛宝钗"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "plot_summary",
        "title": "抄检大观园（第七十四回）",
        "content": "因在园中捡到一个绣春囊，王夫人大怒，命王善保家的等人夜间抄检大观园各处。抄检过程中，晴雯、探春等人表现出强烈不满和反抗。此次抄检是贾府内部矛盾激化的标志事件，暴露了家族内部的倾轧和混乱。事后晴雯被逐出贾府，抱屈而死。此回是贾府由盛转衰的重要转折点，预示着整个大家族即将走向崩溃。",
        "source": "红楼梦第七十四回",
        "chapter": "第七十四回",
        "metadata": {"characters": ["王夫人", "晴雯", "探春", "王善保家的"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "plot_summary",
        "title": "刘姥姥进大观园（第三十九至四十二回）",
        "content": "刘姥姥二进贾府，贾母留她游览大观园。刘姥姥以质朴的语言和行为引发众人大笑，如在宴席上说“老刘老刘，食量大似牛，吃一个老母猪不抬头”。她参观了潇湘馆（黛玉住处）、蘅芜苑（宝钗住处）等。刘姥姥的质朴与贾府的奢华形成鲜明对比，增加了小说的喜剧色彩，也通过她的视角展现了贾府的日常生活和奢靡之风。",
        "source": "红楼梦第三十九至四十二回",
        "chapter": "第三十九至四十二回",
        "metadata": {"characters": ["刘姥姥", "贾母", "林黛玉", "薛宝钗"]},
    },
    # ── 诗词赏析 ──
    {
        "domain": "红楼梦",
        "knowledge_type": "poetry_analysis",
        "title": "《葬花吟》赏析",
        "content": "《葬花吟》是林黛玉在第二十七回吟诵的长诗，是全书最著名的诗词之一。全诗以花喻人，借落花感叹自身命运。“花谢花飞花满天，红消香断有谁怜”写落花飘零之景，映射黛玉孤苦无依的身世。“质本洁来还洁去，强于污淖陷渠沟”表明黛玉坚守高洁品格的决心。“一朝春尽红颜老，花落人亡两不知”是全诗的点睛之笔，既是对花命运的感慨，也是对自身悲剧命运的预感。此诗与黛玉的性格和命运高度统一。",
        "source": "红楼梦诗词鉴赏",
        "chapter": "第二十七回",
        "metadata": {"poems": ["葬花吟"], "characters": ["林黛玉"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "poetry_analysis",
        "title": "《枉凝眉》赏析",
        "content": "《枉凝眉》是《红楼梦》第五回中太虚幻境的判曲之一，写宝黛爱情悲剧。“一个是阆苑仙葩，一个是美玉无瑕”以仙葩（绛珠仙草，即黛玉）和美玉（通灵宝玉，即宝玉）对举。“若说没奇缘，今生偏又遇着他；若说有奇缘，如何心事终虚化”道出两人有缘无分的悲剧本质。“想眼中能有多少泪珠儿，怎经得秋流到冬尽，春流到夏”暗示黛玉将泪尽而亡。此曲是对宝黛爱情悲剧的高度概括。",
        "source": "红楼梦诗词鉴赏",
        "chapter": "第五回",
        "metadata": {"poems": ["枉凝眉"], "characters": ["贾宝玉", "林黛玉"]},
    },
    # ── 文学分析 ──
    {
        "domain": "红楼梦",
        "knowledge_type": "literary_analysis",
        "title": "金陵十二钗人物体系",
        "content": "金陵十二钗是《红楼梦》中最重要的十二位女性人物，分为正册、副册、又副册三个等级。正册十二钗为：林黛玉、薛宝钗、贾元春、贾探春、史湘云、妙玉、贾迎春、贾惜春、王熙凤、巧姐、李纨、秦可卿。每个人物都有判词和判曲暗示其命运。正册人物构成小说的核心叙事网络，她们的命运交织反映了封建社会女性的悲剧宿命。",
        "source": "红楼梦研究",
        "chapter": "全书",
        "metadata": {"characters": ["金陵十二钗"]},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "literary_analysis",
        "title": "贾府兴衰线索",
        "content": "《红楼梦》以贾府的兴衰为主线，展现了一个封建大家族由盛转衰的全过程。贾府曾“烈火烹油、鲜花着锦”般繁盛，四大家族（贾、史、王、薛）权势滔天。但从元妃省亲的奢靡花费开始，贾府财务日益拮据。内部管理混乱、子弟不肖、腐败横行。抄检大观园是内部矛盾的总爆发，此后贾府加速衰落。最终因种种罪状被抄家，“落了片白茫茫大地真干净”。贾府兴衰是封建社会没落的缩影。",
        "source": "红楼梦研究",
        "chapter": "全书",
        "metadata": {},
    },
    {
        "domain": "红楼梦",
        "knowledge_type": "literary_analysis",
        "title": "木石前盟与金玉良缘",
        "content": "木石前盟指贾宝玉（补天石/神瑛侍者）与林黛玉（绛珠仙草）的前世因缘。神瑛侍者日日浇灌绛珠仙草，仙草修成女身后为报恩下凡，以泪还债。金玉良缘指贾宝玉的通灵宝玉与薛宝钗的金锁所象征的姻缘，是家族安排的门当户对婚姻。木石前盟代表真情和自由选择，金玉良缘代表礼教和家族利益。两者的冲突是全书核心矛盾之一，最终以黛玉泪尽而亡、宝玉出家、宝钗独守空闺的三方悲剧告终。",
        "source": "红楼梦研究",
        "chapter": "全书",
        "metadata": {"characters": ["贾宝玉", "林黛玉", "薛宝钗"]},
    },
]


# ---------------------------------------------------------------------------
# 导入逻辑
# ---------------------------------------------------------------------------


def _build_chunk_metadata(entry_metadata: dict | None) -> dict:
    merged = dict(entry_metadata or {})
    merged["embedding_runtime"] = get_embedding_runtime_metadata()
    return merged


async def _get_embeddings_with_retry(
    texts: list[str],
    *,
    retries: int = 2,
) -> list[list[float]]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return await get_embeddings(texts, type_="db")
        except Exception as exc:  # pragma: no cover - 依赖运行时 provider
            last_error = exc
            logger.warning(
                "Embedding 批量生成失败（第 %d/%d 次）：%s",
                attempt,
                retries + 1,
                build_embedding_error_message(exc),
            )
            if attempt <= retries:
                await asyncio.sleep(min(attempt, 2))

    assert last_error is not None
    raise last_error


async def seed() -> None:
    engine = get_engine()
    runtime = get_embedding_runtime_metadata()
    logger.info(
        "当前 embedding 配置：provider=%s model=%s%s",
        runtime["provider"],
        runtime["model"],
        f" device={runtime['device']}" if "device" in runtime else "",
    )

    with Session(engine) as session:
        existing = session.exec(
            select(KnowledgeChunk).where(KnowledgeChunk.domain == "红楼梦")
        ).all()
        existing_titles = {c.title for c in existing}

        new_entries = [e for e in KNOWLEDGE_ENTRIES if e["title"] not in existing_titles]

        if not new_entries:
            logger.info("没有新的知识条目需要导入")
            return

        logger.info("需要导入 %d 条新知识条目", len(new_entries))

        # 批量生成 embedding
        texts = [e["content"] for e in new_entries]
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                embeddings = await _get_embeddings_with_retry(batch)
            except Exception as e:
                logger.error("Embedding 调用失败：%s", build_embedding_error_message(e))
                logger.info("跳过 batch %d-%d", i, i + batch_size)
                continue

            for j, (entry, embedding) in enumerate(
                zip(new_entries[i : i + batch_size], embeddings)
            ):
                chunk = KnowledgeChunk(
                    domain=entry["domain"],
                    knowledge_type=entry["knowledge_type"],
                    title=entry["title"],
                    content=entry["content"],
                    source=entry["source"],
                    chapter=entry.get("chapter"),
                    metadata_=_build_chunk_metadata(entry.get("metadata")),
                    embedding=embedding,
                    token_count=estimate_tokens(entry["content"]),
                )
                session.add(chunk)
                logger.info("  导入: %s", entry["title"])

            session.commit()

        logger.info("导入完成")

    engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
