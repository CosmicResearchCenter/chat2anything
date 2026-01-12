<script setup lang="ts">
import { ref, onMounted, reactive, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getRequest } from '@/utils/http'
import * as echarts from 'echarts'
import {
  User,
  ChatLineRound,
  Collection,
  Cpu,
  Clock,
  UserFilled,
  Refresh,
  ArrowUp,
  ArrowDown,
  Platform,
  Ticket,
  Setting,
  ChatLineSquare,
  ArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()

// 统计数据
const statistics = ref({
  totalUsers: 0,
  totalConversations: 0,
  totalKnowledgeBases: 0,
  activeUsers: 0
})

// 活跃用户增长率
const activeUserGrowth = ref(0)

// 系统状态
const systemStatus = ref({
  cpuUsage: 0,
  memoryUsage: 0,
  diskUsage: 0,
  status: 'healthy'
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

// 活动类型接口
interface Activity {
  id: number | string;
  type: 'user' | 'conversation' | 'knowledge' | string;
  username: string;
  action: string;
  time: string;
}

// 最近活动
const recentActivities = ref<Activity[]>([])

// 图表实例
let userChart: echarts.ECharts | null = null
let conversationChart: echarts.ECharts | null = null

// 快捷入口配置
const quickAccess = [
  { title: '模型配置管理', desc: 'LLM/Embedding/Rerank', icon: Platform, path: 'models', color: 'var(--info-500)' },
  { title: '对话管理', desc: '查看用户对话', icon: ChatLineSquare, path: 'chat', color: 'var(--primary-500)' },
  { title: '知识库管理', desc: '用户知识库文档', icon: Collection, path: 'base', color: 'var(--purple-500)' },
  { title: '用户管理', desc: '管理所有用户', icon: Setting, path: 'user', color: 'var(--success-500)' },
  { title: '邀请码管理', desc: '生成和管理邀请码', icon: Ticket, path: 'invite', color: 'var(--warning-500)' }
]

// 获取系统信息
async function fetchSystemInfo() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/system_info');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      const systemInfo = data.data[0];
      statistics.value.totalUsers = systemInfo.user_count || 0;
      statistics.value.totalConversations = systemInfo.conversation_count || 0;
      statistics.value.totalKnowledgeBases = systemInfo.knowledge_base_count || 0;

      // 获取系统资源使用情况
      await fetchSystemResources();

      // 获取活跃用户统计
      await fetchActiveUsers();

      // 初始化图表
      await fetchUserGrowth();
      await fetchConversationTrend();

      // 获取最近活动
      await fetchRecentActivities();
    }
  } catch (error) {
    console.error('获取系统信息失败:', error);
  }
}

// 获取系统资源使用情况
async function fetchSystemResources() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/system_resources');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      const resources = data.data[0];
      systemStatus.value = {
        cpuUsage: resources.cpu_usage || 0,
        memoryUsage: resources.memory_usage || 0,
        diskUsage: resources.disk_usage || 0,
        status: resources.status || 'healthy'
      };
    }
  } catch (error) {
    console.error('获取系统资源失败:', error);
  }
}

// 获取活跃用户统计
async function fetchActiveUsers() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/active_users');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      const activeUserData = data.data[0];
      statistics.value.activeUsers = activeUserData.active_users || 0;
      activeUserGrowth.value = activeUserData.growth_rate || 0;
    }
  } catch (error) {
    console.error('获取活跃用户失败:', error);
  }
}

// 获取最近活动
async function fetchRecentActivities() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/recent_activities');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      recentActivities.value = data.data[0];
    }
  } catch (error) {
    console.error('获取最近活动失败:', error);
  }
}

// 获取用户增长趋势
async function fetchUserGrowth() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/user_growth');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      chartData.userGrowth = data.data[0];
      setTimeout(() => updateUserChart(), 100);
    }
  } catch (error) {
    console.error('获取用户增长失败:', error);
  }
}

// 获取对话量趋势
async function fetchConversationTrend() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/admin/conversation_trend');
    if (data && data.code === 200 && data.data && data.data.length > 0) {
      chartData.conversationTrend = data.data[0];
      setTimeout(() => updateConversationChart(), 100);
    }
  } catch (error) {
    console.error('获取对话趋势失败:', error);
  }
}

