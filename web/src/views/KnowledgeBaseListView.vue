<template>
  <div class="kb-list-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">知识库管理</h1>
          <p class="page-subtitle">管理您的知识库，组织和存储文档内容</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" class="create-btn" @click="openDialog" :icon="Plus">
            创建新知识库
          </el-button>
        </div>
      </div>
    </div>

    <!-- 知识库列表 -->
    <div class="kb-grid-container">
      <!-- 创建卡片 -->
      <div class="kb-card create-card interactive" @click="openDialog">
        <div class="create-content">
          <div class="create-icon-wrapper">
            <el-icon class="create-icon" :size="32"><Plus /></el-icon>
          </div>
          <div class="create-text">创建新知识库</div>
          <div class="create-hint">点击开始创建</div>
        </div>
      </div>

      <!-- 知识库卡片 -->
      <div
        v-for="kb in files"
        :key="kb.id"
        class="kb-card interactive"
        @click="goToKnowledgeBase(kb.id)"
      >
        <div class="kb-card-header">
          <div class="kb-icon-wrapper">
            <el-icon class="kb-icon" :size="24"><Document /></el-icon>
          </div>
          <div class="kb-actions" @click.stop>
            <el-dropdown trigger="click" placement="bottom-end">
              <div class="action-btn">
                <el-icon><MoreFilled /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="custom-dropdown">
                  <el-dropdown-item
                    :icon="Delete"
                    class="delete-item"
                    @click.stop="handleMenuCommand(kb)('delete')">
                    删除知识库
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="kb-card-body">
          <div class="kb-name text-ellipsis">{{ kb.name }}</div>
          <div class="kb-stats">
            <span class="stat-item">
              <el-icon><Document /></el-icon>
              {{ kb.details }}
            </span>
          </div>
        </div>

        <div class="kb-card-footer">
          <div class="kb-actions-row">
            <el-button
              link
              type="primary"
              size="small"
              @click.stop="goToKnowledgeBase(kb.id)"
            >
              进入管理
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="files.length === 0 && !dialogVisible" class="empty-state">
      <div class="empty-content">
        <el-icon class="empty-icon" :size="64"><Document /></el-icon>
        <div class="empty-title">暂无知识库</div>
        <div class="empty-description">创建您的第一个知识库来开始管理文档</div>
        <el-button type="primary" @click="openDialog" :icon="Plus" class="empty-btn">
          创建知识库
        </el-button>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建新知识库"
      width="420px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <div class="form-group">
          <label class="form-label">知识库名称</label>
          <el-input
            v-model="knowledgeBaseName"
            placeholder="请输入知识库名称"
            clearable
            size="large"
            @keyup.enter="createKnowledgeBase"
          >
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
          <div class="form-hint">建议使用简洁明确的名称，如"产品文档"、"技术手册"</div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="createKnowledgeBase"
            :loading="isCreating"
            size="large"
          >
            {{ isCreating ? '创建中...' : '确认创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// Import MoreFilled and Delete icons
import { Plus, Document, MoreFilled, Delete } from '@element-plus/icons-vue'; 
import { getRequest, postRequest, deleteRequest } from '@/utils/http';
import { ElMessage, ElMessageBox } from 'element-plus'; // Import ElMessageBox

interface FileData {
    id: string;
    name: string;
    details: string;
}

export default defineComponent({
    // Add MoreFilled and Delete to components
    components: { Plus, Document, MoreFilled, Delete }, 
    setup() {
        const router = useRouter();

        const files = ref<FileData[]>([]);
        const dialogVisible = ref(false); 
        const knowledgeBaseName = ref(""); 
        const isCreating = ref(false); 

        const openDialog = () => {
            knowledgeBaseName.value = ""; // Clear previous input
            dialogVisible.value = true;
        };

        const fetchKnowledgeBases = async () => {
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL+'/v1/api/mark/knowledgebase/');
                if (response.code === 200) {
                    files.value = response.data.map((kb: any) => ({
                        id: kb.id,
                        name: kb.knowledgeBaseName,
                        // Ensure details are strings
                        details: `${kb.docs_num || 0}个文档 | ${kb.related_conversations || 0}个关联对话` 
                    }));
                } else {
                    ElMessage.error('获取知识库列表失败: ' + response.message);
                }
            } catch (error) {
                console.error('请求失败:', error);
                ElMessage.error('请求知识库列表时出错');
            }
        };

        onMounted(fetchKnowledgeBases);

        const createKnowledgeBase = async () => {
            if (!knowledgeBaseName.value.trim()) {
                ElMessage.warning('请输入知识库名称');
                return;
            }
            if (isCreating.value) return; 
            isCreating.value = true;
            
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await postRequest(baseURL+'/v1/api/mark/knowledgebase/', {
                    base_name: knowledgeBaseName.value.trim() // Use trimmed value
                });

                if (response.code === 200 && response.data.length > 0) {
                    const newKb = response.data[0];
                    ElMessage.success(`知识库 "${newKb.knowledgeBaseName}" 创建成功`);
                    dialogVisible.value = false;
                    await fetchKnowledgeBases(); // Refresh list after creation
                    // Optionally navigate to the new KB's creation page immediately
                    // router.push(`/manager/${newKb.knowledgeBase_id}/create`); 
                } else {
                     ElMessage.error('创建知识库失败: ' + response.message);
                }
            } catch (error) {
                console.error('请求创建知识库失败:', error);
                ElMessage.error('请求创建知识库时出错');
            } finally {
                isCreating.value = false; 
            }
        };

        const goToKnowledgeBase = (id: string) => {
            router.push(`/manager/${id}`);
        };

        // Updated handleMenuCommand to use ElMessageBox for confirmation
        const handleMenuCommand = (kb: FileData) => async (command: string) => {
            if (command === 'delete') {
                ElMessageBox.confirm(
                    `确定要删除知识库 "${kb.name}" 吗？此操作不可恢复。`,
                    '确认删除',
                    {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning',
                    }
                ).then(async () => {
                    // User confirmed deletion
                    try {
                        const baseURL = import.meta.env.VITE_APP_BASE_URL;
                        const response: any = await deleteRequest(baseURL+`/v1/api/mark/knowledgebase/${kb.id}`);
                        if (response.code === 200) {
                            ElMessage.success(`知识库 "${kb.name}" 已删除`);
                            await fetchKnowledgeBases(); // Refresh list
                        } else {
                            ElMessage.error('删除失败: ' + response.message);
                        }
                    } catch (error) {
                        console.error('删除请求失败:', error);
                        ElMessage.error('删除知识库时出错');
                    }
                }).catch(() => {
                    // User cancelled
                    ElMessage.info('已取消删除');
                });
            }
            // Add other commands like 'settings' here if needed in the future
            // else if (command === 'settings') { ... }
        };

        return {
            files,
            dialogVisible,
            knowledgeBaseName,
            openDialog,
            createKnowledgeBase,
            goToKnowledgeBase,
            handleMenuCommand,
            isCreating,
            // Expose icons to template
            Delete 
        };
    }
});
</script>

