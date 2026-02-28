<template>
  <div class="app-wrapper">
    <header class="app-header">
      <div class="header-inner">
        <div class="logo">
          <div class="logo-badge">日</div>
          <span class="logo-title">日文學習</span>
        </div>
        <nav class="main-nav">
          <RouterLink to="/" class="nav-link">📚 單詞記錄</RouterLink>
          <RouterLink to="/quiz" class="nav-link">✏️ 隨機測驗</RouterLink>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <div class="container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.25);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-badge {
  width: 36px;
  height: 36px;
  background: #c0392b;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}

.main-nav {
  display: flex;
  gap: 4px;
}

.nav-link {
  color: rgba(255,255,255,.7);
  text-decoration: none;
  padding: 7px 14px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  transition: all .2s;
}

.nav-link:hover {
  color: white;
  background: rgba(255,255,255,.12);
}

.nav-link.router-link-active {
  color: white;
  background: rgba(192,57,43,.75);
}

.app-main {
  flex: 1;
  padding: 28px 24px;
}

.container {
  max-width: 960px;
  margin: 0 auto;
}
</style>
