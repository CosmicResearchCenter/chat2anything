<template>
  <div class="user-container">
    <div class="page-header">
      <div class="page-title">
        <el-icon><User /></el-icon>
        <h2>用户管理</h2>
      </div>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>用户管理</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="card-container">
      <!-- 搜索和过滤 -->
      <div class="search-bar">
        <div class="search-input">
          <el-input v-model="searchUser" placeholder="搜索用户名/邮箱/ID..." prefix-icon="Search" clearable />
        </div>
        <div class="search-actions">
          <el-select v-model="userTypeFilter" placeholder="用户类型" style="width: 120px;">
            <el-option label="全部用户" value="all" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
          <el-button type="primary" @click="fetchUsers">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </div>
      </div>

      <!-- 用户列表 -->
      <div class="table-container">
        <el-table
          :data="filteredUsers"
          :loading="loading"
          style="width: 100%"
          border
          stripe
          highlight-current-row
          @row-click="handleRowClick"
        >
          <el-table-column prop="username" label="用户名" min-width="120">
            <template #default="scope">
              <div class="user-info">
                <el-avatar :size="32" :src="scope.row.avatar">
                  {{ scope.row.username.charAt(0) }}
                </el-avatar>
                <span class="username-text">{{ scope.row.username }}</span>
                <el-tag v-if="scope.row.admin_sign" size="small" effect="dark" type="primary">管理员</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="created_at" label="注册时间" min-width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
                {{ scope.row.status === 'active' ? '活跃' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click.stop="viewUserDetail(scope.row)">
                <el-icon><View /></el-icon>查看
              </el-button>
              <el-button link type="primary" @click.stop="toggleAdmin(scope.row)">
                {{ scope.row.admin_sign ? '撤销管理员' : '授权管理员' }}
              </el-button>
              <el-button link type="danger" @click.stop="confirmDeleteUser(scope.row)">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalUsers"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 用户详情抽屉 -->
    <el-drawer
      v-model="userDetailDrawer"
      title="用户详情"
      direction="rtl"
      size="50%"
    >
      <div v-if="selectedUser" class="user-detail">
        <div class="user-header">
          <el-avatar :size="64" :src="selectedUser.avatar">
            {{ selectedUser.username?.charAt(0) }}
          </el-avatar>
          <div class="user-title">
            <h3>{{ selectedUser.username }}</h3>
            <p>{{ selectedUser.email }}</p>
          </div>
        </div>
        
        <el-divider />
        
        <div class="user-stats">
          <div class="stat-block">
            <h4>用户信息</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="用户ID">{{ selectedUser.username }}</el-descriptions-item>
              <el-descriptions-item label="注册时间">{{ formatDate(selectedUser.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="管理权限">
                <el-tag :type="selectedUser.admin_sign ? 'primary' : 'info'">
                  {{ selectedUser.admin_sign ? '管理员' : '普通用户' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="selectedUser.status === 'active' ? 'success' : 'danger'">
                  {{ selectedUser.status === 'active' ? '活跃' : '禁用' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div class="stat-block">
            <h4>使用统计</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="对话数量">{{ userStats.conversationCount }}</el-descriptions-item>
              <el-descriptions-item label="知识库数量">{{ userStats.knowledgeBaseCount }}</el-descriptions-item>
              <el-descriptions-item label="最近活跃">{{ userStats.lastActive }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
        
        <el-divider />
        
        <div class="user-actions">
          <el-button type="primary" @click="toggleAdmin(selectedUser)">
            {{ selectedUser.admin_sign ? '撤销管理员' : '授权管理员' }}
          </el-button>
          <el-button type="danger" @click="confirmDeleteUser(selectedUser)">删除用户</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { getRequest, deleteRequest, postRequest } from '@/utils/http';
import { ElMessage, ElMessageBox } from 'element-plus';

const searchUser = ref('');
const userTypeFilter = ref('all');
const loading = ref(false);
const users = ref<any[]>([]);
const userDetailDrawer = ref(false);
const selectedUser = ref<any | null>(null);
const currentUserId = ref('');
const pageSize = ref(10);
const currentPage = ref(1);
const totalUsers = ref(0);

// 用户统计数据（模拟）
const userStats = reactive({
  conversationCount: 25,
  knowledgeBaseCount: 3,
  lastActive: '2023-05-22 15:30:45'
});

// 过滤用户列表
const filteredUsers = computed(() => {
  let result = users.value;
  
  // 按类型筛选
  if (userTypeFilter.value !== 'all') {
    const isAdmin = userTypeFilter.value === 'admin';
    result = result.filter(user => user.admin_sign === isAdmin);
  }
  
  // 按搜索词过滤
  if (searchUser.value) {
    const searchLower = searchUser.value.toLowerCase();
    result = result.filter(user =>
      user.username.toLowerCase().includes(searchLower) || 
      (user.email && user.email.toLowerCase().includes(searchLower))
    );
  }
  
  return result;
});

// 获取用户列表
async function fetchUsers() {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(baseURL + '/v1/api/mark/admin/users');
    if (response.code === 200) {
      users.value = response.data[0].map((user: any) => ({
        ...user,
        status: 'active' // 模拟状态数据
      }));
      totalUsers.value = users.value.length;
    } else {
      ElMessage.error('获取用户列表失败');
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表出错');
  } finally {
    loading.value = false;
  }
}

// 删除用户
async function deleteUser(user: any) {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await deleteRequest<any>(baseURL + `/v1/api/mark/admin/user/${user.username}`);
    if (response.code === 200) {
      ElMessage.success('用户删除成功');
      if (userDetailDrawer.value) {
        userDetailDrawer.value = false;
      }
      fetchUsers(); // 重新加载用户列表
    } else {
      ElMessage.error('删除用户失败');
    }
  } catch (error) {
    console.error('删除用户出错:', error);
    ElMessage.error('删除用户出错');
  } finally {
    loading.value = false;
  }
}

// 确认删除用户
function confirmDeleteUser(user: any) {
  ElMessageBox.confirm(
    `此操作将永久删除用户 "${user.username}", 是否继续?`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteUser(user);
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

// 切换管理员权限
async function toggleAdmin(user: any) {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const url = user.admin_sign 
      ? `/v1/api/mark/admin/revoke_admin/${user.username}`
      : `/v1/api/mark/admin/grant_admin/${user.username}`;
    const response = await postRequest<any>(baseURL + url, {});
    if (response.code === 200) {
      ElMessage.success(user.admin_sign ? '管理员权限已撤销' : '管理员权限已授予');
      
      // 更新当前用户数据
      if (selectedUser.value && selectedUser.value.username === user.username) {
        selectedUser.value.admin_sign = !user.admin_sign;
      }
      
      // 更新列表中的用户数据
      const userIndex = users.value.findIndex(u => u.username === user.username);
      if (userIndex !== -1) {
        users.value[userIndex].admin_sign = !user.admin_sign;
      }
      
      // 强制刷新列表
      users.value = [...users.value];
    } else {
      ElMessage.error(user.admin_sign ? '撤销管理员权限失败' : '授予管理员权限失败');
    }
  } catch (error) {
    console.error(user.admin_sign ? '撤销管理员权限出错:' : '授予管理员权限出错:', error);
    ElMessage.error(user.admin_sign ? '撤销管理员权限出错' : '授予管理员权限出错');
  } finally {
    loading.value = false;
  }
}

// 查看用户详情
function viewUserDetail(user: any) {
  selectedUser.value = {...user};
  userDetailDrawer.value = true;
}

// 处理行点击
function handleRowClick(row: any) {
  viewUserDetail(row);
}

// 格式化日期
function formatDate(date: string) {
  if (!date) return '-';
  return new Date(date).toLocaleString();
}

// 重置搜索
function resetSearch() {
  searchUser.value = '';
  userTypeFilter.value = 'all';
  fetchUsers();
}

// 处理分页大小变化
function handleSizeChange(size: number) {
  pageSize.value = size;
  fetchUsers();
}

// 处理页码变化
function handleCurrentChange(page: number) {
  currentPage.value = page;
  fetchUsers();
}

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.user-container {
  padding: 24px;
  min-height: calc(100vh - 48px);
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  
  h2 {
    font-size: 24px;
    font-weight: 500;
    margin: 0;
    color: #1a1a1a;
  }
  
  .el-icon {
    font-size: 24px;
    color: #409eff;
  }
}

.card-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.search-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.search-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-container {
  margin-bottom: 24px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username-text {
  margin-right: 8px;
}

.user-detail {
  padding: 16px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.user-title {
  h3 {
    margin: 0 0 8px;
    font-size: 20px;
    font-weight: 600;
  }
  
  p {
    margin: 0;
    font-size: 14px;
    color: #666;
  }
}

.user-stats {
  margin-top: 24px;
}

.stat-block {
  margin-bottom: 24px;
  
  h4 {
    margin: 0 0 16px;
    font-size: 16px;
    font-weight: 500;
  }
}

.user-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .user-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .user-detail {
    padding: 8px;
  }
  
  .user-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}
</style>
