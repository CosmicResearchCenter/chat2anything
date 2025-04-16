<template>
  <el-container class="user-container">
    <el-main class="user-main">
      <div class="aside-header">
        <el-input v-model="searchUser" placeholder="搜索用户..." prefix-icon="Search" />
      </div>
      <div class="user-list">
        <div v-for="user in filteredUsers" 
             :key="user.username"
             class="user-item"
             :class="{ active: currentUserId === user.username, admin: user.admin_sign }"
             >
          <el-avatar :size="32" :src="user.avatar">{{ user.username.charAt(0) }}</el-avatar>
          <span class="username">{{ user.username }}</span>
          <el-button class="delete-button" link type="danger" @click.stop="confirmDeleteUser(user)">删除</el-button>
          <el-button class="authorize-button" link type="primary" @click.stop="toggleAdmin(user)">
            {{ user.admin_sign ? '撤销管理员' : '授权管理员' }}
          </el-button>
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getRequest, deleteRequest, postRequest } from '@/utils/http';
import { ElMessage, ElMessageBox } from 'element-plus';

const searchUser = ref('');
const currentUserId = ref('');
const users = ref<any[]>([]);

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
      users.value = response.data[0];
    } else {
      ElMessage.error('获取用户列表失败');
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表出错');
  }
}

// 删除用户
async function deleteUser(user: any) {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await deleteRequest<any>(baseURL + `/v1/api/mark/admin/user/${user.username}`);
    if (response.code === 200) {
      ElMessage.success('用户删除成功');
      fetchUsers(); // 重新加载用户列表
    } else {
      ElMessage.error('删除用户失败');
    }
  } catch (error) {
    console.error('删除用户出错:', error);
    ElMessage.error('删除用户出错');
  }
}

// 确认删除用户
function confirmDeleteUser(user: any) {
  ElMessageBox.confirm(
    '此操作将永久删除该用户, 是否继续?',
    '提示',
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
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const url = user.admin_sign 
      ? `/v1/api/mark/admin/revoke_admin/${user.username}`
      : `/v1/api/mark/admin/grant_admin/${user.username}`;
    const response = await postRequest<any>(baseURL + url, {});
    if (response.code === 200) {
      ElMessage.success(user.admin_sign ? '管理员权限已撤销' : '管理员权限已授予');
      fetchUsers(); // 重新加载用户列表
    } else {
      ElMessage.error(user.admin_sign ? '撤销管理员权限失败' : '授予管理员权限失败');
    }
  } catch (error) {
    console.error(user.admin_sign ? '撤销管理员权限出错:' : '授予管理员权限出错:', error);
    ElMessage.error(user.admin_sign ? '撤销管理员权限出错' : '授予管理员权限出错');
  }
}

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.user-container {
  height: 100vh;
  background: var(--bg-color, #f0f2f5);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.user-main {
  width: 100%;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.aside-header {
  margin-bottom: 20px;
}

.user-list {
  max-height: 70vh;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.user-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.user-item.active {
  background: #409eff;
  color: white;
}

.user-item.admin {
  border-left: 4px solid #409eff;
}

.username {
  margin-left: 12px;
  font-weight: 500;
}

.delete-button {
  color: #f56c6c;
  font-weight: bold;
  margin-left: auto;
  margin-right: 8px;
}

.authorize-button {
  color: #1e6105;
  font-weight: bold;
}
</style>
