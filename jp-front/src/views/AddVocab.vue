<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";

const API = "http://127.0.0.1:8000";

type Vocab = { id: number; zh: string; ja: string };

const zh = ref("");
const ja = ref("");
const keyword = ref("");

const list = ref<Vocab[]>([]);
const msg = ref("");

// 編輯狀態
const editingId = ref<number | null>(null);
const editZh = ref("");
const editJa = ref("");

async function load() {
  const params = keyword.value.trim() ? { keyword: keyword.value.trim() } : undefined;
  const res = await axios.get(`${API}/vocab`, { params });
  list.value = res.data;
}

async function add() {
  msg.value = "";
  if (!zh.value.trim() || !ja.value.trim()) {
    msg.value = "請輸入中文與日文";
    return;
  }
  try {
    await axios.post(`${API}/vocab`, { zh: zh.value, ja: ja.value });
    zh.value = "";
    ja.value = "";
    await load();
    msg.value = "已新增";
  } catch (err: any) {
    msg.value = err?.response?.data?.detail ?? err?.message ?? "新增失敗";
  }
}

function startEdit(v: Vocab) {
  editingId.value = v.id;
  editZh.value = v.zh;
  editJa.value = v.ja;
  msg.value = "";
}

function cancelEdit() {
  editingId.value = null;
  editZh.value = "";
  editJa.value = "";
}

async function saveEdit(id: number) {
  msg.value = "";
  if (!editZh.value.trim() || !editJa.value.trim()) {
    msg.value = "中文與日文不能為空";
    return;
  }
  try {
    await axios.put(`${API}/vocab/${id}`, { zh: editZh.value, ja: editJa.value });
    cancelEdit();
    await load();
    msg.value = "已更新";
  } catch (err: any) {
    msg.value = err?.response?.data?.detail ?? err?.message ?? "更新失敗";
  }
}

async function remove(id: number) {
  msg.value = "";
  const ok = window.confirm("確定要刪除這筆單字嗎？");
  if (!ok) return;

  try {
    await axios.delete(`${API}/vocab/${id}`);
    // 若剛好刪到正在編輯的那筆
    if (editingId.value === id) cancelEdit();
    await load();
    msg.value = "已刪除";
  } catch (err: any) {
    msg.value = err?.response?.data?.detail ?? err?.message ?? "刪除失敗";
  }
}

async function search() {
  editingId.value = null;
  await load();
}

// AI 助理
const aiLoading = ref(false);
const aiSentence = ref("");
const aiTranslation = ref("");
const aiSpellCheck = ref("");
const aiError = ref("");
async function fetchAISuggest() {
  const zhVal = zh.value.trim();
  const jaVal = ja.value.trim();
  if (!zhVal && !jaVal) {
    clearAI();
    return;
  }
  aiLoading.value = true;
  aiError.value = "";
  try {
    const res = await axios.post(`${API}/ai/suggest`, { zh: zhVal, ja: jaVal });
    aiSentence.value = res.data.sentence;
    aiTranslation.value = res.data.translation;
    aiSpellCheck.value = res.data.spell_check;
  } catch (err: any) {
    aiError.value = err?.response?.data?.detail ?? "AI 服務暫時無法使用";
  } finally {
    aiLoading.value = false;
  }
}

function clearAI() {
  aiSentence.value = "";
  aiTranslation.value = "";
  aiSpellCheck.value = "";
  aiError.value = "";
}

onMounted(load);
</script>

