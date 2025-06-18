<template>
  <div class="invite-container">
    <div class="page-header">
      <div class="page-title">
        <el-icon><Ticket /></el-icon>
        <h2>邀请码管理</h2>
      </div>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>邀请码管理</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="card-container">
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card" v-for="(stat, index) in statistics" :key="index" :style="{ '--stat-color': stat.color }">
          <div class="stat-icon">
            <el-icon :size="28"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>生成邀请码
        </el-button>
        <div class="search-actions">
          <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px;" @change="fetchInviteCodes">
            <el-option label="全部" value="all" />
            <el-option label="未使用" value="unused" />
            <el-option label="已使用" value="used" />
            <el-option label="已过期" value="expired" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
          <el-button @click="fetchInviteCodes">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </div>

      <!-- 邀请码列表 -->
      <div class="table-container">
        <el-table
          :data="inviteCodes"
          :loading="loading"
          style="width: 100%"
          border
          stripe
          highlight-current-row
        >
          <el-table-column prop="code" label="邀请码" min-width="280">
            <template #default="scope">
              <div class="code-cell">
                <span class="code-text">{{ scope.row.code }}</span>
                <el-button link @click="copyCode(scope.row.code)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" />
          <el-table-column prop="created_by" label="创建者" width="100" />
          <el-table-column label="使用情况" width="120">
            <template #default="scope">
              <span>{{ scope.row.current_uses }}/{{ scope.row.max_uses }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="expire_at" label="过期时间" width="180">
            <template #default="scope">
              {{ scope.row.expire_at ? formatDate(scope.row.expire_at) : '永不过期' }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row)">
                {{ getStatusText(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="editInviteCode(scope.row)" v-if="!scope.row.is_used">
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button link :type="scope.row.is_active ? 'warning' : 'success'" 
                        @click="toggleInviteCodeStatus(scope.row)" v-if="!scope.row.is_used">
                <el-icon><Switch /></el-icon>
                {{ scope.row.is_active ? '禁用' : '启用' }}
              </el-button>
              <el-button link type="danger" @click="confirmDeleteInviteCode(scope.row)">
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
          :total="totalCodes"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 生成邀请码对话框 -->
    <el-dialog v-model="showCreateDialog" title="生成邀请码" width="500px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="最大使用次数" prop="max_uses">
          <el-input-number v-model="createForm.max_uses" :min="1" :max="999" />
        </el-form-item>
        <el-form-item label="过期时间" prop="expire_hours">
          <el-input-number v-model="createForm.expire_hours" :min="1" :max="8760" placeholder="小时，留空为永不过期" />
          <div class="form-tip">设置邀请码有效期，单位：小时（1-8760），留空表示永不过期</div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="createForm.description" type="textarea" placeholder="邀请码用途描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createInviteCode" :loading="createLoading">生成</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑邀请码对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑邀请码" width="500px">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="最大使用次数" prop="max_uses">
          <el-input-number v-model="editForm.max_uses" :min="editForm.current_uses" :max="999" />
          <div class="form-tip">不能小于当前已使用次数（{{ editForm.current_uses }}）</div>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" placeholder="邀请码用途描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="updateInviteCode" :loading="updateLoading">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { getRequest, postRequest, putRequest, deleteRequest } from '@/utils/http';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Ticket, Plus, Refresh, Edit, Delete, Switch, CopyDocument } from '@element-plus/icons-vue';

const loading = ref(false);
const createLoading = ref(false);
const updateLoading = ref(false);
const inviteCodes = ref<any[]>([]);
const showCreateDialog = ref(false);
const showEditDialog = ref(false);
const statusFilter = ref('all');
const currentPage = ref(1);
const pageSize = ref(20);
const totalCodes = ref(0);

// 统计数据
const stats = ref({
  total_codes: 0,
  used_codes: 0,
  active_codes: 0,
  expired_codes: 0
});

const statistics = computed(() => [
  { label: '总邀请码', value: stats.value.total_codes, icon: 'Ticket', color: '#1677ff' },
  { label: '活跃邀请码', value: stats.value.active_codes, icon: 'CircleCheck', color: '#52c41a' },
  { label: '已使用', value: stats.value.used_codes, icon: 'User', color: '#722ed1' },
  { label: '已过期', value: stats.value.expired_codes, icon: 'Clock', color: '#f5222d' }
]);

// 生成邀请码表单
const createForm = reactive({
  max_uses: 1,
  expire_hours: null as number | null,
  description: ''
});

const createRules = {
  max_uses: [{ required: true, message: '请输入最大使用次数', trigger: 'blur' }]
};

// 编辑邀请码表单
const editForm = reactive({
  id: 0,
  max_uses: 1,
  current_uses: 0,
  is_active: true,
  description: ''
});

const editRules = {
  max_uses: [{ required: true, message: '请输入最大使用次数', trigger: 'blur' }]
};

const createFormRef = ref();
const editFormRef = ref();

// 获取邀请码列表
async function fetchInviteCodes() {
  loading.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString()
    });

    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/invite_codes?${params.toString()}`);
    if (response.code === 200 && response.data) {
      inviteCodes.value = response.data[0].invite_codes || [];
      totalCodes.value = response.data[0].total || 0;
    } else {
      ElMessage.error(response.message || '获取邀请码列表失败');
    }
  } catch (error) {
    console.error('获取邀请码列表出错:', error);
    ElMessage.error('获取邀请码列表出错');
  } finally {
    loading.value = false;
  }
}

// 获取统计信息
async function fetchStats() {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/invite_code_stats`);
    if (response.code === 200 && response.data) {
      stats.value = response.data[0];
    }
  } catch (error) {
    console.error('获取统计信息出错:', error);
  }
}