<style scoped>
/* 页面容器 */
.kb-list-page {
  width: 100%;
  min-height: 100%;
  background: var(--bg-main);
  padding: 0;
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

.create-btn {
  background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
  border: none;
  box-shadow: 0 4px 12px rgba(2, 69, 163, 0.25);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  padding: 12px 20px;
  transition: all var(--duration-normal) ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(2, 69, 163, 0.35);
}

/* 知识库网格容器 */
.kb-grid-container {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 32px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  min-height: calc(100vh - 200px);
}

/* 卡片基础样式 */
.kb-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-normal) ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  min-height: 180px;
}

.kb-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-300);
}

/* 创建卡片特殊样式 */
.create-card {
  background: linear-gradient(135deg, var(--primary-50), rgba(58, 122, 254, 0.05));
  border: 2px dashed var(--primary-400);
  cursor: pointer;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.create-card:hover {
  background: linear-gradient(135deg, var(--primary-100), rgba(58, 122, 254, 0.1));
  border-color: var(--primary-600);
  transform: translateY(-2px) scale(1.02);
}

.create-content {
  text-align: center;
  padding: 24px;
}

.create-icon-wrapper {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: var(--primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-normal) ease;
}

.create-card:hover .create-icon-wrapper {
  transform: scale(1.1);
  background: var(--primary-600);
  box-shadow: 0 0 20px rgba(58, 122, 254, 0.4);
}

.create-icon {
  color: white;
}

.create-text {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--primary-700);
  margin-bottom: 4px;
}

.create-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 知识库卡片内容 */
.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 16px 12px 16px;
  border-bottom: 1px solid var(--border-light);
}

.kb-icon-wrapper {
  width: 40px;
  height: 40px;
  background: var(--primary-50);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-normal) ease;
}

.kb-card:hover .kb-icon-wrapper {
  background: var(--primary-100);
  transform: scale(1.05);
}

.kb-icon {
  color: var(--primary-600);
}

.kb-actions {
  position: relative;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-tertiary);
  transition: all var(--duration-fast) ease;
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--primary-600);
  transform: scale(1.1);
}

.kb-card-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kb-name {
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0;
}

.kb-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--gray-50);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  width: fit-content;
}

.stat-item .el-icon {
  font-size: 14px;
  color: var(--text-tertiary);
}

.kb-card-footer {
  padding: 12px 16px 16px 16px;
  border-top: 1px solid var(--border-light);
  background: var(--bg-main);
}