// 更新用户图表
function updateUserChart() {
  const element = document.getElementById('user-chart');
  if (!element) return;

  // 销毁旧实例
  if (userChart) {
    userChart.dispose();
  }

  userChart = echarts.init(element, document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : null);

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

  // 从 CSS 变量获取颜色
  const getVar = (name: string) => {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  };

  const textColor = getVar('--text-primary');
  const textSecondary = getVar('--text-secondary');
  const borderColor = getVar('--border-light');
  const splitColor = getVar('--border-light');
  const primaryColor = getVar('--primary-500') || '#3a7afe';
  const primaryColorLight = isDark ? 'rgba(58, 122, 254, 0.3)' : 'rgba(58, 122, 254, 0.15)';
  const primaryColorLighter = isDark ? 'rgba(58, 122, 254, 0.1)' : 'rgba(58, 122, 254, 0.05)';

  userChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: getVar('--bg-card'),
      borderColor: borderColor,
      textStyle: { color: textColor }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: chartData.userGrowth.labels || ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
      axisLine: { lineStyle: { color: borderColor } },
      axisLabel: { color: textSecondary }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: borderColor } },
      axisLabel: { color: textSecondary },
      splitLine: { lineStyle: { color: splitColor } }
    },
    series: [{
      data: chartData.userGrowth.values || [120, 132, 101, 134, 90, 230, 210],
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3,
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: primaryColorLight },
          { offset: 1, color: primaryColorLighter }
        ])
      },
      lineStyle: { color: primaryColor, width: 3 },
      itemStyle: { color: primaryColor },
      symbol: 'circle',
      symbolSize: 6
    }]
  });
}

// 更新对话图表
function updateConversationChart() {
  const element = document.getElementById('conversation-chart');
  if (!element) return;

  // 销毁旧实例
  if (conversationChart) {
    conversationChart.dispose();
  }

  conversationChart = echarts.init(element, document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : null);

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

  // 从 CSS 变量获取颜色
  const getVar = (name: string) => {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  };

  const textColor = getVar('--text-primary');
  const textSecondary = getVar('--text-secondary');
  const borderColor = getVar('--border-light');
  const splitColor = getVar('--border-light');
  const purpleColor = getVar('--purple-500') || '#722ed1';
  const purpleColorLight = isDark ? 'rgba(114, 46, 209, 0.3)' : 'rgba(114, 46, 209, 0.15)';
  const purpleColorLighter = isDark ? 'rgba(114, 46, 209, 0.1)' : 'rgba(114, 46, 209, 0.05)';
  const bgCard = getVar('--bg-card');

  conversationChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: bgCard,
      borderColor: borderColor,
      textStyle: { color: textColor }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: chartData.conversationTrend.labels || ['一月', '二月', '三月', '四月', '五月', '六月', '七月'],
      axisLine: { lineStyle: { color: borderColor } },
      axisLabel: { color: textSecondary }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: borderColor } },
      axisLabel: { color: textSecondary },
      splitLine: { lineStyle: { color: splitColor } }
    },
    series: [{
      data: chartData.conversationTrend.values || [220, 182, 191, 234, 290, 330, 310],
      type: 'bar',
      barWidth: '60%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: purpleColorLight },
          { offset: 1, color: purpleColorLighter }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  });
}

// 导航处理
const navigateTo = (path: string) => {
  router.push(`/admin/${path}`)
}

// 刷新数据
const refreshData = () => {
  fetchSystemInfo()
}

// 处理窗口大小变化
const handleResize = () => {
  setTimeout(() => {
    if (userChart) userChart.resize()
    if (conversationChart) conversationChart.resize()
  }, 100)
}

// 页面挂载
onMounted(() => {
  fetchSystemInfo()
  window.addEventListener('resize', handleResize)
})

// 页面卸载前清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (userChart) {
    userChart.dispose()
    userChart = null
  }
  if (conversationChart) {
    conversationChart.dispose()
    conversationChart = null
  }
})

