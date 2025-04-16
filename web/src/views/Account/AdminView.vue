<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { TabsPaneContext } from 'element-plus'
import { useRouter } from 'vue-router'
import { getRequest } from '@/utils/http'

const activeName = ref('users')
const handleClick = (tab: TabsPaneContext) => {
  console.log(tab.props.name)
}

// 用户数据
const users = ref([
  { id: 1, username: 'user1', email: 'user1@example.com', created_at: '2024-01-01' },
  { id: 2, username: 'user2', email: 'user2@example.com', created_at: '2024-01-02' }
])

// 对话数据
const conversations = ref([
  { id: 1, user_id: 1, title: '对话1', created_at: '2024-01-01', message_count: 10 },
  { id: 2, user_id: 2, title: '对话2', created_at: '2024-01-02', message_count: 5 }
])

// 知识库数据
const knowledgeBases = ref([
  { id: 1, user_id: 1, name: '知识库1', doc_count: 5, created_at: '2024-01-01' },
  { id: 2, user_id: 2, name: '知识库2', doc_count: 3, created_at: '2024-01-02' }
])

// 计算统计数据
const statistics = ref({
  totalUsers: 0,
  totalConversations: 0,
  totalKnowledgeBases: 0
})

// 获取系统信息
async function fetchSystemInfo() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/system_info');
  if (data && data.code === 200) {
    const systemInfo = data.data[0];
    statistics.value.totalUsers = systemInfo.user_count;
    statistics.value.totalConversations = systemInfo.conversation_count;
    statistics.value.totalKnowledgeBases = systemInfo.knowledge_base_count;
  }
}

onMounted(() => {
  fetchSystemInfo();
  // ...existing code...
})

// 搜索关键词
const searchQuery = ref('')

// 过滤后的数据
const filteredUsers = computed(() => {
  return users.value.filter(user => 
    user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const isDarkMode = ref(false)

const router = useRouter()

const navigateTo = (path: string) => {
  router.push(`/admin/${path}`)
}
</script>

<template>
  <div class="admin-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="admin-header">
      <div class="header-left">
        <h1>系统管理控制台</h1>
        <span class="subtitle">AI 助手管理系统</span>
      </div>
      <!-- <el-switch
        v-model="isDarkMode"
        class="theme-switch"
        active-text="暗色"
        inactive-text="亮色"
        inline-prompt
      /> -->
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-cards">
      <el-col :span="8" v-for="(stat, index) in [
        { label: '总用户数', value: statistics.totalUsers, icon: 'User', color: '#1677ff' },
        { label: '总对话数', value: statistics.totalConversations, icon: 'ChatLineRound', color: '#722ed1' },
        { label: '知识库数量', value: statistics.totalKnowledgeBases, icon: 'Collection', color: '#13c2c2' }
      ]" :key="index">
        <div class="stat-card" :style="{ '--card-color': stat.color }">
          <div class="stat-icon">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <div class="quick-access">
      <h2>管理入口</h2>
      <el-row :gutter="24">
        <el-col :span="8" v-for="(item, index) in [
          { title: '对话管理', desc: '查看所有用户对话记录', icon: 'ChatLineSquare', path: 'chat', color: '#1677ff' },
          { title: '知识库管理', desc: '管理用户知识库文档', icon: 'Collection', path: 'base', color: '#722ed1' },
          { title: '用户管理', desc: '管理所有用户', icon: 'Setting', path: 'user', color: '#13c2c2' }
        ]" :key="index">
          <div class="access-card" @click="navigateTo(item.path)" :style="{ '--card-color': item.color }">
            <div class="card-icon">
              <el-icon :size="32"><component :is="item.icon" /></el-icon>
            </div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </el-col>
      </el-row>
    </div>

  </div>
</template>

<style scoped>
.admin-container {
  padding: 32px;
  background: var(--bg-color, #f0f2f5);
  min-height: 100vh;
  transition: all 0.3s;
}

.admin-container.dark-mode {
  --bg-color: #141414;
  --card-bg: #1f1f1f;
  --text-color: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.65);
  --border-color: #303030;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left {
  h1 {
    font-size: 28px;
    margin: 0;
    color: var(--text-color, #1a1a1a);
    font-weight: 600;
  }

  .subtitle {
    font-size: 14px;
    color: var(--text-secondary, #666);
    margin-top: 4px;
  }
}

.statistics-cards {
  margin-bottom: 36px;
}

.stat-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color, #eaeaea);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--card-color);
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
}

.stat-icon {
  background: var(--card-color);
  padding: 16px;
  border-radius: 12px;
  color: white;
  opacity: 0.9;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-color, #1a1a1a);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin-top: 4px;
}

.access-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
  border: 1px solid var(--border-color, #eaeaea);
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--card-color);
    transform: scaleX(0);
    transition: transform 0.3s;
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

    &::after {
      transform: scaleX(1);
    }
  }
}

.card-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--card-color) 15%, transparent);
  border-radius: 16px;
  color: var(--card-color);
}

.access-card h3 {
  font-size: 18px;
  margin: 0 0 12px;
  color: var(--text-color, #1a1a1a);
}

.access-card p {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0;
  line-height: 1.5;
}

.admin-content {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color, #eaeaea);
}

/* // 自适应样式 */
@media (max-width: 768px) {
  .admin-container {
    padding: 16px;
  }

  .statistics-cards .el-col {
    margin-bottom: 16px;
  }

  .stat-card {
    padding: 20px;
  }

  .access-card {
    margin-bottom: 16px;
  }
}
</style>