<template>
  <div class="vocab-page">

    <!-- 新增單字卡片 -->
    <div class="card">
      <div class="card-title">新增單字</div>
      <div class="input-row">
        <input v-model="zh" placeholder="中文" class="field" />
        <input v-model="ja" placeholder="日文（ひらがな・漢字）" class="field" />
        <button @click="add" class="btn btn-primary">＋ 新增</button>
        <button @click="fetchAISuggest" class="btn btn-ai">✨ AI 建議</button>
      </div>
    </div>

    <!-- AI 助理卡片 -->
    <div v-if="aiLoading || aiSentence || aiError" class="card ai-card">
      <div class="ai-header">
        <span class="ai-icon">🤖</span>
        <span class="ai-title">AI 助理</span>
      </div>
      <div v-if="aiLoading" class="ai-loading">⏳ 分析中，請稍候...</div>
      <div v-else-if="aiError" class="ai-error">{{ aiError }}</div>
      <template v-else>
        <div v-if="aiSentence" class="ai-row">
          <span class="ai-label">例句</span>
          <span class="ai-val">{{ aiSentence }}</span>
        </div>
        <div v-if="aiTranslation" class="ai-row">
          <span class="ai-label">翻譯</span>
          <span class="ai-val">{{ aiTranslation }}</span>
        </div>
        <div v-if="aiSpellCheck && aiSpellCheck !== 'n/a'" class="ai-row">
          <span class="ai-label">拼寫檢查</span>
          <span :class="['ai-check', aiSpellCheck === 'correct' ? 'check-ok' : 'check-err']">
            {{ aiSpellCheck === 'correct' ? '✅ 正確' : '❌ ' + aiSpellCheck }}
          </span>
        </div>
      </template>
    </div>

    <!-- 搜尋列 -->
    <div class="card search-card">
      <div class="search-row">
        <input
          v-model="keyword"
          placeholder="🔍 搜尋單字（中文或日文關鍵字）"
          class="field field-search"
          @keydown.enter="search"
        />
        <button @click="search" class="btn btn-secondary">搜尋</button>
        <button @click="keyword=''; search();" class="btn btn-ghost">清除</button>
      </div>
      <div v-if="msg" :class="['msg-bar', msg.includes('失敗') || msg.includes('不能') || msg.includes('請') ? 'msg-err' : 'msg-ok']">
        {{ msg }}
      </div>
    </div>

    <!-- 單字列表卡片 -->
    <div class="card table-card">
      <div class="card-head">
        <span class="card-title">單字列表</span>
        <span class="count-pill">{{ list.length }} 筆</span>
      </div>
      <div class="table-wrap">
        <table class="vocab-table">
          <thead>
            <tr>
              <th class="col-id">ID</th>
              <th>中文</th>
              <th>日文</th>
              <th class="col-act">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in list" :key="v.id" :class="{ editing: editingId === v.id }">
              <td class="col-id muted">{{ v.id }}</td>

              <td v-if="editingId !== v.id">{{ v.zh }}</td>
              <td v-else><input v-model="editZh" class="field field-inline" /></td>

              <td v-if="editingId !== v.id" class="ja-text">{{ v.ja }}</td>
              <td v-else><input v-model="editJa" class="field field-inline" /></td>

              <td class="col-act">
                <template v-if="editingId !== v.id">
                  <button @click="startEdit(v)" class="act-btn act-edit">編輯</button>
                  <button @click="remove(v.id)" class="act-btn act-del">刪除</button>
                </template>
                <template v-else>
                  <button @click="saveEdit(v.id)" class="act-btn act-save">儲存</button>
                  <button @click="cancelEdit" class="act-btn act-cancel">取消</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="list.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <div>尚無單字，快來新增你的第一個單字！</div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.vocab-page { display: flex; flex-direction: column; gap: 16px; }