// 深色模式支持
const isDarkMode = ref(false)
watch(
  () => isDarkMode.value,
  (val: boolean) => {
    document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light')
    setTimeout(() => {
      updateUserChart()
      updateConversationChart()
    }, 100)
  }
)
</script>

<template>
  <div class="admin-dashboard">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">管理控制台</h1>
          <p class="page-subtitle">系统监控 · 数据分析 · 运维管理</p>
        </div>
        <div class="header-actions">
          <el-tooltip content="刷新数据" placement="bottom">
            <el-button
              type="primary"
              :icon="Refresh"
              circle
              @click="refreshData"
              class="refresh-btn"
            />
          </el-tooltip>
          <el-switch
            v-model="isDarkMode"
            class="theme-switch"
            active-text="暗色"
            inactive-text="亮色"
            inline-prompt
          />
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <!-- 快捷入口 - 现代化卡片网格 -->
      <section class="quick-access-section">
        <h2 class="section-title">
          <el-icon><Setting /></el-icon>
          快速入口
        </h2>
        <div class="quick-access-grid">
          <div
            v-for="(item, idx) in quickAccess"
            :key="idx"
            class="access-card"
            :style="{ '--card-color': item.color }"
            @click="navigateTo(item.path)"
          >
            <div class="access-icon-wrapper">
              <el-icon :size="28"><component :is="item.icon" /></el-icon>
            </div>
            <div class="access-content">
              <div class="access-title">{{ item.title }}</div>
              <div class="access-desc">{{ item.desc }}</div>
            </div>
            <el-icon class="access-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </section>

      <!-- 统计数据卡片 -->
      <section class="stats-section">
        <h2 class="section-title">
          <el-icon><User /></el-icon>
          核心数据
        </h2>
        <div class="stats-grid">
          <div
            class="stat-card"
            v-for="(stat, idx) in [
              { label: '总用户', value: statistics.totalUsers, icon: User, color: '#1677ff' },
              { label: '活跃用户', value: statistics.activeUsers, icon: UserFilled, color: '#52c41a', trend: activeUserGrowth },
              { label: '总对话', value: statistics.totalConversations, icon: ChatLineRound, color: '#722ed1' },
              { label: '知识库', value: statistics.totalKnowledgeBases, icon: Collection, color: '#13c2c2' }
            ]"
            :key="idx"
            :style="{ '--stat-color': stat.color }"
          >
            <div class="stat-icon-wrapper">
              <el-icon :size="32"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-details">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-trend" v-if="stat.trend !== undefined">
              <el-icon :color="stat.trend > 0 ? 'var(--success-500)' : 'var(--danger-500)'">
                <component :is="stat.trend > 0 ? ArrowUp : ArrowDown" />
              </el-icon>
              <span :class="stat.trend > 0 ? 'trend-up' : 'trend-down'">{{ Math.abs(stat.trend) }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 图表区域 -->
      <section class="charts-section">
        <h2 class="section-title">
          <el-icon><Cpu /></el-icon>
          数据趋势
        </h2>
        <div class="charts-grid">
          <div class="chart-card">
            <div class="chart-header">
              <el-icon><User /></el-icon>
              <span>用户增长趋势</span>
            </div>
            <div id="user-chart" class="chart-canvas"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <el-icon><ChatLineRound /></el-icon>
              <span>对话数量变化</span>
            </div>
            <div id="conversation-chart" class="chart-canvas"></div>
          </div>
        </div>
      </section>

      <!-- 系统状态与活动 -->
      <section class="system-section">
        <div class="system-status-card">
          <div class="card-header">
            <el-icon><Cpu /></el-icon>
            <span>系统资源</span>
          </div>
          <div class="resource-list">
            <div class="resource-item">
              <div class="resource-info">
                <span class="resource-name">CPU 使用率</span>
                <span class="resource-value">{{ systemStatus.cpuUsage }}%</span>
              </div>
              <el-progress
                :percentage="systemStatus.cpuUsage"
                :color="systemStatus.cpuUsage > 80 ? 'var(--danger-500)' : 'var(--info-500)'"
                :stroke-width="8"
                striped
              />
            </div>
            <div class="resource-item">
              <div class="resource-info">
                <span class="resource-name">内存使用率</span>
                <span class="resource-value">{{ systemStatus.memoryUsage }}%</span>
              </div>
              <el-progress
                :percentage="systemStatus.memoryUsage"
                :color="systemStatus.memoryUsage > 80 ? 'var(--danger-500)' : 'var(--info-500)'"
                :stroke-width="8"
                striped
              />
            </div>
            <div class="resource-item">
              <div class="resource-info">
                <span class="resource-name">磁盘使用率</span>
                <span class="resource-value">{{ systemStatus.diskUsage }}%</span>
              </div>
              <el-progress
                :percentage="systemStatus.diskUsage"
                :color="systemStatus.diskUsage > 80 ? 'var(--danger-500)' : 'var(--info-500)'"
                :stroke-width="8"
                striped
              />
            </div>
          </div>
          <div class="system-status-badge">
            <el-tag
              :type="systemStatus.status === 'healthy' ? 'success' : systemStatus.status === 'warning' ? 'warning' : 'danger'"
              size="large"
              effect="dark"
            >
              {{ systemStatus.status === 'healthy' ? '🟢 系统正常' : systemStatus.status === 'warning' ? '🟡 系统警告' : '🔴 系统异常' }}
            </el-tag>
          </div>
        </div>

        <div class="recent-activities-card">
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>最近活动</span>
          </div>
          <div class="activities-list">
            <el-timeline v-if="recentActivities.length > 0">
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :type="activity.type === 'user' ? 'primary' : activity.type === 'conversation' ? 'success' : activity.type === 'knowledge' ? 'warning' : 'info'"
                :size="'large'"
                :timestamp="activity.time"
                placement="top"
              >
                <div class="activity-item">
                  <span class="activity-username">{{ activity.username }}</span>
                  <span class="activity-action">{{ activity.action }}</span>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无活动记录" :image-size="80" />
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 管理控制台主容器 */
.admin-dashboard {
  width: 100%;
  min-height: 100%;
  background: var(--bg-main);
  padding: 0;
  color: var(--text-primary);
}

/* 页面头部 */
.page-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  padding: 24px 32px;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.header-content {
  max-width: var(--content-max-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.title-section {
  flex: 1;
  min-width: 280px;
}

.page-title {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 6px 0;
  line-height: 1.3;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.refresh-btn {
  background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
  border: none;
  box-shadow: 0 4px 12px rgba(2, 69, 163, 0.25);
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(2, 69, 163, 0.35);
}

.theme-switch {
  margin-left: 8px;
}

/* 主内容区域 */
.dashboard-main {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 通用标题样式 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-light);
}

.section-title .el-icon {
  color: var(--primary-600);
}

/* 快捷入口区域 */
.quick-access-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.access-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: color-mix(in srgb, var(--card-color) 7%, var(--bg-card));
  border: 1px solid color-mix(in srgb, var(--card-color) 20%, var(--border-light));
  border-radius: var(--radius-md);
  padding: 16px 18px;
  cursor: pointer;
  transition: all var(--duration-normal) ease;
  position: relative;
  overflow: hidden;
}

.access-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--card-color);
  transform: scaleY(0);
  transition: transform var(--duration-normal) ease;
}

