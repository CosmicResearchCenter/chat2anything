<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
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

// 主题切换时动态切换 ECharts 主题
watch(
  () => isDarkMode.value,
  (val) => {
    setTimeout(() => {
      updateUserChart()
      updateConversationChart()
    }, 200)
    document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light')
  }
)
</script>

<template>
  <div class="admin-dashboard" :class="{ 'dark-mode': isDarkMode }">
    <!-- 顶部栏 -->
    <header class="dashboard-header">
      <div class="dashboard-title">
        <!-- <img src="/logo.svg" alt="logo" class="logo" /> -->
        <div>
          <h1>AI 管理控制台</h1>
          <span>智能助手 · 数据洞察 · 高效管理</span>
        </div>
      </div>
      <div class="dashboard-actions">
        <el-tooltip content="刷新数据" placement="bottom">
          <el-button size="small" icon="Refresh" circle @click="fetchSystemInfo" />
        </el-tooltip>
        <el-switch
          v-model="isDarkMode"
          class="theme-switch"
          active-text="暗色"
          inactive-text="亮色"
          inline-prompt
        />
      </div>
    </header>

    <main class="dashboard-main with-sidebar">
      <!-- 左侧快捷入口栏 -->
      <aside class="dashboard-sidebar">
        <h2>管理入口</h2>
        <nav class="sidebar-access-list">
          <div
            class="sidebar-access-card"
            v-for="(item, idx) in [
              { title: '对话管理', desc: '查看所有用户对话记录', icon: 'ChatLineSquare', path: 'chat', color: '#1677ff' },
              { title: '知识库管理', desc: '管理用户知识库文档', icon: 'Collection', path: 'base', color: '#722ed1' },
              { title: '用户管理', desc: '管理所有用户', icon: 'Setting', path: 'user', color: '#13c2c2' }
            ]"
            :key="idx"
            @click="navigateTo(item.path)"
            :style="{ '--access-color': item.color }"
          >
            <div class="sidebar-access-icon">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
            </div>
            <div class="sidebar-access-content">
              <span class="sidebar-access-title">{{ item.title }}</span>
              <span class="sidebar-access-desc">{{ item.desc }}</span>
            </div>
            <div class="sidebar-access-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </nav>
      </aside>

      <!-- 右侧主内容 -->
      <section class="dashboard-content">
        <!-- 统计卡片 -->
        <section class="dashboard-stats">
          <div
            class="stat-card"
            v-for="(stat, idx) in [
              { label: '总用户', value: statistics.totalUsers, icon: 'User', color: '#1677ff' },
              { label: '活跃用户', value: statistics.activeUsers, icon: 'UserFilled', color: '#52c41a', trend: activeUserGrowth },
              { label: '总对话', value: statistics.totalConversations, icon: 'ChatLineRound', color: '#722ed1' },
              { label: '知识库', value: statistics.totalKnowledgeBases, icon: 'Collection', color: '#13c2c2' }
            ]"
            :key="idx"
            :style="{ '--stat-color': stat.color }"
          >
            <div class="stat-icon">
              <el-icon :size="28"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-trend" v-if="stat.trend !== undefined">
              <el-icon :color="stat.trend > 0 ? '#52c41a' : '#f56c6c'">
                <component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
              <span :style="{ color: stat.trend > 0 ? '#52c41a' : '#f56c6c' }">{{ Math.abs(stat.trend) }}%</span>
            </div>
          </div>
        </section>
        <!-- 图表区 -->
        <section class="dashboard-charts">
          <div class="chart-card">
            <div class="chart-title">
              <el-icon><User /></el-icon>
              <span>用户增长趋势</span>
            </div>
            <div id="user-chart" class="chart"></div>
          </div>
          <div class="chart-card">
            <div class="chart-title">
              <el-icon><ChatLineRound /></el-icon>
              <span>对话数量变化</span>
            </div>
            <div id="conversation-chart" class="chart"></div>
          </div>
        </section>
        <!-- 系统状态 & 最近活动 -->
        <section class="dashboard-status-activity">
          <div class="system-status-card">
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>系统状态</span>
            </div>
            <div class="status-list">
              <div class="status-item">
                <span>CPU</span>
                <el-progress :percentage="systemStatus.cpuUsage" :color="systemStatus.cpuUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
              <div class="status-item">
                <span>内存</span>
                <el-progress :percentage="systemStatus.memoryUsage" :color="systemStatus.memoryUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
              <div class="status-item">
                <span>磁盘</span>
                <el-progress :percentage="systemStatus.diskUsage" :color="systemStatus.diskUsage > 80 ? '#f56c6c' : '#13c2c2'" />
              </div>
            </div>
            <div class="status-overview">
              <el-tag :type="systemStatus.status === 'healthy' ? 'success' : systemStatus.status === 'warning' ? 'warning' : 'danger'">
                {{ systemStatus.status === 'healthy' ? '系统正常' : systemStatus.status === 'warning' ? '系统警告' : '系统异常' }}
              </el-tag>
            </div>
          </div>
          <div class="recent-activities-card">
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最近活动</span>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :type="activity.type === 'user' ? 'primary' : activity.type === 'conversation' ? 'success' : activity.type === 'knowledge' ? 'warning' : 'info'"
                :size="'small'"
                :timestamp="activity.time"
              >
                <span class="activity-user">{{ activity.username }}</span>
                <span class="activity-action">{{ activity.action }}</span>
              </el-timeline-item>
            </el-timeline>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin-dashboard {
  --bg: #f7faff;
  --card-bg: #fff;
  --text: #222;
  --text-secondary: #888;
  --border: #e6eaf0;
  --shadow: 0 4px 24px 0 rgba(22, 119, 255, 0.06);
  --radius: 18px;
  background: var(--bg);
  min-height: 100vh;
  color: var(--text);
  transition: background 0.3s, color 0.3s;
}
.admin-dashboard.dark-mode {
  --bg: #10131a;
  --card-bg: #181c23;
  --text: #f3f6fa;
  --text-secondary: #7e8ba3;
  --border: #23273a;
  --shadow: 0 4px 24px 0 rgba(22, 119, 255, 0.10);
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 40px 0 40px;
  background: transparent;
}
.dashboard-title {
  display: flex;
  align-items: center;
  gap: 18px;
}
.dashboard-title .logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(22,119,255,0.08);
}
.dashboard-title h1 {
  font-size: 2.1rem;
  font-weight: 700;
  margin: 0;
  color: var(--text);
  letter-spacing: 1px;
}
.dashboard-title span {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-top: 2px;
  display: block;
}
.dashboard-actions {
  display: flex;
  align-items: center;
  gap: 18px;
}
.theme-switch {
  margin-left: 8px;
}
.dashboard-main {
  padding: 24px 40px 40px 40px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  /* overflow-y: scroll; */
}
.dashboard-main.with-sidebar {
  display: flex;
  flex-direction: row;
  gap: 32px;
  padding: 24px 40px 40px 40px;
}
.dashboard-sidebar {
  width: 230px;
  min-width: 180px;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 24px 0 24px 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  margin-right: 32px;
  height: fit-content;
}
.dashboard-sidebar h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 18px 32px;
  letter-spacing: 1px;
}
.sidebar-access-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 12px;
}
.sidebar-access-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: color-mix(in srgb, var(--access-color) 7%, var(--card-bg));
  border-radius: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
  border: 1px solid transparent;
  position: relative;
}
.sidebar-access-card:hover {
  background: color-mix(in srgb, var(--access-color) 18%, var(--card-bg));
  box-shadow: 0 4px 16px 0 color-mix(in srgb, var(--access-color) 18%, transparent);
  border-color: var(--access-color);
  transform: translateY(-2px) scale(1.01);
}
.sidebar-access-icon {
  background: color-mix(in srgb, var(--access-color) 16%, transparent);
  color: var(--access-color);
  border-radius: 8px;
  width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}
