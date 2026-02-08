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
  <div>
    <h3>記錄背好的單詞</h3>

    <!-- 新增 -->
    <div style="display:flex; gap:12px; margin: 8px 0;">
      <input v-model="zh" placeholder="中文" style="flex:1; padding:8px;" />
      <input v-model="ja" placeholder="日文" style="flex:1; padding:8px;" />
      <button @click="add" style="padding:8px 12px;">新增</button>
      <button @click="fetchAISuggest" style="padding:8px 12px;">AI 建議</button>
    </div>

    <!-- AI 助理 -->
    <div v-if="aiLoading || aiSentence || aiError"
         style="margin: 8px 0; padding: 12px; border: 1px solid #e0e0e0;
                border-radius: 6px; background: #f9f9f9;">
      <div style="font-weight: bold; margin-bottom: 6px;">AI 助理</div>
      <div v-if="aiLoading" style="color: #888;">分析中...</div>
      <div v-else-if="aiError" style="color: #d00;">{{ aiError }}</div>
      <template v-else>
        <div v-if="aiSentence"><span style="color:#555;">例句：</span>{{ aiSentence }}</div>
        <div v-if="aiTranslation" style="margin-top:4px;"><span style="color:#555;">翻譯：</span>{{ aiTranslation }}</div>
        <div v-if="aiSpellCheck && aiSpellCheck !== 'n/a'" style="margin-top:4px;">
          <span style="color:#555;">拼寫檢查：</span>
          <span :style="{ color: aiSpellCheck === 'correct' ? '#080' : '#d00' }">
            {{ aiSpellCheck === 'correct' ? '正確' : aiSpellCheck }}
          </span>
        </div>
      </template>
    </div>

    <!-- 查詢 -->
    <div style="display:flex; gap:12px; margin: 8px 0; align-items:center;">
      <input
        v-model="keyword"
        placeholder="搜尋（中文或日文關鍵字）"
        style="flex:1; padding:8px;"
        @keydown.enter="search"
      />
      <button @click="search" style="padding:8px 12px;">搜尋</button>
      <button @click="keyword=''; search();" style="padding:8px 12px;">清除</button>
    </div>

    <div v-if="msg" style="margin: 8px 0;">{{ msg }}</div>

    <hr />
    <h4>最近 200 筆</h4>

    <table border="1" cellpadding="6" cellspacing="0" style="width:100%;">
      <thead>
        <tr>
          <th style="width:80px;">ID</th>
          <th>中文</th>
          <th>日文</th>
          <th style="width:180px;">操作</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="v in list" :key="v.id">
          <td>{{ v.id }}</td>

          <!-- 中文欄 -->
          <td v-if="editingId !== v.id">{{ v.zh }}</td>
          <td v-else>
            <input v-model="editZh" style="width:100%; padding:6px;" />
          </td>

          <!-- 日文欄 -->
          <td v-if="editingId !== v.id">{{ v.ja }}</td>
          <td v-else>
            <input v-model="editJa" style="width:100%; padding:6px;" />
          </td>

          <!-- 操作 -->
          <td>
            <template v-if="editingId !== v.id">
              <button @click="startEdit(v)" style="padding:6px 10px; margin-right:6px;">編輯</button>
              <button @click="remove(v.id)" style="padding:6px 10px;">刪除</button>
            </template>

            <template v-else>
              <button @click="saveEdit(v.id)" style="padding:6px 10px; margin-right:6px;">儲存</button>
              <button @click="cancelEdit" style="padding:6px 10px;">取消</button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
