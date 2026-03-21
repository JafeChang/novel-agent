<template>
  <div class="skills-page">
    <n-layout>
      <n-layout-header class="header">
        <div class="header-left">
          <n-button text @click="router.push('/dashboard')">← 返回</n-button>
          <h1>🎯 技能管理</h1>
        </div>
        <n-button type="primary" @click="showCreateModal = true">创建技能</n-button>
      </n-layout-header>
      
      <n-layout-content class="content">
        <n-grid :cols="2" :x-gap="16" :y-gap="16">
          <n-gi v-for="skill in skills" :key="skill.id">
            <n-card class="skill-card">
              <template #header>
                <div class="skill-header">
                  <span class="skill-name">{{ skill.name }}</span>
                  <n-tag v-if="skill.is_public" type="success" size="small">公开</n-tag>
                  <n-tag v-else type="default" size="small">私有</n-tag>
                </div>
              </template>
              <p class="skill-desc">{{ skill.description || '暂无描述' }}</p>
              <template #footer>
                <div class="skill-footer">
                  <n-button size="small" @click="editSkill(skill)">编辑</n-button>
                  <n-button size="small" type="error" @click="deleteSkill(skill.id)">删除</n-button>
                </div>
              </template>
            </n-card>
          </n-gi>
        </n-grid>
        
        <n-empty v-if="!skills.length" description="还没有技能，点击上方按钮创建一个">
          <template #extra>
            <n-button @click="showCreateModal = true">创建技能</n-button>
          </template>
        </n-empty>
      </n-layout-content>
    </n-layout>
    
    <!-- Create/Edit Skill Modal -->
    <n-modal v-model:show="showCreateModal" style="width: 700px">
      <n-card :title="editingSkill ? '编辑技能' : '创建技能'">
        <n-form :model="skillForm">
          <n-form-item label="技能名称">
            <n-input v-model:value="skillForm.name" placeholder="输入技能名称" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="skillForm.description" type="textarea" placeholder="技能描述(可选)" />
          </n-form-item>
          <n-form-item label="配置 (JSON)">
            <n-input
              v-model:value="skillForm.config"
              type="textarea"
              placeholder='{"param1": "value1"}'
              :rows="3"
            />
          </n-form-item>
          <n-form-item label="代码">
            <n-input
              v-model:value="skillForm.code"
              type="textarea"
              placeholder="输入技能执行代码..."
              :rows="10"
            />
          </n-form-item>
          <n-form-item label="公开">
            <n-switch v-model:value="skillForm.isPublic" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="saveSkill">{{ editingSkill ? '保存' : '创建' }}</n-button>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { skillsApi } from '../api'
import {
  NLayout, NLayoutHeader, NLayoutContent, NCard, NButton, NGrid, NGi,
  NEmpty, NModal, NForm, NFormItem, NInput, NSwitch, NTag, useMessage
} from 'naive-ui'

const router = useRouter()
const message = useMessage()

const skills = ref<any[]>([])
const showCreateModal = ref(false)
const editingSkill = ref<any>(null)

const skillForm = ref({
  name: '',
  description: '',
  config: '{}',
  code: '',
  isPublic: false,
})

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

function editSkill(skill: any) {
  editingSkill.value = skill
  skillForm.value = {
    name: skill.name,
    description: skill.description || '',
    config: JSON.stringify(skill.config || {}, null, 2),
    code: skill.code,
    isPublic: skill.is_public === 1,
  }
  showCreateModal.value = true
}

async function saveSkill() {
  if (!skillForm.value.name.trim() || !skillForm.value.code.trim()) {
    message.warning('请填写名称和代码')
    return
  }
  
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
    
    showCreateModal.value = false
    editingSkill.value = null
    resetForm()
    fetchSkills()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
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

function resetForm() {
  skillForm.value = {
    name: '',
    description: '',
    config: '{}',
    code: '',
    isPublic: false,
  }
}
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
}

.skill-footer {
  display: flex;
  gap: 8px;
}
</style>
