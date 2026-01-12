<template>
  <el-container class="base-container" :class="{ 'dark-mode': isDarkMode, 'content-visible': contentVisible }">
    <el-aside class="base-aside">
      <div class="aside-header">
        <el-input v-model="searchUser" placeholder="搜索用户..." prefix-icon="Search" />
        <!-- <el-switch v-model="isDarkMode" class="theme-switch" size="small" /> -->
      </div>
      <div class="user-list">
        <div v-for="user in filteredUsers" 
             :key="user.username"
             class="user-item"
             :class="{ active: currentUserId === user.username }"
             @click="handleUserClick(user.username)">
          <el-avatar :size="32" :src="user.avatar">{{ user.username.charAt(0) }}</el-avatar>
          <span class="username">{{ user.username }}</span>
        </div>
      </div>
    </el-aside>

    <!-- 中间知识库列表 -->
    <el-main class="base-main">
      <div v-if="currentUserId" class="knowledge-base-list">
        <div v-for="base in userKnowledgeBases" 
             :key="base.knowledge_base_id"
             class="base-item"
             :class="{ active: currentBaseId === base.knowledge_base_id, 'deleted': base.knowledge_base_info.delete_sign }"
             @click="handleBaseClick(base.knowledge_base_id)">
          <div class="base-info">
            <div class="base-title">{{ base.knowledge_base_name }}</div>
            <div class="base-stats">
              <!-- <span>文档数: {{ base.knowledge_base_info.docs_num }}</span> -->
              <span>创建时间: {{ formatDate(base.knowledge_base_info.create_time) }}</span>
              <span v-if="base.knowledge_base_info.delete_sign" class="delete-sign">已删除</span>
            </div>
          </div>
          <el-button link type="danger" @click.stop="confirmDeleteKnowledgeBase(base)">删除</el-button>
        </div>
      </div>
      <div v-else class="no-selection">
        请选择用户查看知识库
      </div>
    </el-main>

    <!-- 右侧文档列表 -->
    <el-aside class="base-aside-right">
      <div v-if="currentBaseId" class="document-list">
        <el-table :data="baseDocuments" style="width: 100%">
          <el-table-column prop="doc_name" label="文档名称" />
          <el-table-column prop="doc_size" label="大小" width="100">
            <template #default="scope">
              {{ formatSize(scope.row.doc_size) }}
            </template>
          </el-table-column>
          <!-- <el-table-column prop="retriever_num" label="检索次数" width="100" /> -->
          <!-- <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button link type="primary" @click="viewDocument(scope.row)">查看</el-button>
            </template>
          </el-table-column> -->
        </el-table>
      </div>
      <div v-else class="no-selection">
        请选择知识库查看文档列表
      </div>
    </el-aside>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getRequest, deleteRequest } from '@/utils/http';
import { ElMessage, ElMessageBox } from 'element-plus';

const searchUser = ref('');
const currentUserId = ref('');
const currentBaseId = ref('');
const users = ref<any[]>([]);
const userKnowledgeBases = ref<any[]>([]);
const baseDocuments = ref<any[]>([]);

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
    if (response.code === 200) {
      users.value = response.data.users;
    } else {
      ElMessage.error('获取用户列表失败');
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表出错');
  }
}

// 获取用户的知识库列表
async function handleUserClick(username: string) {
  currentUserId.value = username;
  currentBaseId.value = '';
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + `/v1/api/mark/admin/user_knowledge_base/${username}`);
    if (response.code === 200) {
      userKnowledgeBases.value = response.data[0];
    }
  } catch (error) {
    console.error('获取知识库列表出错:', error);
    ElMessage.error('获取知识库列表失败');
  }
}

// 获取知识库文档列表
async function handleBaseClick(baseId: string) {
  currentBaseId.value = baseId;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + `/v1/api/mark/admin/user_knowledge_base/${currentUserId.value}/${baseId}`);
    if (response.code === 200) {
      baseDocuments.value = response.data[0];
    }
  } catch (error) {
    console.error('获取文档列表出错:', error);
    ElMessage.error('获取文档列表失败');
  }
}

// 查看文档详情
function viewDocument(doc: any) {
  // 实现文档查看逻辑
  ElMessage.info(`查看文档: ${doc.doc_name}`);
}

// 删除知识库
async function deleteKnowledgeBase(base: any) {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await deleteRequest<any>(baseURL + `/v1/api/mark/admin/user_knowledge_base/${currentUserId.value}/${base.knowledge_base_id}`);
    if (response.code === 200) {
      ElMessage.success('知识库删除成功');
      handleUserClick(currentUserId.value); // 重新加载知识库列表
    } else {
      ElMessage.error('删除知识库失败');
    }
  } catch (error) {
    console.error('删除知识库出错:', error);
    ElMessage.error('删除知识库出错');
  }
}