// 生成邀请码
async function createInviteCode() {
  if (!createFormRef.value) return;
  
  try {
    await createFormRef.value.validate();
    createLoading.value = true;
    
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const requestData: {
      max_uses: number;
      description?: string;
      expire_hours?: number;
    } = {
      max_uses: createForm.max_uses,
      description: createForm.description || undefined
    };
    
    if (createForm.expire_hours !== null) {
      requestData.expire_hours = createForm.expire_hours;
    }
    
    const response = await postRequest<any>(`${baseURL}/v1/api/mark/admin/generate_invite_code`, requestData);
    
    if (response.code === 200) {
      ElMessage.success('邀请码生成成功');
      showCreateDialog.value = false;
      
      // 重置表单
      createForm.max_uses = 1;
      createForm.expire_hours = null;
      createForm.description = '';
      
      // 刷新列表和统计
      fetchInviteCodes();
      fetchStats();
    } else {
      ElMessage.error(response.message || '生成邀请码失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '生成邀请码失败');
  } finally {
    createLoading.value = false;
  }
}

// 编辑邀请码
function editInviteCode(inviteCode: any) {
  editForm.id = inviteCode.id;
  editForm.max_uses = inviteCode.max_uses;
  editForm.current_uses = inviteCode.current_uses;
  editForm.is_active = inviteCode.is_active;
  editForm.description = inviteCode.description || '';
  showEditDialog.value = true;
}

// 更新邀请码
async function updateInviteCode() {
  if (!editFormRef.value) return;
  
  try {
    await editFormRef.value.validate();
    updateLoading.value = true;
    
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await putRequest<any>(`${baseURL}/v1/api/mark/admin/invite_code/${editForm.id}`, {
      max_uses: editForm.max_uses,
      is_active: editForm.is_active,
      description: editForm.description || undefined
    });
    
    if (response.code === 200) {
      ElMessage.success('邀请码更新成功');
      showEditDialog.value = false;
      fetchInviteCodes();
      fetchStats();
    } else {
      ElMessage.error(response.message || '更新邀请码失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '更新邀请码失败');
  } finally {
    updateLoading.value = false;
  }
}

// 切换邀请码状态
function toggleInviteCodeStatus(inviteCode: any) {
  editForm.id = inviteCode.id;
  editForm.max_uses = inviteCode.max_uses;
  editForm.current_uses = inviteCode.current_uses;
  editForm.is_active = !inviteCode.is_active;
  editForm.description = inviteCode.description || '';
  updateInviteCode();
}

// 删除邀请码
async function deleteInviteCode(inviteCode: any) {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await deleteRequest<any>(`${baseURL}/v1/api/mark/admin/delete_invite_code/${inviteCode.id}`);
    
    if (response.code === 200) {
      ElMessage.success('邀请码删除成功');
      fetchInviteCodes();
      fetchStats();
    } else {
      ElMessage.error(response.message || '删除邀请码失败');
    }
  } catch (error: any) {
    ElMessage.error(error.message || '删除邀请码失败');
  }
}

// 确认删除邀请码
function confirmDeleteInviteCode(inviteCode: any) {
  ElMessageBox.confirm(
    `此操作将永久删除邀请码 "${inviteCode.code}", 是否继续?`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteInviteCode(inviteCode);
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

// 复制邀请码
function copyCode(code: string) {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('邀请码已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
}

// 获取状态类型
function getStatusType(inviteCode: any) {
  if (!inviteCode.is_active) return 'info';
  if (inviteCode.current_uses >= inviteCode.max_uses) return 'success';
  if (inviteCode.expire_at && new Date(inviteCode.expire_at) < new Date()) return 'danger';
  return 'success';
}

// 获取状态文本
function getStatusText(inviteCode: any) {
  if (!inviteCode.is_active) return '已禁用';
  if (inviteCode.current_uses >= inviteCode.max_uses) return '已用完';
  if (inviteCode.expire_at && new Date(inviteCode.expire_at) < new Date()) return '已过期';
  return '活跃';
}

// 格式化日期
function formatDate(dateString: string | null | undefined) {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleString();
  } catch (e) {
    return dateString;
  }
}

// 处理分页大小变化
function handleSizeChange(size: number) {
  pageSize.value = size;
  currentPage.value = 1;
  fetchInviteCodes();
}

// 处理页码变化
function handleCurrentChange(page: number) {
  currentPage.value = page;
  fetchInviteCodes();
}

// 页面加载时获取数据
onMounted(() => {
  fetchInviteCodes();
  fetchStats();
});
</script>

<style scoped>
.invite-container {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #eee;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  border-left: 4px solid var(--stat-color);
}

.stat-icon {
  background: color-mix(in srgb, var(--stat-color) 15%, transparent);
  color: var(--stat-color);
  border-radius: 8px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.search-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-container {
  margin-bottom: 24px;
}

.code-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-text {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  flex: 1;
  word-break: break-all;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .invite-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
