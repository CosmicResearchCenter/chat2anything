<template>
  <div class="admin-chat-layout">
    <!-- 左侧用户列表 -->
    <aside class="sidebar-left">
      <div class="sidebar-header">
        <h3 class="sidebar-title">用户列表</h3>
        <el-input
          v-model="searchUser"
          placeholder="搜索用户..."
          class="search-input"
          :prefix-icon="Search"
          size="small"
        />
      </div>
      <div class="sidebar-content custom-scrollbar">
        <div
          v-for="user in filteredUsers"
          :key="user.id"
          class="user-item"
          :class="{ active: currentUserId === user.id }"
          @click="handleUserClick(user.id)"
        >
          <el-avatar :size="32" :src="user.avatar" class="user-avatar">
            {{ user.username.charAt(0) }}
          </el-avatar>
          <span class="username">{{ user.username }}</span>
        </div>
        <div v-if="filteredUsers.length === 0" class="empty-state">
          暂无用户
        </div>
      </div>
    </aside>

    <!-- 中间对话列表 -->
    <main class="main-content">
      <div class="content-header">
        <h3>{{ currentUserId ? '用户对话列表' : '请选择用户' }}</h3>
      </div>
      <div class="content-body custom-scrollbar">
        <div v-if="currentUserId" class="conversation-list">
          <div
            v-for="conv in userConversations"
            :key="conv.id"
            class="conversation-item"
            :class="{
              active: currentConvId === conv.id,
              deleted: conv.delete_sign
            }"
            @click="handleConversationClick(conv.id)"
          >
            <div class="conv-info">
              <div class="conv-title">{{ conv.title }}</div>
              <div class="conv-meta">
                <span class="conv-time">{{ formatDate(conv.created_at) }}</span>
                <span v-if="conv.delete_sign" class="delete-badge">已删除</span>
              </div>
            </div>
            <el-button
              link
              type="danger"
              size="small"
              @click.stop="confirmDeleteConversation(conv)"
            >
              删除
            </el-button>
          </div>
          <div v-if="userConversations.length === 0" class="empty-state">
            暂无对话记录
          </div>
        </div>
        <div v-else class="empty-placeholder">
          <div class="placeholder-content">
            <el-icon class="placeholder-icon"><ChatLineRound /></el-icon>
            <p>请选择左侧用户查看对话记录</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 右侧聊天记录 -->
    <aside class="sidebar-right">
      <div class="content-header">
        <h3>{{ currentConvId ? '对话详情' : '消息记录' }}</h3>
      </div>
      <div class="content-body custom-scrollbar">
        <div v-if="currentConvId" class="message-list">
          <div
            v-for="msg in conversationMessages"
            :key="msg.id"
            class="message-item"
            :class="{
              'user-message': msg.role === 'user',
              'assistant-message': msg.role === 'assistant'
            }"
          >
            <div class="message-header">
              <span class="role-badge" :class="msg.role">
                {{ msg.role === 'user' ? '用户' : '助手' }}
              </span>
              <span class="time">{{ formatTime(msg.created_at) }}</span>
            </div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="conversationMessages.length === 0" class="empty-state">
            暂无消息
          </div>
        </div>
        <div v-else class="empty-placeholder">
          <div class="placeholder-content">
            <el-icon class="placeholder-icon"><Message /></el-icon>
            <p>选择对话查看详细消息记录</p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getRequest, deleteRequest } from '@/utils/http';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Search, ChatLineRound, Message } from '@element-plus/icons-vue';

const searchUser = ref('');
const currentUserId = ref('');
const currentConvId = ref('');
const users = ref<any[]>([]);
const userConversations = ref<any[]>([]);
const conversationMessages = ref<any[]>([]);
const isDarkMode = ref(false);

// 过滤用户列表
const filteredUsers = computed(() => {
  return users.value.filter(user =>
    user.username.toLowerCase().includes(searchUser.value.toLowerCase())
  );
});

// 获取用户列表
async function fetchUsers() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + '/v1/api/mark/admin/users');
    users.value = response.data.users.map((user: any) => ({
      id: user.username,
      username: user.username,
      avatar: '',
      admin_sign: user.admin_sign
    }));
  } catch (error) {
    users.value = [];
    console.log('Failed to fetch users');
  }
}

// 获取用户的对话列表
async function handleUserClick(userId: string) {
  currentUserId.value = userId;
  currentConvId.value = '';
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + `/v1/api/mark/admin/user_conversation/${userId}`);
    userConversations.value = response.data[0].map((conv: any) => ({
      id: conv.conversation_id,
      title: conv.conversation_title,
      created_at: conv.conversation_time,
      delete_sign: conv.delete_sign
    }));
  } catch (error) {
    userConversations.value = [];
    console.log('Failed to fetch conversations');
  }
}

