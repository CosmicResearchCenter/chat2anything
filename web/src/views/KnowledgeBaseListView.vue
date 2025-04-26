<template>
    <el-row :gutter="24" class="kb-list-container">
        <!-- Create new knowledge base card -->
        <el-col :xs="24" :sm="12" :md="8" :lg="6" class="col-card">
            <el-card class="new-base-card" shadow="never" @click="openDialog">
                <div class="new-base-content">
                    <el-icon class="add-icon" :size="40"><Plus /></el-icon>
                    <div class="add-text">创建新知识库</div>
                </div>
            </el-card>
        </el-col>

        <!-- Dynamic cards for knowledge bases -->
        <el-col v-for="kb in files" :key="kb.id" :xs="24" :sm="12" :md="8" :lg="6" class="col-card">
            <el-card class="kb-card" shadow="hover" @click="goToKnowledgeBase(kb.id)">
                <div class="kb-card-header">
                    <el-icon class="kb-icon" :size="30"><Document /></el-icon>
                    <div class="kb-actions" @click.stop>
                        <el-dropdown trigger="click">
                            <span class="el-dropdown-link action-icon" @click.stop>
                                <el-icon><MoreFilled /></el-icon>
                            </span>
                            <template #dropdown>
                                <el-dropdown-menu>
                                    <el-dropdown-item 
                                        :icon="Delete" 
                                        @click.stop="handleMenuCommand(kb)('delete')">
                                        删除
                                    </el-dropdown-item>
                                </el-dropdown-menu>
                            </template>
                        </el-dropdown>
                    </div>
                </div>
                <div class="kb-card-body">
                    <div class="kb-name">{{ kb.name }}</div>
                    <div class="kb-details">{{ kb.details }}</div>
                </div>
            </el-card>
        </el-col>
    </el-row>

    <!-- Dialog remains the same -->
    <el-dialog title="设置知识库名称" v-model="dialogVisible" width="300px">
        <el-input v-model="knowledgeBaseName" placeholder="请输入知识库名称" clearable></el-input>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="createKnowledgeBase" :loading="isCreating">确定</el-button>
            </span>
        </template>
    </el-dialog>
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
.kb-list-container {
    padding: 24px;
    background-color: #f5f7fa; /* Match background */
    min-height: calc(100vh - 60px); /* Adjust based on nav height */
}

.col-card {
    margin-bottom: 24px;
}

/* Base card style */
.el-card {
    border-radius: 12px;
    border: 1px solid #e4e7ed;
    transition: all 0.3s ease;
    cursor: pointer;
    height: 160px; /* Fixed height for consistency */
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
}

.el-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* "Create New" Card Style */
.new-base-card {
    border: 2px dashed #0245a3; /* Use theme color for dashed border */
    background-color: #f8fcff; /* Lighter background */
    justify-content: center;
    align-items: center;
}

.new-base-card:hover {
    border-color: #8fbaf3; /* Lighter blue on hover */
    background-color: #ffffff;
}

.new-base-content {
    text-align: center;
    color: #0245a3; /* Theme color */
}

.add-icon {
    margin-bottom: 10px;
    transition: transform 0.3s ease;
}

.new-base-card:hover .add-icon {
    transform: scale(1.1);
}

.add-text {
    font-size: 16px;
    font-weight: 500;
}

/* Knowledge Base Card Style */
.kb-card {
    position: relative;
    padding: 18px;
    box-sizing: border-box;
}

.kb-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start; /* Align items to the top */
    margin-bottom: 15px;
}

.kb-icon {
    color: #0245a3; /* Theme color */
    background-color: rgba(143, 186, 243, 0.15); /* Light blue background */
    border-radius: 8px;
    padding: 6px;
}

.kb-actions {
    position: absolute;
    top: 15px;
    right: 15px;
}

.action-icon {
    color: #909399; /* Grey color for icon */
    cursor: pointer;
    padding: 5px;
    border-radius: 50%;
    transition: background-color 0.2s ease, color 0.2s ease;
}

.action-icon:hover {
    background-color: #f0f0f0;
    color: #0245a3; /* Theme color on hover */
}

.kb-card-body {
    margin-top: auto; /* Push body content towards the bottom */
}

.kb-name {
    font-size: 17px;
    font-weight: 600;
    color: #303133; /* Darker text for name */
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis; /* Add ellipsis for long names */
}

.kb-details {
    font-size: 13px;
    color: #606266; /* Grey text for details */
    line-height: 1.4;
}

/* Dialog style */
.dialog-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 10px; /* Add some space above buttons */
}

/* Responsive adjustments */
@media screen and (max-width: 768px) {
  .kb-list-container {
    padding: 16px;
  }
  .col-card {
     /* Make cards full width on smaller screens if needed */
     /* :xs="24" already handles this */
  }
  .el-card {
      height: 150px; /* Slightly smaller height */
  }
  .kb-name {
      font-size: 16px;
  }
  .kb-details {
      font-size: 12px;
  }
}
</style>