// 确认删除知识库
function confirmDeleteKnowledgeBase(base: any) {
  ElMessageBox.confirm(
    '此操作将永久删除该知识库, 是否继续?',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteKnowledgeBase(base);
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleDateString();
}

// 格式化文件大小
function formatSize(bytes: number) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers();
  setTimeout(() => contentVisible.value = true, 100);
});

// 添加主题切换
const isDarkMode = ref(false);

// 添加动画状态
const contentVisible = ref(false);
</script>

<style scoped>
.base-container {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 16px;
  height: 100%;
  padding: 16px;
  background: var(--bg-main);
  overflow: hidden;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.base-container.content-visible {
  opacity: 1;
}

/* 左侧用户列表 */
.base-aside {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.aside-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.aside-header :deep(.el-input__wrapper) {
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  transition: all 0.2s;
}

.aside-header :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-400);
}

.aside-header :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-600);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.user-list {
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

.username {
  font-size: 14px;
}

/* 中间知识库列表 */
.base-main {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.knowledge-base-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.base-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 6px 0;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-main);
  border: 1px solid var(--border-light);
}

.base-item:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.base-item.active {
  background: var(--primary-50);
  border-color: var(--primary-300);
  color: var(--primary-700);
  font-weight: 500;
}

.base-item.deleted {
  background: var(--danger-50);
  border-color: var(--danger-200);
  color: var(--danger-600);
  opacity: 0.7;
}

.base-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.base-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.base-stats {
  font-size: 12px;
  color: var(--text-tertiary);
  display: flex;
  gap: 12px;
  align-items: center;
}

.base-item.active .base-stats {
  color: var(--primary-600);
}

.base-item.deleted .base-stats {
  color: var(--danger-500);
}

.delete-sign {
  color: var(--danger-500);
  font-weight: 600;
}

/* 右侧文档列表 */
.base-aside-right {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.document-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.document-list :deep(.el-table) {
  --el-table-border-color: var(--border-light);
  --el-table-header-background-color: var(--bg-main);
  --el-table-background-color: var(--bg-card);
  --el-table-row-hover-background-color: var(--bg-hover);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  background: transparent;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.document-list :deep(.el-table th) {
  background-color: var(--bg-main);
  color: var(--text-secondary);
  font-weight: 600;
  border-bottom: 1px solid var(--border-light);
}

.document-list :deep(.el-table td) {
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}

.document-list :deep(.el-table__empty-block) {
  background-color: var(--bg-card);
  color: var(--text-tertiary);
}

/* 空状态 */
.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 120px;
  color: var(--text-tertiary);
  font-size: 14px;
  text-align: center;
  padding: 20px;
}

/* 自定义滚动条 */
.user-list::-webkit-scrollbar,
.knowledge-base-list::-webkit-scrollbar,
.document-list::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.user-list::-webkit-scrollbar-track,
.knowledge-base-list::-webkit-scrollbar-track,
.document-list::-webkit-scrollbar-track {
  background: transparent;
}

.user-list::-webkit-scrollbar-thumb,
.knowledge-base-list::-webkit-scrollbar-thumb,
.document-list::-webkit-scrollbar-thumb {
  background-color: var(--border-light);
  border-radius: 4px;
}

.user-list::-webkit-scrollbar-thumb:hover,
.knowledge-base-list::-webkit-scrollbar-thumb:hover,
.document-list::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-medium);
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .base-container {
    grid-template-columns: 240px 1fr;
  }

  .base-aside-right {
    grid-column: 1 / -1;
    min-height: 300px;
  }
}

@media screen and (max-width: 768px) {
  .base-container {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }

  .base-aside,
  .base-main,
  .base-aside-right {
    min-height: 200px;
  }
}

/* 暗色模式适配 */
[data-theme="dark"] .base-container {
  background: var(--bg-main);
}

[data-theme="dark"] .base-aside,
[data-theme="dark"] .base-main,
[data-theme="dark"] .base-aside-right {
  background: var(--bg-card);
  border-color: var(--border-light);
}

[data-theme="dark"] .aside-header :deep(.el-input__wrapper) {
  background: var(--bg-elevated);
}

[data-theme="dark"] .user-item:hover,
[data-theme="dark"] .base-item:hover {
  background: var(--bg-hover);
}

[data-theme="dark"] .base-item.active {
  background: var(--primary-700);
  border-color: var(--primary-500);
  color: white;
}

[data-theme="dark"] .base-item.active .base-stats {
  color: white;
}

[data-theme="dark"] .base-item.deleted {
  background: var(--danger-700);
  border-color: var(--danger-500);
  color: white;
}

[data-theme="dark"] .base-item {
  background: var(--bg-elevated);
}

[data-theme="dark"] .document-list :deep(.el-table th) {
  background-color: var(--bg-elevated);
}

[data-theme="dark"] .document-list :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: var(--bg-main);
}
</style>