// 获取对话详细记录
async function handleConversationClick(convId: string) {
  currentConvId.value = convId;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + `/v1/api/mark/admin/conversation/${convId}`);
    conversationMessages.value = response.data[0].flatMap((msg: any) => [
      msg.user ? {
        id: msg.message_time || Date.now().toString(),
        role: 'user',
        content: msg.user,
        created_at: msg.message_time || new Date().toISOString()
      } : null,
      msg.assistant ? {
        id: msg.message_time || Date.now().toString(),
        role: 'assistant',
        content: msg.assistant,
        created_at: msg.message_time || new Date().toISOString()
      } : null
    ].filter(Boolean));
  } catch (error) {
    conversationMessages.value = [];
    console.log('Failed to fetch messages');
  }
}

// 删除对话
async function handleDeleteConversation(convId: string) {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    await deleteRequest<any>(baseURL + `/v1/api/mark/admin/user_conversation/${currentUserId.value}/${convId}`);
    userConversations.value = userConversations.value.filter(conv => conv.id !== convId);
    if (currentConvId.value === convId) {
      currentConvId.value = '';
      conversationMessages.value = [];
    }
  } catch (error) {
    console.log('Failed to delete conversation');
  }
}

// 确认删除对话
function confirmDeleteConversation(conv: any) {
  ElMessageBox.confirm(
    '此操作将永久删除该对话, 是否继续?',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    handleDeleteConversation(conv.id);
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleDateString();
}

// 格式化时间
function formatTime(date: string) {
  return new Date(date).toLocaleTimeString();
}

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.admin-chat-layout {
  display: grid;
  grid-template-columns: 1fr 1fr 3fr;
  gap: 16px;
  height: 100%;
  padding: 16px;
  background: var(--bg-main);
  overflow: hidden;
}

/* 左侧用户列表 */
.sidebar-left {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.search-input :deep(.el-input__wrapper) {
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  transition: all 0.2s;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-400);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-600);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin: 4px 0;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.user-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.user-item.active {
  background: var(--primary-600);
  color: white;
  font-weight: 500;
}

.user-avatar {
  flex-shrink: 0;
}

.username {
  font-size: 14px;
}

/* 中间对话列表 */
.main-content {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.content-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
}

.content-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 6px 0;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-main);
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-light);
  transform: translateY(-1px);
}

.conversation-item.active {
  background: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--primary-700);
  font-weight: 500;
}

.conversation-item.deleted {
  opacity: 0.6;
  text-decoration: line-through;
  color: var(--danger-500);
}

.conv-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.conv-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: var(--text-tertiary);
}

.delete-badge {
  color: var(--danger-500);
  font-weight: 500;
}

/* 右侧聊天记录 */
.sidebar-right {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  padding: 12px;
  border-radius: var(--radius-md);
  backdrop-filter: blur(10px);
  animation: fadeIn 0.3s ease;
  border: 1px solid var(--border-light);
}

.user-message {
  background: var(--primary-50);
  border-color: var(--primary-200);
}

.assistant-message {
  background: var(--bg-elevated);
  border-color: var(--border-medium);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.role-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.role-badge.user {
  background: var(--primary-100);
  color: var(--primary-700);
}

.role-badge.assistant {
  background: var(--bg-main);
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
}

.time {
  color: var(--text-tertiary);
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

/* 空状态 */
.empty-state,
.empty-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 120px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.placeholder-icon {
  font-size: 32px;
  color: var(--text-tertiary);
  opacity: 0.5;
}

.placeholder-content p {
  margin: 0;
  color: var(--text-secondary);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 自定义滚动条 */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--border-light) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-light);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-medium);
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .admin-chat-layout {
    grid-template-columns: 240px 1fr;
  }

  .sidebar-right {
    grid-column: 1 / -1;
    min-height: 300px;
  }
}

@media screen and (max-width: 768px) {
  .admin-chat-layout {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }

  .sidebar-left,
  .main-content,
  .sidebar-right {
    min-height: 200px;
  }
}

/* Element Plus 组件样式覆盖 */
.message-item :deep(.el-collapse-item__header) {
  background: transparent;
  border-color: var(--border-light);
  color: var(--text-primary);
}

.message-item :deep(.el-collapse-item__content) {
  background: var(--bg-main);
  color: var(--text-primary);
}

/* 暗色模式适配 */
[data-theme="dark"] .admin-chat-layout {
  background: var(--bg-main);
}

[data-theme="dark"] .sidebar-left,
[data-theme="dark"] .main-content,
[data-theme="dark"] .sidebar-right {
  background: var(--bg-card);
  border-color: var(--border-light);
}

[data-theme="dark"] .user-item:hover,
[data-theme="dark"] .conversation-item:hover {
  background: var(--bg-hover);
}

[data-theme="dark"] .conversation-item.active {
  background: var(--primary-700);
  border-color: var(--primary-500);
  color: white;
}

[data-theme="dark"] .user-message {
  background: var(--primary-700);
  border-color: var(--primary-500);
  color: white;
}

[data-theme="dark"] .assistant-message {
  background: var(--bg-elevated);
  border-color: var(--border-medium);
}

[data-theme="dark"] .search-input :deep(.el-input__wrapper) {
  background: var(--bg-elevated);
}

[data-theme="dark"] .conversation-item {
  background: var(--bg-elevated);
}

[data-theme="dark"] .message-content {
  color: var(--text-primary);
}
</style>
