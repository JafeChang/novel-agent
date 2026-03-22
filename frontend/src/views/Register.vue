<template>
  <div class="auth-container">
    <n-card title="注册" style="width: 400px">
      <n-form :model="form" @submit.prevent="handleRegister">
        <n-form-item label="邮箱">
          <n-input v-model:value="form.email" placeholder="your@email.com" />
        </n-form-item>
        <n-form-item label="用户名">
          <n-input v-model:value="form.username" placeholder="username" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="form.password" type="password" show-password-on="mousedown" />
        </n-form-item>
        <n-button type="primary" block :loading="authStore.loading" attr-type="submit">
          注册
        </n-button>
      </n-form>
      <div class="auth-footer">
        已有账号? <router-link to="/login">登录</router-link>
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
  username: '',
  password: '',
})

async function handleRegister() {
  const success = await authStore.register(form.value.email, form.value.username, form.value.password)
  if (success) {
    message.success('注册成功')
    router.push('/')
  } else {
    message.error('注册失败，邮箱或用户名可能已被使用')
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
