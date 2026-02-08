from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from db import Base, engine, get_db
from models import Vocab
from schemas import (
    VocabCreate, VocabOut, VocabUpdate,
    QuizItem, QuizSubmitRequest, QuizResultItem,
    AISuggestRequest, AISuggestResponse
)
import os
import json
from huggingface_hub import InferenceClient

Base.metadata.create_all(bind=engine)

HF_API_KEY = os.getenv("HF_API_KEY", "")

AI_SYSTEM_PROMPT = """你是一位日文學習助理。請根據用戶提供的中文和/或日文單字，
用以下嚴格 JSON 格式回覆，不要輸出 JSON 以外的任何內容：

{
  "sentence": "一個包含該單字的自然日文例句",
  "translation": "該例句的繁體中文翻譯",
  "spell_check": "若用戶同時提供了中文和日文：檢查日文輸入是否正確對應中文，正確則回 correct，否則給出正確的日文寫法；若只提供一種語言則回 n/a"
}"""

app = FastAPI(title="JP Learning API")

# 讓前端可以呼叫（開發階段先放寬）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/vocab", response_model=VocabOut)
def create_vocab(payload: VocabCreate, db: Session = Depends(get_db)):
    vocab = Vocab(zh=payload.zh.strip(), ja=payload.ja.strip())
    db.add(vocab)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # 可能是 UNIQUE 衝突或其他錯誤
        raise HTTPException(status_code=400, detail="Insert failed (maybe duplicate).")
    db.refresh(vocab)
    return vocab

@app.delete("/vocab/{vocab_id}")
def delete_vocab(vocab_id: int, db: Session = Depends(get_db)):
    vocab = db.query(Vocab).filter(Vocab.id == vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocab not found")

    db.delete(vocab)
    db.commit()
    return {"ok": True}

@app.put("/vocab/{vocab_id}", response_model=VocabOut)
def update_vocab(vocab_id: int, payload: VocabUpdate, db: Session = Depends(get_db)):
    vocab = db.query(Vocab).filter(Vocab.id == vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocab not found")

    vocab.zh = payload.zh.strip()
    vocab.ja = payload.ja.strip()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed (maybe duplicate).")

    db.refresh(vocab)
    return vocab


@app.get("/vocab", response_model=list[VocabOut])
def list_vocab(
    keyword: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    q = db.query(Vocab)
    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(or_(Vocab.zh.like(kw), Vocab.ja.like(kw)))
    return q.order_by(Vocab.id.desc()).limit(200).all()


@app.get("/quiz/random10", response_model=list[QuizItem])
def random_10(db: Session = Depends(get_db)):
    # MySQL 可用 ORDER BY RAND()，資料很多時可再優化
    items = db.query(Vocab.id, Vocab.zh).order_by(func.rand()).limit(10).all()
    return [QuizItem(id=i.id, zh=i.zh) for i in items]

@app.post("/quiz/submit", response_model=list[QuizResultItem])
def submit_quiz(payload: QuizSubmitRequest, db: Session = Depends(get_db)):
    ids = [a.id for a in payload.answers]
    rows = db.query(Vocab).filter(Vocab.id.in_(ids)).all()
    vocab_map = {r.id: r for r in rows}

    results: list[QuizResultItem] = []
    for a in payload.answers:
        vocab = vocab_map.get(a.id)
        if not vocab:
            continue
        user = (a.answer_ja or "").strip()
        correct = (vocab.ja or "").strip()
        # 比對：先用完全相同。你也可以改成忽略空白/全半形/假名轉換等
        is_ok = user == correct
        results.append(QuizResultItem(
            id=vocab.id,
            zh=vocab.zh,
            correct_ja=correct,
            user_ja=user,
            is_correct=is_ok
        ))
    return results


@app.post("/ai/suggest", response_model=AISuggestResponse)
async def ai_suggest(payload: AISuggestRequest):
    import asyncio
    zh_text = payload.zh.strip()
    ja_text = payload.ja.strip()

    if not zh_text and not ja_text:
        raise HTTPException(status_code=400, detail="請至少輸入中文或日文")

    if not HF_API_KEY:
        raise HTTPException(status_code=500, detail="未設定 HF API Key")

    def call_hf():
        client = InferenceClient(api_key=HF_API_KEY)
        return client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            max_tokens=300,
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": f"中文：{zh_text or '（未提供）'}\n日文：{ja_text or '（未提供）'}"}
            ]
        )

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_hf)
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        return AISuggestResponse(
            sentence=data.get("sentence", ""),
            translation=data.get("translation", ""),
            spell_check=data.get("spell_check", "n/a")
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI 回應格式錯誤，請重試")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服務錯誤：{str(e)}")


# 靜態檔案服務（Vue 前端）
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jp-front", "dist")
if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = os.path.join(DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DIST, "index.html"))
