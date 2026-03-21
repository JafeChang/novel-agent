<template>
  <div class="skills-page">
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <n-button text @click="router.push('/dashboard')">← 返回</n-button>
          <h1>🎯 技能管理</h1>
        </div>
        <n-button type="primary" @click="openCreateModal">创建技能</n-button>
      </n-layout-header>
      
      <n-layout-content class="content">
        <n-tabs v-model:value="tabValue">
          <n-tab-pane name="my" tab="我的技能">
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-gi v-for="skill in mySkills" :key="skill.id">
                <n-card class="skill-card" hoverable>
                  <template #header>
                    <div class="skill-header">
                      <span class="skill-name">{{ skill.name }}</span>
                    </div>
                  </template>
                  <p class="skill-desc">{{ skill.description || '暂无描述' }}</p>
                  <template #footer>
                    <div class="skill-footer">
                      <n-button size="small" @click="editSkill(skill)">编辑</n-button>
                      <n-button size="small" type="info" @click="testSkill(skill)">测试</n-button>
                      <n-button size="small" type="error" @click="deleteSkill(skill.id)">删除</n-button>
                    </div>
                  </template>
                </n-card>
              </n-gi>
            </n-grid>
            <n-empty v-if="!mySkills.length" description="还没有创建技能">
              <template #extra>
                <n-button @click="openCreateModal">创建技能</n-button>
              </template>
            </n-empty>
          </n-tab-pane>
          
          <n-tab-pane name="public" tab="公开技能">
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-gi v-for="skill in publicSkills" :key="skill.id">
                <n-card class="skill-card" hoverable>
                  <template #header>
                    <div class="skill-header">
                      <span class="skill-name">{{ skill.name }}</span>
                      <n-tag type="success" size="small">by {{ skill.owner?.username || '未知' }}</n-tag>
                    </div>
                  </template>
                  <p class="skill-desc">{{ skill.description || '暂无描述' }}</p>
                  <template #footer>
                    <n-button size="small" type="primary" @click="copySkill(skill)">复制到我的技能</n-button>
                  </template>
                </n-card>
              </n-gi>
            </n-grid>
            <n-empty v-if="!publicSkills.length" description="暂无公开技能" />
          </n-tab-pane>
        </n-tabs>
      </n-layout-content>
    </n-layout>
    
    <!-- Create/Edit Skill Modal -->
    <n-modal v-model:show="showModal" style="width: 800px; max-height: 90vh; overflow-y: auto">
      <n-card :title="editingSkill ? '编辑技能' : '创建技能'">
        <n-form :model="skillForm" label-placement="top">
          <n-form-item label="技能名称">
            <n-input v-model:value="skillForm.name" placeholder="输入技能名称，如：小说章节写作" />
          </n-form-item>
          
          <n-form-item label="技能描述">
            <n-input 
              v-model:value="skillForm.description" 
              type="textarea" 
              placeholder="描述这个技能的功能和使用场景..."
              :rows="2"
            />
          </n-form-item>
          
          <n-grid :cols="2" :x-gap="16">
            <n-gi>
              <n-form-item label="配置参数 (JSON)">
                <n-input
                  v-model:value="skillForm.config"
                  type="textarea"
                  placeholder='{"style": "悬疑", "mood": "紧张"}'
                  :rows="4"
                  class="code-input"
                />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="技能代码">
                <n-input
                  v-model:value="skillForm.code"
                  type="textarea"
                  placeholder="输入技能的执行代码..."
                  :rows="4"
                  class="code-input"
                />
              </n-form-item>
            </n-gi>
          </n-grid>
          
          <n-form-item label="公开给其他用户">
            <n-switch v-model:value="skillForm.isPublic" />
          </n-form-item>
          
          <!-- Skill Preview -->
          <n-divider>技能预览</n-divider>
          <n-card size="small" embedded>
            <n-descriptions :column="1" size="small">
              <n-descriptions-item label="名称">{{ skillForm.name || '-' }}</n-descriptions-item>
              <n-descriptions-item label="描述">{{ skillForm.description || '-' }}</n-descriptions-item>
              <n-descriptions-item label="配置">{{ formatJson(skillForm.config) }}</n-descriptions-item>
            </n-descriptions>
          </n-card>
        </n-form>
        
        <template #footer>
          <n-space justify="end">
            <n-button @click="showModal = false">取消</n-button>
            <n-button type="primary" @click="saveSkill" :loading="saving">
              {{ editingSkill ? '保存修改' : '创建技能' }}
            </n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
    
    <!-- Test Skill Modal -->
    <n-modal v-model:show="showTestModal" style="width: 700px">
      <n-card title="测试技能">
        <n-form :model="testForm" label-placement="top">
          <n-form-item label="测试参数 (JSON)">
            <n-input
              v-model:value="testForm.parameters"
              type="textarea"
              placeholder='{"title": "第一章", "characters": "张三"}'
              :rows="6"
              class="code-input"
            />
          </n-form-item>
        </n-form>
        
        <n-spin v-if="testing" />
        <n-input
          v-else
          v-model:value="testResult"
          type="textarea"
          placeholder="执行结果将显示在这里..."
          :rows="8"
          readonly
        />
        
        <template #footer>
          <n-space justify="end">
            <n-button @click="showTestModal = false">关闭</n-button>
            <n-button type="primary" @click="executeSkillTest" :loading="testing">
              执行
            </n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { skillsApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NCard, NButton, NGrid, NGi,
  NEmpty, NModal, NForm, NFormItem, NInput, NSwitch, NTag, NTabs, NTabPane,
  NDivider, NDescriptions, NDescriptionsItem, NSpin, NSpace, useMessage
} from 'naive-ui'