.access-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px color-mix(in srgb, var(--card-color) 15%, transparent);
  border-color: var(--card-color);
}

.access-card:hover::before {
  transform: scaleY(1);
}

.access-icon-wrapper {
  width: 48px;
  height: 48px;
  background: color-mix(in srgb, var(--card-color) 15%, transparent);
  color: var(--card-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--duration-normal) ease;
}

.access-card:hover .access-icon-wrapper {
  background: var(--card-color);
  color: white;
  transform: scale(1.05);
}

.access-content {
  flex: 1;
  min-width: 0;
}

.access-title {
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.access-desc {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.access-arrow {
  color: var(--card-color);
  opacity: 0;
  transform: translateX(-8px);
  transition: all var(--duration-normal) ease;
}

.access-card:hover .access-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* 统计数据区域 */
.stats-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  position: relative;
  overflow: hidden;
  transition: all var(--duration-normal) ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--stat-color), transparent);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--stat-color);
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  background: color-mix(in srgb, var(--stat-color) 12%, transparent);
  color: var(--stat-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-details {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
}

.trend-up {
  color: var(--success-500);
}

.trend-down {
  color: var(--danger-500);
}

/* 图表区域 */
.charts-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.chart-card {
  background: var(--bg-main);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.chart-header .el-icon {
  color: var(--primary-600);
}

.chart-canvas {
  height: 280px;
  width: 100%;
  border-radius: var(--radius-sm);
  background: var(--bg-card);
}

/* 系统状态与活动区域 */
.system-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.system-status-card,
.recent-activities-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.card-header .el-icon {
  color: var(--primary-600);
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.resource-name {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.resource-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: var(--font-weight-bold);
}

.system-status-badge {
  display: flex;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);
}

.activities-list {
  flex: 1;
  overflow-y: auto;
  max-height: 320px;
  padding-right: 4px;
}

.activity-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  background: var(--bg-main);
  border-radius: var(--radius-sm);
  margin-top: 8px;
}

.activity-username {
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  font-size: 14px;
}

.activity-action {
  color: var(--text-secondary);
  font-size: 13px;
}

/* 滚动条美化 */
.activities-list::-webkit-scrollbar {
  width: 6px;
}

.activities-list::-webkit-scrollbar-track {
  background: transparent;
}

.activities-list::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 3px;
}

