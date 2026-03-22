<template>
  <div class="home-page">
    <n-card class="hero-card">
      <h1>📚 Novel Agent</h1>
      <p>欢迎来到你的 AI 小说创作工作台。</p>
      <div class="actions">
        <n-button v-if="isAuthenticated" type="primary" @click="goToDashboard">
          进入我的项目
        </n-button>
        <template v-else>
          <n-button type="primary" @click="goToLogin">登录</n-button>
          <n-button secondary @click="goToRegister">注册</n-button>
        </template>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { NCard, NButton } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => !!authStore.token)

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}

function goToDashboard() {
  router.push('/dashboard')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fb;
}

.hero-card {
  width: 100%;
  max-width: 640px;
  text-align: center;
}

.hero-card h1 {
  margin: 0 0 12px;
}

.hero-card p {
  color: #666;
  margin-bottom: 24px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