const router = useRouter()
const message = useMessage()

const skills = ref<any[]>([])
const tabValue = ref('my')
const showModal = ref(false)
const showTestModal = ref(false)
const editingSkill = ref<any>(null)
const saving = ref(false)
const testing = ref(false)
const testResult = ref('')
const testSkillRef = ref<any>(null)

const skillForm = ref({
  name: '',
  description: '',
  config: '{}',
  code: '',
  isPublic: false,
})

const testForm = ref({
  parameters: '{}',
})

const mySkills = computed(() => skills.value.filter(s => s.user_id === authStore.user?.id))
const publicSkills = computed(() => skills.value.filter(s => s.is_public === 1 && s.user_id !== authStore.user?.id))

onMounted(() => {
  fetchSkills()
})

async function fetchSkills() {
  try {
    const response = await skillsApi.list()
    skills.value = response.data
  } catch (error) {
    message.error('获取技能列表失败')
  }
}

function openCreateModal() {
  editingSkill.value = null
  skillForm.value = {
    name: '',
    description: '',
    config: '{}',
    code: '',
    isPublic: false,
  }
  showModal.value = true
}

function editSkill(skill: any) {
  editingSkill.value = skill
  skillForm.value = {
    name: skill.name,
    description: skill.description || '',
    config: JSON.stringify(skill.config || {}, null, 2),
    code: skill.code,
    isPublic: skill.is_public === 1,
  }
  showModal.value = true
}

function testSkill(skill: any) {
  testSkillRef.value = skill
  testForm.value = { parameters: skill.config ? JSON.stringify(skill.config, null, 2) : '{}' }
  testResult.value = ''
  showTestModal.value = true
}

async function executeSkillTest() {
  if (!testSkillRef.value) return
  
  testing.value = true
  testResult.value = ''
  try {
    const params = JSON.parse(testForm.value.parameters || '{}')
    const response = await skillsApi.execute(testSkillRef.value.id, params)
    
    if (response.data.success) {
      testResult.value = response.data.output || '执行完成（无输出）'
    } else {
      testResult.value = '错误: ' + (response.data.error || '未知错误')
    }
  } catch (error: any) {
    testResult.value = '错误: ' + (error.message || '执行失败')
  } finally {
    testing.value = false
  }
}

async function saveSkill() {
  if (!skillForm.value.name.trim() || !skillForm.value.code.trim()) {
    message.warning('请填写名称和代码')
    return
  }
  
  saving.value = true
  try {
    const data = {
      name: skillForm.value.name,
      description: skillForm.value.description,
      config: JSON.parse(skillForm.value.config || '{}'),
      code: skillForm.value.code,
      is_public: skillForm.value.isPublic ? 1 : 0,
    }
    
    if (editingSkill.value) {
      await skillsApi.update(editingSkill.value.id, data)
      message.success('技能更新成功')
    } else {
      await skillsApi.create(data)
      message.success('技能创建成功')
    }
    
    showModal.value = false
    editingSkill.value = null
    fetchSkills()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteSkill(id: number) {
  if (!confirm('确定要删除这个技能吗？')) return
  try {
    await skillsApi.delete(id)
    message.success('删除成功')
    fetchSkills()
  } catch (error) {
    message.error('删除失败')
  }
}

async function copySkill(skill: any) {
  try {
    const data = {
      name: skill.name + ' (副本)',
      description: skill.description,
      config: skill.config,
      code: skill.code,
      is_public: 0,
    }
    await skillsApi.create(data)
    message.success('已复制到你的技能列表')
    fetchSkills()
  } catch (error) {
    message.error('复制失败')
  }
}

function formatJson(str: string): string {
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch {
    return str
  }
}

// Import auth store (must be done at top level in script setup)
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
</script>

<style scoped>
.skills-page {
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

.skill-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.skill-card:hover {
  transform: translateY(-2px);
}

.skill-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skill-name {
  font-weight: bold;
}

.skill-desc {
  color: #666;
  font-size: 14px;
  margin: 8px 0;
  min-height: 40px;
}

.skill-footer {
  display: flex;
  gap: 8px;
}

.code-input :deep(.n-input__input-el) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
  font-size: 13px !important;
}
</style>
