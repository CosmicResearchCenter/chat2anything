<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import type { TabsPaneContext } from 'element-plus'
import { useRouter } from 'vue-router'
import { getRequest } from '@/utils/http'
import * as echarts from 'echarts'

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
  totalKnowledgeBases: 0,
  activeUsers: 0
})

// 图表数据
const chartData = reactive({
  userGrowth: {
    labels: [],
    values: []
  },
  conversationTrend: {
    labels: [],
    values: []
  }
})

// 系统状态
const systemStatus = ref({
  cpuUsage: 0,
  memoryUsage: 0,
  diskUsage: 0,
  status: 'healthy' // healthy, warning, critical
})

// 活跃用户增长率
const activeUserGrowth = ref(0)

// 定义活动类型接口
interface Activity {
  id: number | string;
  type: 'user' | 'conversation' | 'knowledge' | string;
  username: string;
  action: string;
  time: string;
}

// 最近活动
const recentActivities = ref<Activity[]>([])

// 获取系统信息
async function fetchSystemInfo() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/system_info');
  if (data && data.code === 200) {
    const systemInfo = data.data[0];
    statistics.value.totalUsers = systemInfo.user_count;
    statistics.value.totalConversations = systemInfo.conversation_count;
    statistics.value.totalKnowledgeBases = systemInfo.knowledge_base_count;
    
    // 获取系统资源使用情况
    fetchSystemResources();
    
    // 获取活跃用户统计
    fetchActiveUsers();
    
    // 初始化图表
    fetchUserGrowth();
    fetchConversationTrend();
    
    // 获取最近活动
    fetchRecentActivities();
  }
}

// 获取系统资源使用情况
async function fetchSystemResources() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/system_resources');
  if (data && data.code === 200) {
    const resources = data.data[0];
    systemStatus.value = {
      cpuUsage: resources.cpu_usage,
      memoryUsage: resources.memory_usage,
      diskUsage: resources.disk_usage,
      status: resources.status
    };
  }
}

// 获取活跃用户统计
async function fetchActiveUsers() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/active_users');
  if (data && data.code === 200) {
    const activeUserData = data.data[0];
    statistics.value.activeUsers = activeUserData.active_users;
    activeUserGrowth.value = activeUserData.growth_rate;
  }
}

// 获取最近活动
async function fetchRecentActivities() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/recent_activities');
  if (data && data.code === 200) {
    recentActivities.value = data.data[0];
  }
}

// 获取用户增长趋势
async function fetchUserGrowth() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/user_growth');
  if (data && data.code === 200) {
    chartData.userGrowth = data.data[0];
    updateUserChart();
  }
}

// 获取对话量趋势
async function fetchConversationTrend() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/conversation_trend');
  if (data && data.code === 200) {
    chartData.conversationTrend = data.data[0];
    updateConversationChart();
  }
}

// 初始化图表
function initCharts() {
  setTimeout(() => {
    updateUserChart();
    updateConversationChart();
  }, 100);
}

// 更新用户图表
function updateUserChart() {
  const userChart = echarts.init(document.getElementById('user-chart'));
  
  // 用户增长图表
  userChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: chartData.userGrowth.labels || ['一月', '二月', '三月', '四月', '五月', '六月', '七月'] 
    },
    yAxis: { type: 'value' },
    series: [{
      data: chartData.userGrowth.values || [120, 132, 101, 134, 90, 230, 210],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      color: '#1677ff'
    }]
  });
  
  window.addEventListener('resize', () => {
    userChart.resize();
  });
}

// 更新对话图表
function updateConversationChart() {
  const convChart = echarts.init(document.getElementById('conversation-chart'));
  
  // 对话趋势图表
  convChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: chartData.conversationTrend.labels || ['一月', '二月', '三月', '四月', '五月', '六月', '七月'] 
    },
    yAxis: { type: 'value' },
    series: [{
      data: chartData.conversationTrend.values || [220, 182, 191, 234, 290, 330, 310],
      type: 'bar',
      color: '#722ed1'
    }]
  });
  
  window.addEventListener('resize', () => {
    convChart.resize();
  });
}

