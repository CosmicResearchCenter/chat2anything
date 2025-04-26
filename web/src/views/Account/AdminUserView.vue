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
          <el-input v-model="searchUser" placeholder="搜索用户名/邮箱..." prefix-icon="Search" clearable @clear="fetchUsers" @keyup.enter="fetchUsers"/>
        </div>
        <div class="search-actions">
          <el-select v-model="userTypeFilter" placeholder="用户类型" style="width: 120px;" @change="handleFilterChange">
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
          :data="users"  
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
          <el-table-column prop="create_time" label="注册时间" min-width="180">
            <template #default="scope">
              {{ formatDate(scope.row.create_time) }}
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
              <el-button link :type="scope.row.status === 'active' ? 'warning' : 'success'" @click.stop="toggleUserStatus(scope.row)">
                <el-icon><Switch /></el-icon>
                {{ scope.row.status === 'active' ? '禁用' : '启用' }}
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
          :current-page="currentPage"
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
              <el-descriptions-item label="注册时间">{{ formatDate(selectedUser.create_time) }}</el-descriptions-item>
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
              <el-descriptions-item label="对话数量">{{ selectedUser.stats?.conversationCount ?? 'N/A' }}</el-descriptions-item>
              <el-descriptions-item label="知识库数量">{{ selectedUser.stats?.knowledgeBaseCount ?? 'N/A' }}</el-descriptions-item>
              <el-descriptions-item label="最近活跃">{{ formatDate(selectedUser.stats?.lastActive) }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <el-divider />

        <div class="user-actions">
           <el-button :type="selectedUser.status === 'active' ? 'warning' : 'success'" @click="toggleUserStatus(selectedUser)">
             {{ selectedUser.status === 'active' ? '禁用用户' : '启用用户' }}
           </el-button>
          <el-button type="danger" @click="confirmDeleteUser(selectedUser)">删除用户</el-button>
        </div>
      </div>
      <el-skeleton :rows="10" animated v-else />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { getRequest, deleteRequest, postRequest, putRequest } from '@/utils/http'; // 确保导入 putRequest
import { ElMessage, ElMessageBox } from 'element-plus';
import { User, Search, Refresh, View, Delete, Switch } from '@element-plus/icons-vue'; // 导入图标

const searchUser = ref('');
const userTypeFilter = ref('all');
const loading = ref(false);
const users = ref<any[]>([]); // 只存储当前页的用户
const userDetailDrawer = ref(false);
const selectedUser = ref<any | null>(null); // 存储详细信息，包括 stats
// const currentUserId = ref(''); // 似乎未使用，可以移除
const pageSize = ref(10);
const currentPage = ref(1);
const totalUsers = ref(0);

// 用户统计数据（现在从 API 获取，可以移除或保留作为默认结构）
// const userStats = reactive({ ... }); // 不再需要模拟数据

// 获取用户列表 - 已更新以使用 API 参数
async function fetchUsers() {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    interface UserParams {
      page: number;
      pageSize: number;
      search?: string;
      type: string;
      [key: string]: any; // 添加索引签名允许字符串键访问
    }
    
    const params: UserParams = {
      page: currentPage.value,
      pageSize: pageSize.value,
      search: searchUser.value || undefined, // 如果为空则不传
      type: userTypeFilter.value,
      // sortBy: 'create_time', // 可选：添加排序
      // sortOrder: 'desc'      // 可选：添加排序
    };
    // 清理 undefined 参数
    Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

    // 构建查询字符串
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      queryParams.append(key, String(value));
    });

    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/users?${queryParams.toString()}`);
    if (response.code === 200 && response.data) {
      users.value = response.data.users || [];
      totalUsers.value = response.data.total || 0;
    } else {
      ElMessage.error(response.message || '获取用户列表失败');
      users.value = [];
      totalUsers.value = 0;
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表出错');
    users.value = [];
    totalUsers.value = 0;
  } finally {
    loading.value = false;
  }
}

// 删除用户 - 已更新端点
async function deleteUser(user: any) {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    // 使用新的端点
    const response = await deleteRequest<any>(baseURL + `/v1/api/mark/admin/user/${user.username}`);
    if (response.code === 200) {
      ElMessage.success('用户删除成功');
      if (userDetailDrawer.value && selectedUser.value?.username === user.username) {
        userDetailDrawer.value = false; // 如果删除的是当前查看的用户，关闭抽屉
      }
      // 刷新当前页数据
      // 如果删除的是当前页最后一条，可能需要跳转到前一页
      if (users.value.length === 1 && currentPage.value > 1) {
        currentPage.value--;
      }
      fetchUsers();
    } else {
      ElMessage.error(response.message || '删除用户失败');
    }
  } catch (error: any) {
    console.error('删除用户出错:', error);
    ElMessage.error(error.response?.data?.detail || '删除用户出错');
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

// 切换用户状态 - 新增函数
async function updateUserStatus(user: any, newStatus: 'active' | 'disabled') {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const url = `${baseURL}/v1/api/mark/admin/user/${user.username}/status`;
    const response = await putRequest<any>(url, { status: newStatus });

    if (response.code === 200) {
      ElMessage.success(`用户状态已更新为 ${newStatus === 'active' ? '活跃' : '禁用'}`);

      // 更新本地数据
      const userIndex = users.value.findIndex(u => u.username === user.username);
      if (userIndex !== -1) {
        users.value[userIndex].status = newStatus;
      }
      if (selectedUser.value && selectedUser.value.username === user.username) {
        selectedUser.value.status = newStatus;
      }
       // 强制刷新列表 (如果直接修改 ref 数组项无效)
       users.value = [...users.value];
       if (selectedUser.value) selectedUser.value = {...selectedUser.value};

    } else {
      ElMessage.error(response.message || '更新用户状态失败');
    }
  } catch (error: any) {
    console.error('更新用户状态出错:', error);
    ElMessage.error(error.response?.data?.detail || '更新用户状态出错');
  } finally {
    loading.value = false;
  }
}

// 触发切换用户状态
function toggleUserStatus(user: any) {
   const targetStatus = user.status === 'active' ? 'disabled' : 'active';
   const actionText = targetStatus === 'active' ? '启用' : '禁用';
   ElMessageBox.confirm(
    `确定要${actionText}用户 "${user.username}" 吗?`,
    `确认${actionText}`,
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
     updateUserStatus(user, targetStatus);
  }).catch(() => {
    ElMessage.info(`已取消${actionText}`);
  });
}


// 获取用户详细信息 - 新增函数
async function fetchUserDetail(username: string) {
  selectedUser.value = null; // 清空旧数据并显示加载状态
  userDetailDrawer.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/user/${username}/details`);
    if (response.code === 200 && response.data) {
      selectedUser.value = response.data;
    } else {
      ElMessage.error(response.message || '获取用户详情失败');
      userDetailDrawer.value = false; // 获取失败则关闭抽屉
    }
  } catch (error: any) {
    console.error('获取用户详情出错:', error);
    ElMessage.error(error.response?.data?.detail || '获取用户详情出错');
    userDetailDrawer.value = false; // 出错则关闭抽屉
  }
}

