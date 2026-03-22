<template>
  <div class="auth-container">
    <n-card title="登录" style="width: 400px">
      <n-form :model="form" @submit.prevent="handleLogin">
        <n-form-item label="邮箱">
          <n-input v-model:value="form.email" placeholder="your@email.com" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="mousedown" />
        </n-form-item>
        <n-button type="primary" block :loading="authStore.loading" attr-type="submit">
          登录
        </n-button>
      </n-form>
      <div class="auth-footer">
        还没有账号? <router-link to="/register">注册</router-link>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const form = ref({
  email: '',
  password: '',
})

async function handleLogin() {
  const success = await authStore.login(form.value.email, form.value.password)
  if (success) {
    message.success('登录成功')
    await router.push('/')
  } else {
    message.error('登录失败，请检查邮箱和密码')
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.auth-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
}
</style>