/* ── 共用卡片 ── */
.card {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px 24px;
}
.card-title { font-size: 15px; font-weight: 600; margin-bottom: 14px; color: #1a1a2e; }
.card-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.count-pill {
  font-size: 12px; background: #f0ede8; color: var(--muted);
  padding: 2px 10px; border-radius: 99px;
}

/* ── 輸入列 ── */
.input-row { display: flex; gap: 10px; flex-wrap: wrap; }
.field {
  flex: 1; min-width: 120px;
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color .2s, box-shadow .2s;
  background: #fafaf8;
}
.field:focus { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(36,113,163,.12); }

/* ── 按鈕 ── */
.btn {
  padding: 9px 18px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all .18s; white-space: nowrap;
}
.btn-primary { background: var(--red); color: white; }
.btn-primary:hover { background: var(--red-dark); }
.btn-ai { background: var(--purple); color: white; }
.btn-ai:hover { background: var(--purple-dark); }
.btn-secondary { background: var(--blue); color: white; }
.btn-secondary:hover { background: var(--blue-dark); }
.btn-ghost {
  background: transparent; color: var(--muted);
  border: 1px solid var(--border);
}
.btn-ghost:hover { background: #f0ede8; color: var(--text); }

/* ── AI 卡片 ── */
.ai-card { background: var(--ai-bg); border-left: 4px solid var(--purple); }
.ai-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.ai-icon { font-size: 18px; }
.ai-title { font-weight: 700; font-size: 15px; color: var(--purple); }
.ai-loading { color: var(--muted); font-size: 14px; }
.ai-error { color: var(--red); font-size: 14px; }
.ai-row { display: flex; gap: 10px; margin-top: 8px; font-size: 14px; align-items: flex-start; }
.ai-label {
  flex-shrink: 0; width: 64px;
  color: var(--muted); font-size: 12px; font-weight: 600;
  padding-top: 2px; text-transform: uppercase; letter-spacing: .5px;
}
.ai-val { color: var(--text); line-height: 1.6; }
.ai-check { font-weight: 600; }
.check-ok { color: var(--green); }
.check-err { color: var(--red); }

/* ── 搜尋 ── */
.search-card { padding: 16px 24px; }
.search-row { display: flex; gap: 10px; flex-wrap: wrap; }
.field-search { flex: 1; min-width: 200px; }
.msg-bar {
  margin-top: 10px; padding: 8px 14px;
  border-radius: 6px; font-size: 13px; font-weight: 500;
}
.msg-ok { background: var(--green-bg); color: var(--green); }
.msg-err { background: var(--danger-bg); color: var(--red); }

/* ── 表格 ── */
.table-card { padding: 20px 24px 0; }
.table-wrap { overflow-x: auto; }
.vocab-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.vocab-table thead tr { border-bottom: 2px solid var(--border); }
.vocab-table th {
  padding: 10px 12px; text-align: left;
  color: var(--muted); font-weight: 600; font-size: 12px;
  text-transform: uppercase; letter-spacing: .5px;
}
.vocab-table td { padding: 11px 12px; border-bottom: 1px solid #f0ede8; }
.vocab-table tbody tr:hover { background: #faf9f6; }
.vocab-table tbody tr.editing { background: #fdf6ff; }
.vocab-table tbody tr:last-child td { border-bottom: none; }

.col-id { width: 64px; }
.col-act { width: 160px; }
.muted { color: var(--muted); font-size: 13px; }
.ja-text { font-size: 15px; letter-spacing: .5px; }

.field-inline {
  width: 100%; padding: 6px 10px;
  border: 1px solid var(--blue);
  border-radius: 6px; font-size: 14px;
  font-family: inherit; outline: none;
  background: white;
}

/* ── 操作按鈕（表格內小按鈕） ── */
.act-btn {
  padding: 4px 12px; border-radius: 5px; border: none;
  font-size: 12px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all .15s; margin-right: 6px;
}
.act-edit   { background: #ebf5fb; color: var(--blue); }
.act-edit:hover { background: var(--blue); color: white; }
.act-del    { background: #fdf2f2; color: var(--red); }
.act-del:hover { background: var(--red); color: white; }
.act-save   { background: var(--green-bg); color: var(--green); }
.act-save:hover { background: var(--green); color: white; }
.act-cancel { background: #f0ede8; color: var(--muted); }
.act-cancel:hover { background: #d5d0c8; color: var(--text); }

/* ── 空狀態 ── */
.empty-state {
  text-align: center; padding: 40px 20px;
  color: var(--muted); font-size: 14px;
}
.empty-icon { font-size: 36px; margin-bottom: 10px; }
</style>