.sidebar-access-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.sidebar-access-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 2px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.sidebar-access-desc {
  font-size: 0.92rem;
  color: var(--text-secondary);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.sidebar-access-arrow {
  color: var(--access-color);
  margin-left: 6px;
  font-size: 1.1rem;
}

/* 主内容区域 */
.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-width: 0;
}

/* 隐藏原右侧快捷入口 */
.dashboard-quick-access {
  display: none !important;
}
.dashboard-stats {
  display: flex;
  gap: 28px;
  margin-bottom: 8px;
}
.stat-card {
  flex: 1;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 28px 24px;
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}
.stat-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, var(--stat-color), #fff0 80%);
}
.stat-card:hover {
  box-shadow: 0 8px 32px 0 rgba(22,119,255,0.13);
  transform: translateY(-2px) scale(1.01);
}
.stat-icon {
  background: color-mix(in srgb, var(--stat-color) 18%, transparent);
  color: var(--stat-color);
  border-radius: 12px;
  width: 54px; height: 54px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 2.1rem;
  font-weight: 700;
  color: var(--text);
}
.stat-label {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-top: 2px;
}
.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 1rem;
  font-weight: 500;
}
.dashboard-charts {
  display: flex;
  gap: 28px;
}
.chart-card {
  flex: 1;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px 22px 18px 22px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 10px;
}
.chart {
  height: 260px;
  width: 100%;
}
.dashboard-status-activity {
  display: flex;
  gap: 28px;
}
.system-status-card, .recent-activities-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 24px 22px 18px 22px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.system-status-card {
  flex: 1.1;
  min-width: 260px;
  margin-right: 0;
}
.recent-activities-card {
  flex: 2;
  min-width: 0;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 12px;
}
.status-list {
  margin-bottom: 18px;
}
.status-item {
  margin-bottom: 14px;
}
.status-item span {
  font-size: 0.98rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: block;
}
.status-overview {
  margin-top: 18px;
  text-align: center;
}
.activity-user {
  color: var(--text);
  font-weight: 500;
}
.activity-action {
  color: var(--text-secondary);
  margin-left: 6px;
}
.dashboard-quick-access {
  margin-top: 18px;
}
.dashboard-quick-access h2 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 18px;
  letter-spacing: 1px;
}
.quick-access-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 28px;
  width: 100%;
  /* 让卡片自动换行，避免溢出 */
}
.access-card {
  flex: 1;
  min-width: 0;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 22px 18px;
  cursor: pointer;
  position: relative;
  transition: box-shadow 0.2s, transform 0.2s;
  overflow: hidden;
}
.access-card:hover {
  box-shadow: 0 8px 32px 0 color-mix(in srgb, var(--access-color) 30%, transparent);
  transform: translateY(-2px) scale(1.02);
}
.access-card::after {
  content: '';
  position: absolute;
  left: 0; bottom: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--access-color), #fff0 80%);
  transition: transform 0.3s;
  transform: scaleX(0);
}
.access-card:hover::after {
  transform: scaleX(1);
}
.access-icon {
  background: color-mix(in srgb, var(--access-color) 16%, transparent);
  color: var(--access-color);
  border-radius: 10px;
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
}
.access-content {
  flex: 1;
  margin-left: 10px;
}
.access-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--text);
}
.access-content p {
  font-size: 0.98rem;
  color: var (--text-secondary);
  margin: 0;
}
.access-arrow {
  color: var(--access-color);
  margin-left: 8px;
  font-size: 1.3rem;
}

