<template>
  <div class="chapter-editor">
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <n-button text @click="router.back()">← 返回</n-button>
          <input v-model="chapter.title" class="title-input" placeholder="章节标题" @blur="saveChapter" />
        </div>
        <div class="header-actions">
          <n-select v-model:value="chapter.status" :options="statusOptions" style="width: 120px" @update:value="saveChapter" />
          <n-button type="primary" @click="saveChapter">保存</n-button>
        </div>
      </n-layout-header>
      
      <n-layout-content class="content">
        <div class="editor-layout">
          <div class="editor-area">
            <n-input
              v-model:value="chapter.content"
              type="textarea"
              placeholder="开始写作..."
              :autosize="{ minRows: 20 }"
              @blur="saveChapter"
            />
            <div class="word-count">字数: {{ wordCount }}</div>
          </div>
          
          <div class="ai-panel">
            <h3>🤖 AI 写作助手</h3>
            
            <n-tabs v-model:value="aiTab">
              <n-tab-pane name="skills" tab="技能">
                <div class="skills-list">
                  <div v-for="skill in skills" :key="skill.id" class="skill-item" @click="selectSkill(skill)">
                    <span>{{ skill.name }}</span>
                  </div>
                  <n-empty v-if="!skills.length" description="暂无技能" />
                </div>
              </n-tab-pane>
              
              <n-tab-pane name="execute" tab="执行">
                <div v-if="selectedSkill" class="execute-area">
                  <h4>{{ selectedSkill.name }}</h4>
                  <p>{{ selectedSkill.description }}</p>
                  
                  <n-input
                    v-model:value="skillParams"
                    type="textarea"
                    placeholder="输入参数 (JSON格式)"
                    :rows="4"
                  />
                  
                  <n-button type="primary" block :loading="executing" @click="executeSkill">
                    执行技能
                  </n-button>
                  
                  <div v-if="executeResult" class="execute-result">
                    <h5>结果:</h5>
                    <pre>{{ executeResult }}</pre>
                    <n-button @click="applyResult">应用到正文</n-button>
                  </div>
                </div>
                <n-empty v-else description="请先选择一个技能" />
              </n-tab-pane>
            </n-tabs>
          </div>
        </div>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { chaptersApi, skillsApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NInput, NButton, NSelect,
  NTabs, NTabPane, NEmpty, useMessage
} from 'naive-ui'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const chapterId = Number(route.params.chapterId)
const chapter = ref<any>({ title: '', content: '', status: 'draft' })
const skills = ref<any[]>([])
const aiTab = ref('skills')
const selectedSkill = ref<any>(null)
const skillParams = ref('{}')
const executing = ref(false)
const executeResult = ref('')

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '写作中', value: 'writing' },
  { label: '已完成', value: 'completed' },
  { label: '已发布', value: 'published' },
]

const wordCount = computed(() => {
  return chapter.value.content?.length || 0
})

onMounted(() => {
  fetchChapter()
  fetchSkills()
})

async function fetchChapter() {
  try {
    const response = await chaptersApi.get(chapterId)
    chapter.value = response.data
  } catch (error) {
    message.error('获取章节失败')
    router.back()
  }
}

async function fetchSkills() {
  try {
    const response = await skillsApi.list()
    skills.value = response.data
  } catch (error) {
    console.error('Failed to fetch skills:', error)
  }
}

async function saveChapter() {
  try {
    await chaptersApi.update(chapterId, {
      title: chapter.value.title,
      content: chapter.value.content,
      status: chapter.value.status,
    })
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  }
}

function selectSkill(skill: any) {
  selectedSkill.value = skill
  aiTab.value = 'execute'
}

async function executeSkill() {
  if (!selectedSkill.value) return
  
  executing.value = true
  try {
    const params = JSON.parse(skillParams.value || '{}')
    const response = await skillsApi.execute(selectedSkill.value.id, params, chapterId)
    
    if (response.data.success) {
      executeResult.value = response.data.output || '执行完成'
    } else {
      executeResult.value = '错误: ' + (response.data.error || '未知错误')
    }
  } catch (error: any) {
    executeResult.value = '错误: ' + (error.message || '执行失败')
  } finally {
    executing.value = false
  }
}

function applyResult() {
  if (executeResult.value) {
    chapter.value.content += '\n\n' + executeResult.value
    saveChapter()
    message.success('已应用到正文')
  }
}
</script>

<style scoped>
.chapter-editor {
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
  flex: 1;
}

.title-input {
  flex: 1;
  font-size: 20px;
  font-weight: bold;
  border: none;
  outline: none;
  padding: 8px;
  background: transparent;
}

.title-input:focus {
  background: #f5f5f5;
  border-radius: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content {
  padding: 24px;
}

.editor-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

.editor-area {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.word-count {
  margin-top: 12px;
  text-align: right;
  color: #999;
  font-size: 14px;
}

.ai-panel {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-panel h3 {
  margin: 0 0 16px 0;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.skill-item:hover {
  background: #e5e5e5;
}

.execute-area h4 {
  margin: 0 0 8px 0;
}

.execute-area p {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.execute-area .n-input {
  margin-bottom: 12px;
}

.execute-result {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.execute-result pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  max-height: 200px;
  overflow-y: auto;
  margin: 12px 0;
}

.execute-result h5 {
  margin: 0;
}
</style>
