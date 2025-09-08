from app.infrastructure.rag.retriever import SimpleRetriever, tokenize


def test_tokenize_handles_cjk_and_ascii():
    tks = tokenize("红色像苹果 red car 勇敢")
    # should contain CJK chars and ascii words
    assert "红" in tks and "色" in tks and "red" in tks and "car" in tks


def test_retriever_from_dataset_basic():
    ds = {
        "knowledge_cards": [
            {"id": "KC-RED-01", "title": "什么是红色", "lines": ["红色像苹果"], "tags": ["颜色"]},
            {"id": "KC-BRAVE-01", "title": "勇敢是什么", "lines": ["勇敢就是不怕"], "tags": ["品质"]},
        ],
        "story_prompts": [
            {"id": "SP-01", "title": "红色小车冒险", "prompt": "关于红色小车的勇敢故事"}
        ],
    }
    r = SimpleRetriever.from_kids_dataset(ds)
    res = r.retrieve("红色小车", top_k=2)
    assert res and any("红" in (it.get("text") or "") for it in res)