.activities-list::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-main {
    padding: 24px;
  }

  .page-header {
    padding: 20px 24px;
  }

  .quick-access-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .dashboard-main {
    padding: 16px;
    gap: 24px;
  }

  .page-header {
    padding: 16px 20px;
  }

  .page-title {
    font-size: 24px;
  }

  .section-title {
    font-size: 16px;
  }

  .quick-access-grid,
  .stats-grid,
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .system-section {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .chart-canvas {
    height: 220px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .dashboard-main {
    padding: 12px;
  }

  .page-header {
    padding: 12px 16px;
  }

  .stat-card,
  .chart-card,
  .system-status-card,
  .recent-activities-card {
    padding: 16px;
  }

  .access-card {
    padding: 12px;
    gap: 10px;
  }

  .access-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .section-title {
    font-size: 15px;
    margin-bottom: 12px;
  }
}

/* 深色模式适配 */
[data-theme="dark"] .page-header {
  background: rgba(26, 31, 38, 0.95);
  border-bottom-color: var(--border-light);
}

[data-theme="dark"] .quick-access-section,
[data-theme="dark"] .stats-section,
[data-theme="dark"] .charts-section,
[data-theme="dark"] .system-status-card,
[data-theme="dark"] .recent-activities-card {
  background: var(--bg-card);
  border-color: var(--border-light);
}

[data-theme="dark"] .access-card {
  background: color-mix(in srgb, var(--card-color) 10%, var(--bg-card));
}

[data-theme="dark"] .chart-card {
  background: var(--bg-main);
}

[data-theme="dark"] .activity-item {
  background: var(--bg-elevated);
}

/* 动画效果 */
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quick-access-grid .access-card,
.stats-grid .stat-card,
.charts-grid .chart-card {
  animation: cardAppear 0.4s ease forwards;
}

.quick-access-grid .access-card:nth-child(1) { animation-delay: 0.05s; }
.quick-access-grid .access-card:nth-child(2) { animation-delay: 0.1s; }
.quick-access-grid .access-card:nth-child(3) { animation-delay: 0.15s; }
.quick-access-grid .access-card:nth-child(4) { animation-delay: 0.2s; }
.quick-access-grid .access-card:nth-child(5) { animation-delay: 0.25s; }

/* 微交互 */
@media (hover: hover) {
  .access-card:active,
  .stat-card:active {
    transform: scale(0.98);
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .access-card,
  .stat-card,
  .chart-card,
  .system-status-card,
  .recent-activities-card {
    border-width: 2px;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .access-card,
  .stat-card,
  .chart-card,
  .access-icon-wrapper,
  .stat-icon-wrapper {
    animation: none !important;
    transition: none !important;
  }
}
</style>