.kb-actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 空状态 */
.empty-state {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 80px 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  color: var(--gray-300);
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-title {
  font-size: 20px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.empty-btn {
  background: linear-gradient(135deg, var(--primary-600), var(--primary-500));
  border: none;
  box-shadow: 0 4px 12px rgba(2, 69, 163, 0.25);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  padding: 12px 24px;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog) {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}

.custom-dialog :deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-card);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.custom-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.custom-dialog :deep(.el-dialog__body) {
  padding: 24px;
  background: var(--bg-card);
}

.dialog-content {
  padding: 0 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.form-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
  margin-top: 4px;
}

.custom-dialog :deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  box-shadow: none;
  transition: all var(--duration-fast) ease;
  padding: 12px 16px;
}

.custom-dialog :deep(.el-input__wrapper:hover) {
  border-color: var(--primary-300);
  background: var(--bg-hover);
}

.custom-dialog :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-50);
}

.custom-dialog :deep(.el-input__prefix) {
  color: var(--primary-600);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px 24px;
  background: var(--bg-card);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

/* 下拉菜单自定义 */
.custom-dropdown :deep(.el-dropdown-menu) {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-light);
  padding: 4px 0;
}

.custom-dropdown :deep(.el-dropdown-menu__item) {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 4px;
  margin: 2px 4px;
}

.custom-dropdown :deep(.el-dropdown-menu__item:hover) {
  background: var(--bg-hover);
}

.custom-dropdown :deep(.delete-item) {
  color: var(--danger-500);
}

.custom-dropdown :deep(.delete-item:hover) {
  background: rgba(245, 34, 45, 0.1);
  color: var(--danger-500);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .kb-grid-container {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px 20px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .kb-grid-container {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px 20px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 13px;
  }

  .empty-state {
    padding: 60px 20px;
  }

  .custom-dialog :deep(.el-dialog) {
    width: 90% !important;
    margin: 15vh auto !important;
  }
}

@media (max-width: 480px) {
  .kb-grid-container {
    padding: 12px 16px;
    gap: 12px;
  }

  .kb-card {
    min-height: 160px;
  }

  .kb-card-header,
  .kb-card-body,
  .kb-card-footer {
    padding: 12px;
  }

  .create-card {
    min-height: 140px;
  }

  .create-icon-wrapper {
    width: 52px;
    height: 52px;
  }

  .create-text {
    font-size: 15px;
  }

  .dialog-footer {
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px 16px 16px;
  }

  .dialog-footer .el-button {
    width: 100%;
  }
}

/* 深色模式适配 */
[data-theme="dark"] .page-header {
  background: rgba(26, 31, 38, 0.95);
  border-bottom-color: var(--border-light);
}

[data-theme="dark"] .kb-card {
  background: var(--bg-card);
  border-color: var(--border-light);
}

[data-theme="dark"] .create-card {
  background: linear-gradient(135deg, rgba(58, 122, 254, 0.1), rgba(58, 122, 254, 0.05));
  border-color: var(--primary-400);
}

[data-theme="dark"] .create-card:hover {
  background: linear-gradient(135deg, rgba(58, 122, 254, 0.15), rgba(58, 122, 254, 0.1));
}

[data-theme="dark"] .stat-item {
  background: var(--bg-elevated);
}

[data-theme="dark"] .custom-dialog :deep(.el-input__wrapper:hover) {
  background: var(--bg-elevated);
}

/* 动画效果 */
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kb-card {
  animation: cardAppear 0.4s ease forwards;
}

.kb-card:nth-child(1) { animation-delay: 0.05s; }
.kb-card:nth-child(2) { animation-delay: 0.1s; }
.kb-card:nth-child(3) { animation-delay: 0.15s; }
.kb-card:nth-child(4) { animation-delay: 0.2s; }

/* 微交互 */
.interactive {
  cursor: pointer;
  user-select: none;
}

.interactive:active {
  transform: scale(0.98);
}

/* 滚动条美化 */
.kb-grid-container::-webkit-scrollbar {
  width: 8px;
}

.kb-grid-container::-webkit-scrollbar-track {
  background: transparent;
}

.kb-grid-container::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 4px;
}

.kb-grid-container::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .kb-card {
    border-width: 2px;
  }

  .create-card {
    border-width: 3px;
  }

  .page-header {
    border-bottom-width: 2px;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .kb-card,
  .create-card,
  .create-icon-wrapper,
  .kb-icon-wrapper {
    animation: none !important;
    transition: none !important;
  }
}

/* 打印样式 */
@media print {
  .page-header {
    position: static;
    background: white;
    border-bottom: 2px solid #000;
  }

  .kb-grid-container {
    grid-template-columns: 1fr 1fr;
  }

  .kb-card {
    break-inside: avoid;
    box-shadow: none;
    border: 1px solid #000;
  }

  .create-card,
  .kb-actions,
  .kb-card-footer,
  .header-actions {
    display: none !important;
  }
}
</style>