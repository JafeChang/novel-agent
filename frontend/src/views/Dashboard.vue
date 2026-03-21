<template>
  <div class="dashboard">
    <n-layout>
      <n-layout-header class="header">
        <h1>📚 Novel Agent</h1>
        <div class="header-actions">
          <span>欢迎, {{ authStore.user?.username }}</span>
          <n-button @click="handleLogout">退出</n-button>
        </div>
      </n-layout-header>
      
      <n-layout-content class="content">
        <div class="content-header">
          <h2>我的项目</h2>
          <n-button type="primary" @click="showCreateModal = true">新建项目</n-button>
        </div>
        
        <n-grid :cols="3" :x-gap="16" :y-gap="16">
          <n-gi v-for="project in projects" :key="project.id">
            <n-card class="project-card" hoverable @click="goToProject(project.id)">
              <template #header>
                <span class="project-title">{{ project.name }}</span>
              </template>
              <p class="project-desc">{{ project.description || '暂无描述' }}</p>
              <template #footer>
                <div class="project-footer">
                  <span>{{ project.chapters?.length || 0 }} 章节</span>
                  <n-button text type="error" @click.stop="deleteProject(project.id)">删除</n-button>
                </div>
              </template>
            </n-card>
          </n-gi>
        </n-grid>
        
        <n-empty v-if="!projects.length" description="还没有项目，点击上方按钮创建一个">
          <template #extra>
            <n-button @click="showCreateModal = true">新建项目</n-button>
          </template>
        </n-empty>
      </n-layout-content>
    </n-layout>
    
    <!-- Create Project Modal -->
    <n-modal v-model:show="showCreateModal">
      <n-card style="width: 500px" title="新建项目">
        <n-form :model="newProject">
          <n-form-item label="项目名称">
            <n-input v-model:value="newProject.name" placeholder="输入项目名称" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="newProject.description" type="textarea" placeholder="项目描述(可选)" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="createProject">创建</n-button>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { projectsApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NCard, NButton, NGrid, NGi,
  NEmpty, NModal, NForm, NFormItem, NInput, useMessage
} from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const projects = ref<any[]>([])
const showCreateModal = ref(false)
const newProject = ref({ name: '', description: '' })

onMounted(() => {
  fetchProjects()
})

async function fetchProjects() {
  try {
    const response = await projectsApi.list()
    projects.value = response.data
  } catch (error) {
    message.error('获取项目列表失败')
  }
}

async function createProject() {
  if (!newProject.value.name.trim()) {
    message.warning('请输入项目名称')
    return
  }
  try {
    await projectsApi.create(newProject.value)
    message.success('项目创建成功')
    showCreateModal.value = false
    newProject.value = { name: '', description: '' }
    fetchProjects()
  } catch (error) {
    message.error('创建失败')
  }
}

function goToProject(id: number) {
  router.push(`/project/${id}`)
}

async function deleteProject(id: number) {
  try {
    await projectsApi.delete(id)
    message.success('删除成功')
    fetchProjects()
  } catch (error) {
    message.error('删除失败')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.content {
  padding: 24px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h2 {
  margin: 0;
}

.project-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.project-card:hover {
  transform: translateY(-4px);
}

.project-title {
  font-weight: bold;
}

.project-desc {
  color: #666;
  font-size: 14px;
  margin: 8px 0;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
