<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { ChatDotRound, Folder, Setting, User, Menu, Moon, Sunny, ChatLineRound, Collection, Ticket } from '@element-plus/icons-vue'
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { applyTheme, getInitialTheme } from './utils/theme'

// 管理员状态响应式变量
const isAdmin = ref(false)
const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const darkMode = ref(false)

// 检查用户是否为管理员
async function checkIsAdmin() {
  const token = localStorage.getItem('token')
  if (!token) {
    isAdmin.value = false
    return
  }

  const baseURL = import.meta.env.VITE_APP_BASE_URL
  try {
    const response = await fetch(`${baseURL}/v1/api/mark/admin/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    isAdmin.value = response.ok
  } catch (error) {
    console.error('Error checking admin status:', error)
    isAdmin.value = false
  }
}

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

// 切换暗色模式
const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  applyTheme(darkMode.value ? 'dark' : 'light')
}

// 导航菜单项
const menuItems = computed(() => {
  const items = [
    {
      path: '/',
      icon: ChatDotRound,
      label: '智能问答',
      color: 'var(--primary-500)'
    },
    {
      path: '/manager',
      icon: Folder,
      label: '知识库',
      color: 'var(--purple-500)'
    }
  ]

  if (isAdmin.value) {
    items.push({
      path: '/admin',
      icon: User,
      label: '后台管理',
      color: 'var(--warning-500)'
    })
  }

  return items
})

// 处理导航点击
const handleNavigate = (path: string) => {
  router.push(path)
}

// 组件挂载时检查管理员状态和主题
onMounted(async () => {
  await checkIsAdmin()

  const initialTheme = getInitialTheme()
  darkMode.value = initialTheme === 'dark'
  applyTheme(initialTheme)
})

// 监听路由变化，重新检查管理员状态
watch(
  () => route.path,
  async () => {
    await checkIsAdmin()
  }
)
</script>

<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': collapsed }">
    <!-- 侧边栏 -->
    <aside class="sidebar glass" :class="{ 'collapsed': collapsed }">
      <!-- Logo区域 -->
      <div class="sidebar-header">
        <div class="logo" v-if="!collapsed">
          <span class="logo-text">Chat2Anything</span>
        </div>
        <button class="collapse-btn" @click="toggleSidebar" title="折叠/展开">
          <el-icon><Menu /></el-icon>
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="nav-item"
          :class="{ 'active': route.path === item.path }"
          @click="handleNavigate(item.path)"
          :style="{ '--item-color': item.color }"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span class="nav-label" v-if="!collapsed">{{ item.label }}</span>
        </div>
      </nav>

      <!-- 底部工具栏 -->
      <div class="sidebar-footer">
        <div class="theme-toggle" @click="toggleDarkMode" title="切换主题">
          <el-icon v-if="!darkMode"><Moon /></el-icon>
          <el-icon v-else><Sunny /></el-icon>
          <span class="nav-label" v-if="!collapsed">{{ darkMode ? '亮色' : '暗色' }}模式</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content" :class="{ 'sidebar-collapsed': collapsed }">
      <div class="content-wrapper">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--bg-main);
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar, var(--bg-card));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: all var(--duration-normal) ease;
  z-index: 100;
  box-shadow: var(--shadow-md);
}

.sidebar.collapsed {
  width: var(--sidebar-width-collapsed);
}

[data-theme="dark"] .sidebar {
  background: rgba(26, 31, 38, 0.95);
  border-right-color: var(--border-light);
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-light);
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.logo-text {
  font-size: 16px;
  font-weight: var(--font-weight-bold);
  color: var(--primary-600);
  white-space: nowrap;
  animation: slideIn 0.3s ease;
}

.collapse-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) ease;
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--primary-600);
  transform: scale(1.1);
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  color: var(--text-secondary);
  background: transparent;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--item-color);
  transform: scaleY(0);
  transition: transform var(--duration-normal) ease;
  border-radius: 0 2px 2px 0;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateX(2px);
}

.nav-item:hover::before {
  transform: scaleY(1);
}

.nav-item.active {
  background: var(--primary-50);
  color: var(--primary-600);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-primary-sm);
}

.nav-item.active::before {
  transform: scaleY(1);
}

[data-theme="dark"] .nav-item.active {
  background: var(--primary-100);
}

.nav-label {
  white-space: nowrap;
  animation: fadeIn 0.3s ease;
}

/* 侧边栏底部 */
.sidebar-footer {
  border-top: 1px solid var(--border-light);
  padding: 12px 8px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  color: var(--text-secondary);
  background: transparent;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--primary-600);
  transform: translateX(2px);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow: hidden;
  background: var(--bg-main);
  transition: all var(--duration-normal) ease;
}

.content-wrapper {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 滚动条样式 */
.content-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 4px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

/* 动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  :root {
    --sidebar-width: 120px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    transform: translateX(-100%);
    width: 260px;
    max-width: 86vw;
    background: var(--bg-sidebar, var(--bg-card));
    box-shadow: var(--shadow-xl);
    z-index: 1000;
  }

  .sidebar.collapsed {
    transform: translateX(0);
    width: 260px;
  }

  .main-content {
    margin-left: 0 !important;
  }

  /* 移动端遮罩层 */
  .app-layout.sidebar-collapsed::before {
    content: '';
    position: fixed;
    inset: 0;
    background: var(--overlay-50);
    backdrop-filter: blur(2px);
    z-index: 99;
    animation: fadeIn 0.3s ease;
  }

  .app-layout:not(.sidebar-collapsed)::before {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-item {
    padding: 10px 12px;
  }

  .logo-text {
    font-size: 14px;
  }
}

/* 深色模式适配 */
[data-theme="dark"] .sidebar {
  background: var(--bg-sidebar);
  border-right-color: var(--border-light);
}

[data-theme="dark"] .sidebar-header,
[data-theme="dark"] .sidebar-footer {
  border-color: var(--border-light);
}

/* 霓虹灯效果 - 仅在激活状态 */
.nav-item.active .el-icon {
  filter: drop-shadow(0 0 8px var(--item-color));
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 玻璃态增强 */
.sidebar {
  background: var(--bg-sidebar);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

[data-theme="dark"] .sidebar {
  background: var(--bg-sidebar);
}

/* 微交互 - 按下效果 */
.nav-item:active {
  transform: scale(0.98) translateX(0) !important;
}

/* 滚动条美化 */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: var(--gray-200);
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: var(--gray-300);
}

[data-theme="dark"] .sidebar-nav::-webkit-scrollbar-thumb {
  background: var(--gray-700);
}

[data-theme="dark"] .sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: var(--gray-600);
}

/* 工具提示样式 */
.sidebar .collapse-btn,
.sidebar .theme-toggle,
.nav-item {
  position: relative;
}

.sidebar .collapse-btn:hover::after,
.sidebar .theme-toggle:hover::after,
.nav-item:hover::after {
  content: attr(title);
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 8px;
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  opacity: 0;
  animation: tooltipIn 0.2s ease forwards;
  pointer-events: none;
  border: 1px solid var(--border-light);
}

@keyframes tooltipIn {
  to {
    opacity: 1;
  }
}

/* 当侧边栏折叠时，只显示图标的导航项 */
.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.sidebar.collapsed .nav-label {
  display: none;
}

.sidebar.collapsed .logo-text {
  display: none;
}

.sidebar.collapsed .theme-toggle .nav-label {
  display: none;
}

/* 注意：app-layout 已是 flex，sidebar 会自然占位；main-content 不需要额外 margin-left */

/* 加载状态指示器 */
.loading-indicator {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-500), var(--primary-300));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
  z-index: 10000;
}

.loading-indicator.active {
  transform: scaleX(1);
  animation: loadingPulse 1.5s ease-in-out infinite;
}

@keyframes loadingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* 通知红点 */
.badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background: var(--danger-500);
  border-radius: 50%;
  border: 2px solid var(--bg-main);
  animation: pulse 2s ease-in-out infinite;
}

/* 响应式断点优化 */
@media (max-width: 1024px) {
  :root {
    --sidebar-width: 140px;
  }
}

@media (max-width: 640px) {
  :root {
    --sidebar-width-collapsed: 64px;
  }

  .sidebar-header {
    padding: 12px 8px;
  }

  .nav-item {
    padding: 10px 12px;
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .sidebar {
    border-right-width: 2px;
    border-right-color: var(--gray-900);
  }

  .nav-item.active {
    border: 2px solid var(--gray-900);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .nav-item,
  .collapse-btn,
  .theme-toggle,
  .logo-text,
  .nav-label {
    transition: none !important;
    animation: none !important;
  }
}

/* 打印样式 */
@media print {
  .sidebar {
    display: none !important;
  }

  .main-content {
    margin-left: 0 !important;
  }
}
</style>
