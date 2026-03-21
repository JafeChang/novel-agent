<template>
  <div class="chapter-editor">
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <n-button text @click="router.back()">← 返回</n-button>
          <input v-model="chapter.title" class="title-input" placeholder="章节标题" @blur="saveChapter" />
          <n-tag :type="getStatusType(chapter.status)" size="small">
            {{ getStatusText(chapter.status) }}
          </n-tag>
        </div>
        <div class="header-actions">
          <n-select v-model:value="chapter.status" :options="statusOptions" style="width: 120px" @update:value="saveChapter" />
          <n-button type="primary" @click="saveChapter" :loading="saving">
            保存
          </n-button>
        </div>
      </n-layout-header>
      
      <n-layout-content class="content">
        <div class="editor-layout">
          <!-- Main Editor -->
          <div class="editor-area">
            <n-input
              v-model:value="chapter.content"
              type="textarea"
              placeholder="开始写作...

提示：
• 使用自然段落的写作方式
• 人物对话用引号标注
• 适当添加场景描写和心理活动
• 设置悬念为下一章铺垫"
              :autosize="{ minRows: 25 }"
              @blur="saveChapter"
              class="content-editor"
            />
            <div class="editor-footer">
              <span class="word-count">字数: {{ wordCount }}</span>
              <span class="last-saved" v-if="lastSaved">上次保存: {{ lastSaved }}</span>
            </div>
          </div>
          
          <!-- AI Assistant Panel -->
          <div class="ai-panel">
            <h3>🤖 AI 写作助手</h3>
            
            <n-tabs v-model:value="aiTab" size="small">
              <n-tab-pane name="skills" tab="选择技能">
                <div class="skills-list">
                  <div 
                    v-for="skill in skills" 
                    :key="skill.id" 
                    class="skill-item"
                    :class="{ active: selectedSkill?.id === skill.id }"
                    @click="selectSkill(skill)"
                  >
                    <span class="skill-name">{{ skill.name }}</span>
                    <span class="skill-desc">{{ skill.description?.slice(0, 30) }}...</span>
                  </div>
                  <n-empty v-if="!skills.length" description="暂无技能" size="small">
                    <template #extra>
                      <n-button size="tiny" @click="goToSkills">去创建</n-button>
                    </template>
                  </n-empty>
                </div>
              </n-tab-pane>
              
              <n-tab-pane name="execute" tab="执行">
                <div v-if="selectedSkill" class="execute-area">
                  <div class="selected-skill-info">
                    <n-tag type="info">{{ selectedSkill.name }}</n-tag>
                    <n-button text size="tiny" @click="selectedSkill = null">取消</n-button>
                  </div>
                  
                  <p class="execute-hint">{{ selectedSkill.description }}</p>
                  
                  <n-input
                    v-model:value="skillParams"
                    type="textarea"
                    placeholder="输入参数 (JSON格式)"
                    :rows="5"
                    class="params-input"
                  />
                  
                  <n-space vertical :size="12">
                    <n-button type="primary" block :loading="executing" @click="executeSkill">
                      执行技能
                    </n-button>
                    
                    <n-button v-if="executeResult" block @click="applyResult">
                      📝 应用到正文
                    </n-button>
                  </n-space>
                  
                  <div v-if="executeResult" class="execute-result">
                    <div class="result-header">
                      <span>执行结果:</span>
                      <n-button text size="tiny" @click="copyResult">复制</n-button>
                    </div>
                    <pre class="result-content">{{ executeResult }}</pre>
                  </div>
                </div>
                <n-empty v-else description="请先选择一个技能" size="small" />
              </n-tab-pane>
              
              <n-tab-pane name="templates" tab="模板">
                <div class="templates-list">
                  <div class="template-item" @click="insertTemplate('dialogue')">
                    <span>📢 对话</span>
                  </div>
                  <div class="template-item" @click="insertTemplate('description')">
                    <span>🌄 场景描写</span>
                  </div>
                  <div class="template-item" @click="insertTemplate('psychology')">
                    <span>💭 心理活动</span>
                  </div>
                  <div class="template-item" @click="insertTemplate('action')">
                    <span>⚡ 动作描写</span>
                  </div>
                </div>
              </n-tab-pane>
            </n-tabs>
          </div>
        </div>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { chaptersApi, skillsApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NInput, NButton, NSelect,
  NTabs, NTabPane, NEmpty, NTag, NSpace, useMessage, useDialog
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
const saving = ref(false)
const lastSaved = ref('')
let autoSaveTimer: number | null = null

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
  // Auto-save every 30 seconds
  autoSaveTimer = window.setInterval(() => {
    if (chapter.value.content) {
      saveChapter(true)
    }
  }, 30000)
})