/* 响应式优化 */
@media (max-width: 1200px) {
  .dashboard-main { padding: 18px 10px 24px 10px; }
  .dashboard-header { padding: 24px 10px 0 10px; }
  .dashboard-stats, .dashboard-charts, .dashboard-status-activity { gap: 14px; }
  .quick-access-list { gap: 14px; }
}
@media (max-width: 900px) {
  .dashboard-stats, .dashboard-charts, .dashboard-status-activity {
    flex-direction: column;
  }
  .stat-card, .chart-card, .system-status-card, .recent-activities-card {
    width: 100%;
    min-width: 0;
  }
  .quick-access-list {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}
@media (max-width: 600px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .dashboard-title { gap: 10px; }
  .dashboard-main { padding: 8px 2vw 16px 2vw; gap: 18px; }
  .stat-card, .chart-card, .system-status-card, .recent-activities-card, .access-card { padding: 14px 8px; }
  .chart { height: 180px; }
  .quick-access-list {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
@media (max-width: 1200px) {
  .dashboard-main.with-sidebar { gap: 16px; padding: 18px 10px 24px 10px; }
  .dashboard-header { padding: 24px 10px 0 10px; }
  .dashboard-sidebar { margin-right: 16px; }
}
@media (max-width: 900px) {
  .dashboard-main.with-sidebar {
    flex-direction: column;
    gap: 0;
  }
  .dashboard-sidebar {
    width: 100%;
    min-width: 0;
    margin-right: 0;
    margin-bottom: 18px;
    flex-direction: row;
    padding: 14px 0;
    justify-content: flex-start;
    align-items: flex-start;
    overflow-x: auto;
  }
  .sidebar-access-list {
    flex-direction: row;
    gap: 10px;
    padding: 0 8px;
    width: 100%;
  }
  .sidebar-access-card {
    min-width: 180px;
    padding: 10px 10px;
  }
}
@media (max-width: 600px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .dashboard-title { gap: 10px; }
  .dashboard-main.with-sidebar { padding: 8px 2vw 16px 2vw; }
  .dashboard-sidebar { padding: 8px 0; }
  .sidebar-access-list { gap: 6px; }
  .sidebar-access-card { min-width: 120px; padding: 8px 6px; }
  .dashboard-content { gap: 18px; }
}
</style>
