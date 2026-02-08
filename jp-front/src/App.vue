<template>
  <div style="max-width: 900px; margin: 24px auto; font-family: sans-serif;">
    <h2>日文學習</h2>
    <nav style="display:flex; gap:12px; margin-bottom: 16px;">
      <RouterLink to="/">單詞記錄</RouterLink>
      <RouterLink to="/quiz">隨機測驗</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