onUnmounted(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
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

async function saveChapter(silent = false) {
  saving.value = true
  try {
    await chaptersApi.update(chapterId, {
      title: chapter.value.title,
      content: chapter.value.content,
      status: chapter.value.status,
    })
    if (!silent) {
      message.success('保存成功')
    }
    lastSaved.value = new Date().toLocaleTimeString()
  } catch (error) {
    if (!silent) {
      message.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

function selectSkill(skill: any) {
  selectedSkill.value = skill
  skillParams.value = skill.config ? JSON.stringify(skill.config, null, 2) : '{}'
  aiTab.value = 'execute'
}

async function executeSkill() {
  if (!selectedSkill.value) return
  
  executing.value = true
  executeResult.value = ''
  try {
    const params = JSON.parse(skillParams.value || '{}')
    const response = await skillsApi.execute(selectedSkill.value.id, params, chapterId)
    
    if (response.data.success) {
      executeResult.value = response.data.output || '执行完成（无输出）'
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
  if (executeResult.value && !executeResult.value.startsWith('错误:')) {
    chapter.value.content = (chapter.value.content || '') + '\n\n' + executeResult.value
    saveChapter()
    message.success('已应用到正文')
    executeResult.value = ''
  }
}

function copyResult() {
  navigator.clipboard.writeText(executeResult.value)
  message.success('已复制到剪贴板')
}

function goToSkills() {
  router.push('/skills')
}

function insertTemplate(type: string) {
  const templates: Record<string, string> = {
    dialogue: '    "好吧，"他叹了口气，说道，"也许你是对的。"',
    description: '　　窗外，夕阳的余晖洒在街道上，将一切都染成了金黄色。',
    psychology: '　　她心里清楚，这一切都不会那么简单。但她已经没有了退路。',
    action: '　　他猛地站起身，椅子在地板上发出刺耳的摩擦声。',
  }
  
  const template = templates[type] || ''
  if (template) {
    chapter.value.content = (chapter.value.content || '') + '\n' + template
    message.success('已插入模板')
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
.chapter-editor {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.title-input {
  flex: 1;
  font-size: 18px;
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
  grid-template-columns: 1fr 340px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.editor-area {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content-editor :deep(.n-input__input-el) {
  font-size: 16px;
  line-height: 1.8;
  font-family: 'Georgia', 'Times New Roman', serif;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  color: #999;
  font-size: 13px;
}

.ai-panel {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

.ai-panel h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.skill-item {
  padding: 10px 12px;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.skill-item:hover {
  background: #e8e8e8;
}

.skill-item.active {
  border-color: #18a058;
  background: #f0fdf4;
}

.skill-item .skill-name {
  display: block;
  font-weight: 600;
  font-size: 14px;
}

.skill-item .skill-desc {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.execute-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-skill-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.execute-hint {
  color: #666;
  font-size: 13px;
  margin: 0;
}

.params-input :deep(.n-input__input-el) {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.execute-result {
  margin-top: 12px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
}

.result-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
  background: #fff;
  padding: 8px;
  border-radius: 4px;
}

.templates-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.template-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  text-align: center;
  font-size: 13px;
  transition: background 0.2s;
}

.template-item:hover {
  background: #e5e5e5;
}
</style>
