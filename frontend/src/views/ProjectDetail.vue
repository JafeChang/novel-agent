<template>
  <div class="project-detail">
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <n-button text @click="router.push('/dashboard')">← 返回</n-button>
          <h1>{{ project?.name }}</h1>
        </div>
        <div class="header-actions">
          <n-button @click="handleDeleteProject" type="error">删除项目</n-button>
        </div>
      </n-layout-header>
      
      <n-layout-content class="content">
        <p class="project-desc">{{ project?.description || '暂无描述' }}</p>
        
        <div class="content-header">
          <h2>章节列表</h2>
          <n-button type="primary" @click="showCreateModal = true">新建章节</n-button>
        </div>
        
        <n-list hoverable clickable v-if="chapters.length">
          <n-list-item v-for="chapter in chapters" :key="chapter.id" @click="goToEditor(chapter.id)">
            <template #prefix>
              <span class="chapter-order">{{ chapter.order }}</span>
            </template>
            <n-thing :title="chapter.title">
              <template #description>
                <n-space>
                  <n-tag :type="getStatusType(chapter.status)" size="small">
                    {{ getStatusText(chapter.status) }}
                  </n-tag>
                  <span class="word-count">{{ chapter.word_count }} 字</span>
                </n-space>
              </template>
            </n-thing>
            <template #suffix>
              <n-button text type="error" @click.stop="deleteChapter(chapter.id)">删除</n-button>
            </template>
          </n-list-item>
        </n-list>
        
        <n-empty v-else description="还没有章节，点击上方按钮创建一个">
          <template #extra>
            <n-button @click="showCreateModal = true">新建章节</n-button>
          </template>
        </n-empty>
      </n-layout-content>
    </n-layout>
    
    <!-- Create Chapter Modal -->
    <n-modal v-model:show="showCreateModal">
      <n-card style="width: 500px" title="新建章节">
        <n-form :model="newChapter">
          <n-form-item label="章节标题">
            <n-input v-model:value="newChapter.title" placeholder="输入章节标题" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="createChapter">创建</n-button>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projectsApi, chaptersApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NCard, NButton, NList, NListItem,
  NEmpty, NModal, NForm, NFormItem, NInput, NThing, NTag, NSpace, useMessage
} from 'naive-ui'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const projectId = Number(route.params.id)
const project = ref<any>(null)
const chapters = ref<any[]>([])
const showCreateModal = ref(false)
const newChapter = ref({ title: '' })

onMounted(() => {
  fetchProject()
  fetchChapters()
})

async function fetchProject() {
  try {
    const response = await projectsApi.get(projectId)
    project.value = response.data
  } catch (error) {
    message.error('获取项目失败')
    router.push('/dashboard')
  }
}

async function fetchChapters() {
  try {
    const response = await chaptersApi.list(projectId)
    chapters.value = response.data
  } catch (error) {
    message.error('获取章节列表失败')
  }
}

async function createChapter() {
  if (!newChapter.value.title.trim()) {
    message.warning('请输入章节标题')
    return
  }
  try {
    await chaptersApi.create(projectId, {
      title: newChapter.value.title,
      order: chapters.value.length + 1,
    })
    message.success('章节创建成功')
    showCreateModal.value = false
    newChapter.value = { title: '' }
    fetchChapters()
  } catch (error) {
    message.error('创建失败')
  }
}

function goToEditor(chapterId: number) {
  router.push(`/editor/${chapterId}`)
}

async function deleteChapter(chapterId: number) {
  try {
    await chaptersApi.delete(chapterId)
    message.success('删除成功')
    fetchChapters()
  } catch (error) {
    message.error('删除失败')
  }
}

async function handleDeleteProject() {
  if (!confirm('确定要删除这个项目吗？所有章节将被永久删除。')) return
  try {
    await projectsApi.delete(projectId)
    message.success('项目已删除')
    router.push('/dashboard')
  } catch (error) {
    message.error('删除失败')
  }
}

function getStatusType(status: string) {
  const map: Record<string, any> = {
    draft: 'default',
    writing: 'info',
    completed: 'success',
    published: 'warning',
  }
  return map[status] || 'default'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    draft: '草稿',
    writing: '写作中',
    completed: '已完成',
    published: '已发布',
  }
  return map[status] || status
}
</script>

<style scoped>
.project-detail {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.content {
  padding: 24px;
}

.project-desc {
  color: #666;
  margin-bottom: 24px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.content-header h2 {
  margin: 0;
}

.chapter-order {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #eee;
  border-radius: 50%;
  font-weight: bold;
}

.word-count {
  color: #999;
  font-size: 12px;
}
</style>