onMounted(() => {
  fetchSystemInfo();
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
      <div class="header-actions">
        <el-button size="small" icon="Refresh" circle @click="fetchSystemInfo" />
        <el-switch
          v-model="isDarkMode"
          class="theme-switch"
          active-text="暗色"
          inactive-text="亮色"
          inline-prompt
        />
      </div>
    </div>

    <div class="admin-content">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="statistics-cards">
        <el-col :span="6" v-for="(stat, index) in [
          { label: '总用户数', value: statistics.totalUsers, icon: 'User', color: '#1677ff' },
          { label: '活跃用户', value: statistics.activeUsers, icon: 'UserFilled', color: '#52c41a' },
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
            <div class="stat-trend" v-if="index === 1">
              <el-icon :color="activeUserGrowth > 0 ? 'green' : 'red'">
                <component :is="activeUserGrowth > 0 ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
              <span :style="{ color: activeUserGrowth > 0 ? 'green' : 'red' }">{{ Math.abs(activeUserGrowth) }}%</span>
            </div>
            <div class="stat-trend" v-else>
              <el-icon color="green"><ArrowUp /></el-icon>
              <span>10%</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 数据趋势 -->
      <el-row :gutter="20" class="chart-section">
        <el-col :span="12">
          <div class="chart-card">
            <h3>用户增长趋势</h3>
            <div id="user-chart" class="chart"></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-card">
            <h3>对话数量变化</h3>
            <div id="conversation-chart" class="chart"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 系统状态和最近活动 -->
      <el-row :gutter="20" class="status-section">
        <el-col :span="8">
          <div class="system-status-card">
            <h3>系统状态</h3>
            <div class="status-content">
              <div class="status-item">
                <span>CPU 使用率</span>
                <el-progress :percentage="systemStatus.cpuUsage" :color="systemStatus.cpuUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
              <div class="status-item">
                <span>内存使用率</span>
                <el-progress :percentage="systemStatus.memoryUsage" :color="systemStatus.memoryUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
              <div class="status-item">
                <span>磁盘使用率</span>
                <el-progress :percentage="systemStatus.diskUsage" :color="systemStatus.diskUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
              <div class="status-overview">
                <el-tag :type="systemStatus.status === 'healthy' ? 'success' : systemStatus.status === 'warning' ? 'warning' : 'danger'">
                  {{ systemStatus.status === 'healthy' ? '系统正常' : systemStatus.status === 'warning' ? '系统警告' : '系统异常' }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="16">
          <div class="recent-activities-card">
            <h3>最近活动</h3>
            <div class="activities-content">
              <el-timeline>
                <el-timeline-item
                  v-for="activity in recentActivities"
                  :key="activity.id"
                  :type="activity.type === 'user' ? 'primary' : activity.type === 'conversation' ? 'success' : activity.type === 'knowledge' ? 'warning' : 'info'"
                  :size="'small'"
                  :timestamp="activity.time"
                >
                  {{ activity.username }} {{ activity.action }}
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 快捷入口 -->
      <div class="quick-access">
        <h2>管理入口</h2>
        <el-row :gutter="24">
          <el-col :md="8" :sm="12" :xs="24" v-for="(item, index) in [
            { title: '对话管理', desc: '查看所有用户对话记录', icon: 'ChatLineSquare', path: 'chat', color: '#1677ff' },
            { title: '知识库管理', desc: '管理用户知识库文档', icon: 'Collection', path: 'base', color: '#722ed1' },
            { title: '用户管理', desc: '管理所有用户', icon: 'Setting', path: 'user', color: '#13c2c2' }
          ]" :key="index">
            <div class="access-card" @click="navigateTo(item.path)" :style="{ '--card-color': item.color }">
              <div class="card-icon">
                <el-icon :size="32"><component :is="item.icon" /></el-icon>
              </div>
              <div class="card-content">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
              <div class="card-action">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  background: var(--bg-color, #f5f7fa);
  min-height: 100vh;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-y: hidden;
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
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color, #eaeaea);
  flex-shrink: 0;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
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

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.statistics-cards {
  margin-bottom: 24px;
}

.stat-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color, #eaeaea);
  height: 100%;

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
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color, #1a1a1a);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #52c41a;
}

.chart-section {
  margin-bottom: 24px;
}

.chart-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color, #eaeaea);
  height: 100%;
  
  h3 {
    margin-top: 0;
    margin-bottom: 16px;
    font-size: 16px;
    color: var(--text-color, #1a1a1a);
    font-weight: 500;
  }
}

.chart {
  height: 280px;
  width: 100%;
}

.status-section {
  margin-bottom: 24px;
}

.system-status-card, .recent-activities-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color, #eaeaea);
  height: 100%;
  min-height: 360px;
  display: flex;
  flex-direction: column;
}

.status-content, .activities-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.status-item {
  margin-bottom: 16px;
  span {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: var(--text-secondary, #666);
  }
}

.status-overview {
  margin-top: 24px;
  text-align: center;
}

.quick-access {
  margin-top: 50px;
  margin-bottom: 24px;
  
  h2 {
    font-size: 20px;
    margin-bottom: 16px;
    color: var(--text-color, #1a1a1a);
  }
}

.access-card {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s;
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
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--card-color) 15%, transparent);
  border-radius: 12px;
  color: var(--card-color);
  flex-shrink: 0;
}

.card-content {
  margin-left: 16px;
  flex: 1;
  
  h3 {
    font-size: 18px;
    margin: 0 0 8px;
    color: var(--text-color, #1a1a1a);
  }

  p {
    font-size: 14px;
    color: var(--text-secondary, #666);
    margin: 0;
    line-height: 1.5;
  }
}

.card-action {
  color: var(--card-color);
  margin-left: 12px;
}

/* 自适应样式 */
@media (max-width: 1200px) {
  .chart-section .el-col {
    width: 100%;
  }
  
  .status-section .el-col {
    width: 100%;
  }
  
  .system-status-card, .recent-activities-card {
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .admin-content {
    padding: 16px;
  }

  .statistics-cards .el-col {
    width: 100%;
    margin-bottom: 16px;
  }
  
  .chart {
    height: 220px;
  }
  
  .quick-access h2 {
    font-size: 18px;
  }
}
</style>