// 查看用户详情 - 调用 fetchUserDetail
function viewUserDetail(user: any) {
  fetchUserDetail(user.username);
}

// 处理行点击 - 调用 fetchUserDetail
function handleRowClick(row: any) {
  fetchUserDetail(row.username);
}

// 格式化日期
function formatDate(dateString: string | null | undefined) {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleString();
  } catch (e) {
    return dateString; // 如果格式无效，返回原始字符串
  }
}

// 重置搜索和过滤
function resetSearch() {
  searchUser.value = '';
  userTypeFilter.value = 'all';
  currentPage.value = 1; // 重置到第一页
  fetchUsers();
}

// 处理筛选变化
function handleFilterChange() {
    currentPage.value = 1; // 筛选变化时重置到第一页
    fetchUsers();
}

// 处理分页大小变化
function handleSizeChange(size: number) {
  pageSize.value = size;
  currentPage.value = 1; // 切换大小后回到第一页
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
  display: grid; /* 使用 grid 布局 */
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* 响应式列 */
  gap: 24px; /* 列间距 */
}

.stat-block {
  /* margin-bottom: 24px; */ /* 由 grid gap 控制间距 */

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

/* 确保 el-icon 在按钮中有正确的间距 */
.el-button .el-icon {
  margin-right: 4px;
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
  
  .user-stats {
    grid-template-columns: 1fr; /* 在小屏幕上堆叠 */
  }
}
</style>
