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
  <div>
    <h3>隨機測驗（10 題）</h3>
    <div style="display:flex; gap:12px; margin-bottom: 12px;">
      <button @click="fetch10" style="padding:8px 12px;">抽 10 題</button>
      <button :disabled="items.length===0" @click="submit" style="padding:8px 12px;">送出比對</button>
    </div>

    <div v-if="items.length>0">
      <table border="1" cellpadding="6" cellspacing="0" style="width:100%;">
        <thead>
          <tr>
            <th>#</th>
            <th>中文</th>
            <th>輸入日文</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(it, idx) in items" :key="it.id">
            <td>{{ idx+1 }}</td>
            <td>{{ it.zh }}</td>
            <td>
              <input v-model="answers[it.id]" placeholder="日文" style="width:100%; padding:6px;" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="results">
      <hr />
      <h4>結果</h4>
      <table border="1" cellpadding="6" cellspacing="0" style="width:100%;">
        <thead>
          <tr>
            <th>中文</th>
            <th>你輸入的</th>
            <th>正確答案</th>
            <th>是否正確</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.id">
            <td>{{ r.zh }}</td>
            <td>{{ r.user_ja }}</td>
            <td>{{ r.correct_ja }}</td>
            <td>{{ r.is_correct ? "✅" : "❌" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
