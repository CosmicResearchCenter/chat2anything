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
  height: 100vh;
  background: var(--bg-color, #f5f7fa);
  transition: all 0.3s ease;
  opacity: 0;
}

.base-container.content-visible {
  opacity: 1;
}

.base-container.dark-mode {
  --bg-color: #1a1a1a;
  --card-bg: #242424;
  --text-color: #fff;
  --border-color: #333;
  color: var(--text-color);
}

.base-aside {
  width: 20% !important;
  background: var(--card-bg, rgba(248, 249, 250, 0.95));
  backdrop-filter: blur(20px);
  border-radius: 16px;
  margin: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.base-aside-right {
  width: 30% !important;
  background: rgba(248, 249, 250, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  margin: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.base-main {
  width: 50% !important;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  margin: 12px;
  padding: 20px;
}

.search-box {
  margin-bottom: 20px;
}

.user-item, .base-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.user-item:hover, .base-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.user-item.active, .base-item.active {
  background: #0245a3;
  color: white;
}

.username {
  margin-left: 12px;
}

.base-info {
  width: 100%;
}

.base-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.base-stats {
  font-size: 12px;
  color: #666;
  display: flex;
  justify-content: space-between;
}

.base-item.active .base-stats {
  color: #fff;
}

.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}

.base-item {
  border: 1px solid var(--border-color, #eee);
  margin: 8px 0;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.base-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.base-item.deleted {
  background: #ffebee;
  color: #d32f2f;
}

.delete-sign {
  color: #d32f2f;
  font-weight: bold;
}

@media screen and (max-width: 768px) {
  .base-aside,
  .base-aside-right,
  .base-main {
    width: 100% !important;
    margin: 6px;
  }
  
  .el-container {
    flex-direction: column;
  }
}
</style>
