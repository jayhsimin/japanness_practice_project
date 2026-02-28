<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

const API = "http://127.0.0.1:8000";

type QuizItem = { id: number; zh: string };
type ResultItem = { id:number; zh:string; correct_ja:string; user_ja:string; is_correct:boolean };

const items = ref<QuizItem[]>([]);
const answers = ref<Record<number, string>>({});
const results = ref<ResultItem[] | null>(null);

async function fetch10() {
  results.value = null;
  const res = await axios.get(`${API}/quiz/random10`);
  items.value = res.data;
  answers.value = {};
  for (const it of items.value) answers.value[it.id] = "";
}

async function submit() {
  const payload = {
    answers: items.value.map(it => ({
      id: it.id,
      answer_ja: answers.value[it.id] ?? ""
    }))
  };
  const res = await axios.post(`${API}/quiz/submit`, payload);
  results.value = res.data;
}
</script>

<template>
  <div class="quiz-page">

    <!-- 操作區 -->
    <div class="card action-card">
      <div class="action-left">
        <div class="card-title">隨機測驗</div>
        <p class="subtitle">從單字庫隨機抽取 10 題，輸入對應的日文單字</p>
      </div>
      <div class="action-btns">
        <button @click="fetch10" class="btn btn-primary">🎲 抽 10 題</button>
        <button :disabled="items.length === 0" @click="submit" class="btn btn-secondary">📝 送出比對</button>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-if="items.length === 0 && !results" class="card empty-card">
      <div class="empty-icon">🎯</div>
      <div class="empty-text">點擊「抽 10 題」開始測驗</div>
    </div>

    <!-- 題目表格 -->
    <div v-if="items.length > 0" class="card table-card">
      <div class="card-title">作答區</div>
      <div class="table-wrap">
        <table class="quiz-table">
          <thead>
            <tr>
              <th class="col-no">#</th>
              <th>中文</th>
              <th>輸入日文</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(it, idx) in items" :key="it.id">
              <td class="col-no num">{{ idx + 1 }}</td>
              <td class="zh-text">{{ it.zh }}</td>
              <td>
                <input
                  v-model="answers[it.id]"
                  placeholder="請輸入日文..."
                  class="answer-input"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 結果卡片 -->
    <div v-if="results" class="card result-card">
      <div class="result-header">
        <span class="card-title">測驗結果</span>
        <span class="score-pill">
          {{ results.filter(r => r.is_correct).length }} / {{ results.length }} 正確
        </span>
      </div>
      <div class="table-wrap">
        <table class="result-table">
          <thead>
            <tr>
              <th>中文</th>
              <th>你輸入的</th>
              <th>正確答案</th>
              <th class="col-result">結果</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in results" :key="r.id" :class="r.is_correct ? 'row-ok' : 'row-ng'">
              <td>{{ r.zh }}</td>
              <td :class="r.is_correct ? 'ans-ok' : 'ans-ng'">{{ r.user_ja || '（未填）' }}</td>
              <td class="correct-ans">{{ r.correct_ja }}</td>
              <td class="col-result">{{ r.is_correct ? '✅' : '❌' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<style scoped>
.quiz-page { display: flex; flex-direction: column; gap: 16px; }

/* ── 共用卡片 ── */
.card {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px 24px;
}
.card-title { font-size: 15px; font-weight: 700; color: #1a1a2e; }

/* ── 操作區 ── */
.action-card { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.subtitle { font-size: 13px; color: var(--muted); margin-top: 4px; }
.action-btns { display: flex; gap: 10px; flex-shrink: 0; }

.btn {
  padding: 9px 20px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all .18s; white-space: nowrap;
}
.btn-primary { background: var(--red); color: white; }
.btn-primary:hover { background: var(--red-dark); }
.btn-secondary { background: var(--blue); color: white; }
.btn-secondary:hover { background: var(--blue-dark); }
.btn-secondary:disabled { opacity: .4; cursor: not-allowed; }

/* ── 空狀態 ── */
.empty-card { text-align: center; padding: 48px 20px; }
.empty-icon { font-size: 40px; margin-bottom: 12px; }
.empty-text { color: var(--muted); font-size: 15px; }

/* ── 題目表格 ── */
.table-card { padding: 20px 24px 0; }
.table-card .card-title { margin-bottom: 14px; }
.table-wrap { overflow-x: auto; }

.quiz-table, .result-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.quiz-table thead tr, .result-table thead tr { border-bottom: 2px solid var(--border); }
.quiz-table th, .result-table th {
  padding: 10px 12px; text-align: left;
  color: var(--muted); font-weight: 600; font-size: 12px;
  text-transform: uppercase; letter-spacing: .5px;
}
.quiz-table td, .result-table td { padding: 11px 12px; border-bottom: 1px solid #f0ede8; }
.quiz-table tbody tr:hover { background: #faf9f6; }
.quiz-table tbody tr:last-child td,
.result-table tbody tr:last-child td { border-bottom: none; }

.col-no { width: 48px; }
.col-result { width: 72px; text-align: center; }
.num { color: var(--muted); font-size: 13px; font-weight: 600; }
.zh-text { font-weight: 500; }

.answer-input {
  width: 100%; padding: 7px 10px;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 14px; font-family: inherit; outline: none;
  transition: border-color .2s;
}
.answer-input:focus { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(36,113,163,.12); }

/* ── 結果 ── */
.result-card { padding: 20px 24px 0; }
.result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.score-pill {
  font-size: 13px; font-weight: 700;
  background: #eafaf1; color: var(--green);
  padding: 3px 12px; border-radius: 99px;
}

.row-ok { background: #f0faf4; }
.row-ng { background: #fdf5f5; }
.row-ok:hover { background: #e6f7ed; }
.row-ng:hover { background: #fceaea; }

.ans-ok { color: var(--green); font-weight: 600; }
.ans-ng { color: var(--red); font-weight: 600; text-decoration: line-through; }
.correct-ans { color: #1a1a2e; font-weight: 600; }
</style>
