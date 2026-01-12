<template>
    <el-container class="page-container">
        <!-- Sidebar -->
        <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
            <div class="sidebar-header" :class="{ 'collapsed': isCollapse }">
                <div class="logo">
                    <el-icon><Monitor /></el-icon>
                    <span v-if="!isCollapse" class="logo-text">{{ settings.knowledgeBaseName || '知识库' }}</span>
                </div>
            </div>
            <el-menu 
                :default-active="activeMenu" 
                class="sidebar-menu" 
                :collapse="isCollapse"
                background-color="transparent" 
                text-color="#a6adb4" 
                active-text-color="#ffffff"
                :collapse-transition="false"
            >
                <el-menu-item index="1" @click="toggleSwitch('1')" class="menu-item">
                    <el-icon><Document /></el-icon>
                    <template #title>
                        <span class="menu-text">文档管理</span>
                    </template>
                </el-menu-item>
                <el-menu-item index="2" @click="toggleSwitch('2')" class="menu-item">
                    <el-icon><Setting /></el-icon>
                    <template #title>
                        <span class="menu-text">知识库设置</span>
                    </template>
                </el-menu-item>
            </el-menu>
            <div class="sidebar-footer">
                <el-button class="collapse-btn" text @click="toggleCollapse">
                    <el-icon :size="20">
                        <Fold v-if="!isCollapse" />
                        <Expand v-else />
                    </el-icon>
                </el-button>
            </div>
        </el-aside>

        <!-- Main content -->
        <el-main class="main-content">
            <!-- Document Management View -->
            <div v-if="switchButton === '1'" class="content-wrapper document-view">
                <el-card shadow="never" class="content-card">
                    <template #header>
                        <div class="card-header">
                            <span>文档列表</span>
                            <div class="header-actions">
                                <el-input 
                                    v-model="searchText" 
                                    placeholder="搜索文档..." 
                                    class="search-input" 
                                    clearable 
                                    :prefix-icon="Search"
                                />
                                <el-button type="primary" @click="addFile" :icon="Plus">添加文件</el-button>
                            </div>
                        </div>
                    </template>
                    
                    <el-table :data="filteredFiles" style="width: 100%" class="file-table" height="calc(100vh - 260px)">
                        <el-table-column type="index" label="#" width="50" align="center"></el-table-column>
                        <el-table-column prop="name" label="文件名" min-width="250" sortable>
                            <template #default="scope">
                                <div class="file-info">
                                    <el-icon class="file-icon"><Document /></el-icon>
                                    <span class="file-name">{{ scope.row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>
                        <el-table-column prop="size" label="大小" width="120" align="center" sortable></el-table-column>
                        <el-table-column prop="uploadDate" label="上传时间" width="180" align="center" sortable></el-table-column>
                        <el-table-column prop="status" label="状态" width="100" align="center">
                            <template #default="scope">
                                <el-tag :type="scope.row.status === '可用' ? 'success' : 'warning'" size="small" effect="light">
                                    {{ scope.row.status }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="100" align="center">
                            <template #default="scope">
                                <el-dropdown trigger="click" @command="(command: string) => handleFileAction(command, scope.row.docId)">
                                    <el-button text type="primary" :icon="MoreFilled" class="action-more-btn"></el-button>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item command="rename" :icon="EditPen">重命名</el-dropdown-item>
                                            <el-dropdown-item command="reindex" :icon="Refresh">重新索引</el-dropdown-item>
                                            <el-dropdown-item command="delete" :icon="Delete" divided class="delete-item">删除</el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </div>

            <!-- Settings View -->
            <div v-else class="content-wrapper settings-view">
                 <el-card shadow="never" class="content-card settings-card">
                    <template #header>
                        <div class="card-header">
                            <span>知识库设置</span>
                        </div>
                    </template>
                    <el-form :model="settings" label-width="140px" label-position="right">
                        <el-form-item label="知识库名称">
                            <el-input v-model="settings.knowledgeBaseName" placeholder="请输入知识库名称" />
                        </el-form-item>

                        <el-divider content-position="left">检索配置</el-divider>
                        
                        <el-form-item label="RAG模式">
                            <el-radio-group v-model="settings.rag_model">
                                <el-radio :label="0">混合检索</el-radio>
                                <el-radio :label="1">向量检索</el-radio>
                                <el-radio :label="2">模糊检索</el-radio>
                            </el-radio-group>
                             <el-tooltip content="混合检索结合向量和关键词搜索；向量检索仅使用语义相似度；模糊检索仅使用关键词匹配。" placement="top">
                                <el-icon class="info-icon"><InfoFilled /></el-icon>
                            </el-tooltip>
                        </el-form-item>
                        <el-form-item label="启用二阶段重排">
                            <el-switch v-model="settings.is_rerank" />
                             <el-tooltip content="对初步检索结果进行更精细的排序，提高相关性，但可能增加延迟。" placement="top">
                                <el-icon class="info-icon"><InfoFilled /></el-icon>
                            </el-tooltip>
                        </el-form-item>
                        <el-form-item>
                            <el-button type="primary" @click="saveSettings" :loading="isSavingSettings">保存设置</el-button>
                        </el-form-item>
                        <!-- Admin Only Section -->
                        <template v-if="isAdmin">
                            <el-divider content-position="left">访问权限</el-divider>
                            <el-form-item label="公开知识库">
                                <el-switch v-model="settings.is_public" @change="togglePublicStatus" />
                                <span class="setting-desc">公开后其他注册用户可访问此知识库</span>
                                <el-tooltip content="允许其他用户在问答中使用此知识库的数据。" placement="top">
                                    <el-icon class="info-icon"><InfoFilled /></el-icon>
                                </el-tooltip>
                            </el-form-item>
                        </template>

                        
                    </el-form>
                </el-card>
            </div>
        </el-main>

        <!-- Dialogs remain unchanged, but ensure they are styled consistently if needed -->
        <el-dialog v-model="renameDialogVisible" title="重命名文档" width="400px" :close-on-click-modal="false">
            <el-form :model="renameForm" ref="renameFormRef" label-width="80px">
                <el-form-item label="新文件名" prop="newDocName" :rules="[{ required: true, message: '请输入新的文档名', trigger: 'blur' }]">
                    <el-input v-model="renameForm.newDocName" placeholder="请输入新的文档名"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="renameDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="confirmRename">确定</el-button>
                </span>
            </template>
        </el-dialog>

        <el-dialog v-model="reindexDialogVisible" title="重新索引文档" width="500px" :close-on-click-modal="false">
            <el-form label-width="100px">
                <el-form-item label="分割模型">
                    <el-radio-group v-model="reindexSplitterModel">
                        <el-radio :label="0">LLMSplitter</el-radio>
                        <el-radio :label="1">TextSplitter</el-radio>
                    </el-radio-group>
                </el-form-item>
                <!-- LLMSplitter Args -->
                <div v-if="reindexSplitterModel === 0">
                    <el-form-item label="窗口大小">
                        <el-input v-model="reindexWindowSize" placeholder="建议值: 2000-2500"></el-input>
                    </el-form-item>
                    <el-form-item label="步长">
                        <el-input v-model="reindexStepSize" placeholder="建议值: 1500-1800"></el-input>
                    </el-form-item>
                </div>
                <!-- TextSplitter Args -->
                <div v-if="reindexSplitterModel === 1">
                    <el-form-item label="块大小">
                        <el-input v-model="reindexChunkSize" placeholder="建议值: 500-600"></el-input>
                    </el-form-item>
                    <el-form-item label="重叠大小">
                        <el-input v-model="reindexChunkOverlap" placeholder="建议值: 100-200"></el-input>
                    </el-form-item>
                </div>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="reindexDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="confirmReindex" :loading="isReindexing">确定</el-button>
                </span>
            </template>
        </el-dialog>
    </el-container>
</template>

<script lang="ts">
// Import necessary icons
import { defineComponent, ref, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { getRequest, postRequest, deleteRequest, putRequest } from '@/utils/http';
import { 
    Monitor, Document, Setting, Fold, Expand, Search, Plus, MoreFilled, EditPen, Refresh, Delete, InfoFilled 
} from '@element-plus/icons-vue';

// ... (interface File definition remains the same) ...
interface File {
    index: number;
    name: string;
    size: string;
    uploadDate: string;
    status: string;
    docId: string;
}

export default defineComponent({
    // Register imported icons
    components: { Monitor, Document, Setting, Fold, Expand, Search, Plus, MoreFilled, EditPen, Refresh, Delete, InfoFilled },
    setup() {
        const router = useRouter();
        const route = useRoute();
        const switchButton = ref('1'); // '1' for documents, '2' for settings
        const activeMenu = ref('1');
        const searchText = ref('');
        const files = ref<File[]>([]);
        const isCollapse = ref(false);
        const isAdmin = ref(false);
        const isSavingSettings = ref(false); // Loading state for saving settings
        const isReindexing = ref(false); // Loading state for reindexing

        const settings = ref({
            knowledgeBaseId: "",
            knowledgeBaseName: '',
            rag_model: 0,
            is_rerank: false,
            is_public: false
        });

        // Computed property to filter files based on search text
        const filteredFiles = computed(() => {
            if (!searchText.value) {
                return files.value;
            }
            return files.value.filter(file => 
                file.name.toLowerCase().includes(searchText.value.toLowerCase())
            );
        });

        const fetchFiles = async () => {
            const baseId = route.params.base_id as string;
            if (!baseId) return;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}`);
                if (response.code === 200) {
                    // Fetch status for all docs concurrently
                    const statusPromises = response.data.map((doc: any) => 
                        getRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}/doc/${doc.doc_id}/index_status`)
                    );
                    const statusResponses = await Promise.all(statusPromises);

                    files.value = response.data.map((doc: any, index: number) => {
                        const statusRes = statusResponses[index];
                        const status = statusRes.code === 200 && statusRes.data?.[0]?.index_status === 1 ? '可用' : '处理中';
                        return {
                            index: index + 1,
                            name: doc.doc_name,
                            size: (doc.doc_size / 1024).toFixed(1) + ' KB', // More standard unit
                            uploadDate: new Date(doc.create_time).toLocaleString(),
                            status,
                            docId: doc.doc_id
                        };
                    });
                    // No success message needed here, it's just data fetching
                } else {
                    ElMessage.error("获取文档列表失败: " + response.message);
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("获取文档列表时出错");
            }
        };

        const get_kb_config = async () => {
            const baseId = route.params.base_id as string;
             if (!baseId) return;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}/config`);
                if (response.code === 200 && response.data.length > 0) {
                    // Assign fetched settings, ensuring defaults if properties are missing
                    const fetchedSettings = response.data[0];
                    settings.value = {
                        knowledgeBaseId: fetchedSettings.knowledgeBaseId || baseId,
                        knowledgeBaseName: fetchedSettings.knowledgeBaseName || '',
                        rag_model: fetchedSettings.rag_model ?? 0, // Default to 0 if null/undefined
                        is_rerank: fetchedSettings.is_rerank ?? false,
                        is_public: fetchedSettings.is_public ?? false
                    };
                } else {
                    ElMessage.warning("未能获取知识库配置，将使用默认设置。");
                     // Set default name if fetch fails but baseId exists
                    settings.value.knowledgeBaseId = baseId;
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("获取知识库配置时出错");
                 settings.value.knowledgeBaseId = baseId; // Ensure ID is set even on error
            }
        };

        const checkIsAdmin = async () => {
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL + '/v1/api/mark/admin/me');
                isAdmin.value = response.code === 200;
            } catch (error) {
                console.error('检查管理员状态时出错:', error);
                isAdmin.value = false;
            }
        };

        const toggleSwitch = (menuIndex: string) => {
            if (switchButton.value !== menuIndex) {
                switchButton.value = menuIndex;
                activeMenu.value = menuIndex;
                // No need for ElMessage info on tab switch
            }
        };

        const addFile = () => {
            const baseId = route.params.base_id as string;
            router.push(`/manager/${baseId}/create`);
        };

        const saveSettings = async () => {
            const baseId = route.params.base_id as string;
            settings.value.knowledgeBaseId = baseId; // Ensure ID is correct
            isSavingSettings.value = true; // Start loading
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await putRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}/config`, settings.value);
                if (response.code === 200) {
                    ElMessage.success("设置已保存");
                    // Optionally re-fetch config if needed, but usually UI reflects changes
                    // await get_kb_config(); 
                } else {
                    ElMessage.error("保存设置失败: " + response.message);
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("保存设置时出错");
            } finally {
                isSavingSettings.value = false; // Stop loading
            }
        };

        // Combined handler for file actions from dropdown
        const handleFileAction = (command: string, docId: string) => {
            switch (command) {
                case 'rename':
                    openRenameDialog(docId);
                    break;
                case 'reindex':
                    openReindexDialog(docId);
                    break;
                case 'delete':
                    confirmDeleteFile(docId); // Use confirmation dialog
                    break;
            }
        };

        // Confirmation before deleting a file
        const confirmDeleteFile = (docId: string) => {
             const fileToDelete = files.value.find(f => f.docId === docId);
             if (!fileToDelete) return;

             ElMessageBox.confirm(
                `确定要删除文档 "${fileToDelete.name}" 吗？此操作将删除文档及其索引，且不可恢复。`,
                '确认删除',
                {
                    confirmButtonText: '确定删除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    confirmButtonClass: 'el-button--danger'
                }
            ).then(async () => {
                await deleteFile(docId);
            }).catch(() => {
                ElMessage.info('已取消删除');
            });
        };


        const deleteFile = async (docId: string) => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await deleteRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}/doc/${docId}`);
                if (response.code === 200) {
                    ElMessage.success("文件已删除");
                    fetchFiles(); // Refresh list
                } else {
                    ElMessage.error("删除文件失败: " + response.message);
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("删除文件时出错");
            }
        };

        const toggleCollapse = () => {
            isCollapse.value = !isCollapse.value;
        };

        // --- Rename Dialog ---
        const renameDialogVisible = ref(false);
        const renameFormRef = ref(); // Ref for form validation
        const renameForm = ref({ newDocName: '' });
        const currentDocId = ref(''); 

        const openRenameDialog = (docId: string) => {
            currentDocId.value = docId;
            const currentDoc = files.value.find(file => file.docId === docId);
            renameForm.value.newDocName = currentDoc ? currentDoc.name : '';
            renameDialogVisible.value = true;
            // Reset validation state if dialog was opened before
            renameFormRef.value?.resetFields(); 
        };

        const confirmRename = async () => {
            renameFormRef.value?.validate(async (valid: boolean) => {
                if (valid) {
                    const baseId = route.params.base_id as string;
                    try {
                        const baseURL = import.meta.env.VITE_APP_BASE_URL;
                        const response: any = await putRequest(baseURL + `/v1/api/mark/knowledgebase/${baseId}/doc/${currentDocId.value}/rename?new_name=${renameForm.value.newDocName}`, {});
                        if (response.code === 200) {
                            ElMessage.success("文件已重命名");
                            renameDialogVisible.value = false;
                            fetchFiles();
                        } else {
                            ElMessage.error("重命名文件失败: " + response.message);
                        }
                    } catch (error) {
                        console.error(error);
                        ElMessage.error("重命名文件时出错");
                    }
                } else {
                    console.log('Rename form validation failed');
                    return false;
                }
            });
        };

        // --- Reindex Dialog ---
        const reindexDialogVisible = ref(false);
        const currentReindexDocId = ref('');
        const reindexSplitterModel = ref(0); // 0: LLMSplitter, 1: TextSplitter
        const reindexWindowSize = ref('2000'); // Default LLMSplitter window_size
        const reindexStepSize = ref('1500');   // Default LLMSplitter step_size
        const reindexChunkSize = ref('500'); // Default TextSplitter chunk_size
        const reindexChunkOverlap = ref('200'); // Default TextSplitter chunk_overlap

        const openReindexDialog = (docId: string) => {
            currentReindexDocId.value = docId;
            // Reset to defaults or fetch current settings if available
            reindexSplitterModel.value = 0; 
            reindexWindowSize.value = '2000';
            reindexStepSize.value = '1500';
            reindexChunkSize.value = '500';
            reindexChunkOverlap.value = '200';
            reindexDialogVisible.value = true;
        };

        const confirmReindex = async () => {
            const baseId = route.params.base_id as string;
            let splitter_args = {};
            // Validate inputs basic check (can be more robust)
            if (reindexSplitterModel.value === 0) {
                 if (!reindexWindowSize.value || !reindexStepSize.value || isNaN(Number(reindexWindowSize.value)) || isNaN(Number(reindexStepSize.value))) {
                    ElMessage.warning('LLMSplitter 参数必须是有效的数字');
                    return;
                }
                splitter_args = {
                    window_size: reindexWindowSize.value,
                    step_size: reindexStepSize.value, 
                };
            } else {
                 if (!reindexChunkSize.value || !reindexChunkOverlap.value || isNaN(Number(reindexChunkSize.value)) || isNaN(Number(reindexChunkOverlap.value))) {
                    ElMessage.warning('TextSplitter 参数必须是有效的数字');
                    return;
                }
                splitter_args = {
                    chunk_size: reindexChunkSize.value,
                    chunk_overlap: reindexChunkOverlap.value
                };
            }

            const requestBody = {
                splitter_model: reindexSplitterModel.value,
                splitter_args: splitter_args
            };

            isReindexing.value = true; // Start loading
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await postRequest(
                    baseURL + `/v1/api/mark/knowledgebase/${baseId}/reindex/${currentReindexDocId.value}`,
                    requestBody
                );
                if (response.code === 200) {
                    ElMessage.success(response.message || "重新索引任务已启动");
                    reindexDialogVisible.value = false;
                    // Refresh file list to show updated status (likely '处理中')
                    fetchFiles(); 
                } else {
                    ElMessage.error("启动重新索引失败: " + response.message);
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("重新索引时出错");
            } finally {
                 isReindexing.value = false; // Stop loading
            }
        };

        // --- Public Status Toggle ---
        const togglePublicStatus = async (status: boolean) => {
            const baseId = route.params.base_id as string;
            const action = status ? '公开' : '取消公开';
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const endpoint = status 
                    ? `/v1/api/mark/knowledgebase/${baseId}/public` 
                    : `/v1/api/mark/knowledgebase/${baseId}/unpublic`;
                
                const response: any = await putRequest(baseURL + endpoint, {});
                
                if (response.code === 200) {
                    ElMessage.success(`知识库已${action}`);
                } else {
                    ElMessage.error(`${action}知识库失败: ${response.message}`);
                    settings.value.is_public = !status; // Revert switch on failure
                }
            } catch (error) {
                console.error(error);
                ElMessage.error(`操作知识库${action}状态时出错`);
                settings.value.is_public = !status; // Revert switch on error
            }
        };

        onMounted(() => {
            fetchFiles();
            get_kb_config();
            checkIsAdmin();
            // Set initial active menu based on route if needed (e.g., if linking directly to settings)
            // const currentPath = route.path;
            // if (currentPath.includes('/settings')) { // Adjust logic as needed
            //     toggleSwitch('2');
            // }
        });

        return {
            // State
            switchButton,
            activeMenu,
            searchText,
            files, // Original files list
            filteredFiles, // Computed property for display
            settings,
            isCollapse,
            isAdmin,
            isSavingSettings,
            isReindexing,

            // Methods
            toggleSwitch,
            addFile,
            saveSettings,
            get_kb_config,
            toggleCollapse,
            handleFileAction, // Use combined handler
            togglePublicStatus,

            // Rename Dialog
            renameDialogVisible,
            renameForm,
            renameFormRef,
            openRenameDialog,
            confirmRename,

            // Reindex Dialog
            reindexDialogVisible,
            reindexSplitterModel,
            reindexWindowSize,
            reindexStepSize,
            reindexChunkSize,
            reindexChunkOverlap,
            openReindexDialog,
            confirmReindex,

            // Icons (already registered in components)
            Search, Plus, MoreFilled, EditPen, Refresh, Delete, InfoFilled
        };
    }
});
</script>

<style scoped>
.page-container {
    display: flex;
    height: 100%;
    width: 100%;
    background: var(--bg-main);
    overflow: hidden;
}

/* --- Sidebar Styles --- */
.sidebar {
    background: var(--bg-sidebar);
    transition: width 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
    border-right: 1px solid var(--border-light);
    box-shadow: var(--shadow-sm);
}

.sidebar-header {
    padding: 18px 16px;
    height: 60px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border-bottom: 1px solid var(--border-light);
    overflow: hidden;
}

.sidebar-header.collapsed {
    padding: 18px 0;
    justify-content: center;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 600;
    white-space: nowrap;
}

.logo .el-icon {
    font-size: 22px;
    color: var(--primary-500);
}

.logo-text {
    opacity: 1;
    transition: opacity 0.3s ease;
}

.sidebar-header.collapsed .logo-text {
    opacity: 0;
    display: none;
}

.sidebar-menu {
    flex-grow: 1;
    border: none;
    overflow-y: auto;
    overflow-x: hidden;
    margin-top: 10px;
    background: transparent !important;
}

.sidebar-menu::-webkit-scrollbar {
    display: none;
}

.sidebar-menu {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.menu-item {
    margin: 4px 10px;
    border-radius: var(--radius-md);
    height: 44px;
    line-height: 44px;
    padding-left: 18px !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
    transition: all 0.2s;
}

.menu-item .el-icon {
    margin-right: 12px;
    font-size: 18px;
    color: var(--text-tertiary);
}

.menu-item:not(.is-active):hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
}

.menu-item:not(.is-active):hover .el-icon {
    color: var(--text-primary);
}

.menu-item.is-active {
    background: var(--primary-600) !important;
    color: white !important;
    font-weight: 500;
}

.menu-item.is-active .el-icon {
    color: white;
}

.sidebar-footer {
    padding: 10px;
    border-top: 1px solid var(--border-light);
    display: flex;
    justify-content: center;
}

.collapse-btn {
    color: var(--text-secondary);
    width: 100%;
    border-radius: var(--radius-md);
}

.collapse-btn:hover {
    background-color: var(--bg-hover);
    color: var(--text-primary);
}

/* --- Main Content Styles --- */
.main-content {
    flex: 1;
    padding: 20px;
    height: 100%;
    overflow-y: auto;
    box-sizing: border-box;
    background: var(--bg-main);
}

.content-wrapper {
    height: 100%;
}

.content-card {
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    background: var(--bg-card);
    box-shadow: var(--shadow-sm);
    height: calc(100% - 40px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.el-card :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    padding: 16px 20px;
    font-weight: 600;
    color: var(--text-primary);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    width: 100%;
}

.header-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.search-input {
    width: 250px;
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

.el-button {
    border-radius: var(--radius-md);
}

.el-button--primary {
    background: var(--primary-600);
    border-color: var(--primary-600);
}

.el-button--primary:hover {
    background: var(--primary-700);
    border-color: var(--primary-700);
}

/* --- Document Table Styles --- */
.file-table {
    flex-grow: 1;
    background: transparent;
}

.file-table :deep(.el-table) {
    --el-table-border-color: var(--border-light);
    --el-table-header-background-color: var(--bg-elevated);
    --el-table-background-color: var(--bg-card);
    --el-table-row-hover-background-color: var(--bg-hover);
    --el-table-text-color: var(--text-primary);
    --el-table-header-text-color: var(--text-secondary);
    background: transparent;
}

.file-table :deep(.el-table__header th) {
    background-color: var(--bg-elevated);
    color: var(--text-secondary);
    font-weight: 600;
    border-bottom: 1px solid var(--border-light);
}

.file-table :deep(.el-table__row) {
    background-color: var(--bg-card);
    transition: background-color 0.2s ease;
}

.file-table :deep(.el-table__row:hover) {
    background-color: var(--bg-hover);
}

.file-table :deep(.el-table__empty-block) {
    background-color: var(--bg-card);
    color: var(--text-tertiary);
}

.file-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.file-icon {
    color: var(--primary-500);
    font-size: 16px;
}

.file-name {
    color: var(--text-primary);
    cursor: default;
}

.el-tag--small {
    padding: 0 8px;
    line-height: 20px;
    height: 22px;
    border-radius: var(--radius-sm);
}

.action-more-btn {
    padding: 5px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
}

.action-more-btn:hover {
    background-color: var(--bg-hover);
    color: var(--primary-600);
}

.el-dropdown-menu__item.delete-item {
    color: var(--danger-500);
}

.el-dropdown-menu__item.delete-item:hover {
    background-color: var(--danger-100);
    color: var(--danger-600);
}

/* --- Settings View Styles --- */
.settings-card :deep(.el-card__body) {
    padding: 30px;
}

.settings-view .el-form {
    max-width: 700px;
    margin: 0 auto;
}

.settings-view .el-divider {
    margin: 30px 0;
    border-color: var(--border-light);
}

.settings-view .el-divider__text {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    background: var(--bg-card);
}

.settings-view .el-form-item {
    margin-bottom: 24px;
}

.settings-view .el-form-item__label {
    color: var(--text-secondary);
    font-weight: 500;
}

.settings-view .el-radio-group {
    margin-right: 10px;
}

.settings-view .el-radio {
    color: var(--text-primary);
}

.settings-view .el-radio__inner {
    background-color: var(--bg-main);
    border-color: var(--border-medium);
}

.settings-view .el-radio__inner:hover {
    border-color: var(--primary-500);
}

.settings-view .el-radio.is-checked .el-radio__inner {
    background-color: var(--primary-600);
    border-color: var(--primary-600);
}

.settings-view .el-radio.is-checked .el-radio__label {
    color: var(--primary-600);
}

.settings-view .el-switch {
    --el-switch-on-color: var(--primary-600);
    --el-switch-off-color: var(--border-medium);
}

.settings-view .el-input__wrapper {
    background: var(--bg-main);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
}

.settings-view .el-input__wrapper:hover {
    border-color: var(--primary-400);
}

.settings-view .el-input__wrapper.is-focus {
    border-color: var(--primary-600);
    box-shadow: 0 0 0 3px var(--primary-100);
}

.info-icon {
    margin-left: 8px;
    color: var(--text-tertiary);
    cursor: help;
    transition: color 0.2s;
}

.info-icon:hover {
    color: var(--primary-500);
}

.setting-desc {
    margin-left: 10px;
    color: var(--text-tertiary);
    font-size: 12px;
    line-height: 1.5;
    display: inline-block;
    vertical-align: middle;
    margin-right: 5px;
}

/* --- Dialog Styles --- */
.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding-top: 10px;
}

.el-dialog {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-xl);
}

.el-dialog :deep(.el-dialog__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    color: var(--text-primary);
    padding: 20px;
}

.el-dialog :deep(.el-dialog__title) {
    color: var(--text-primary);
    font-weight: 600;
}

.el-dialog :deep(.el-dialog__body) {
    color: var(--text-primary);
    padding: 20px;
}

.el-dialog :deep(.el-form-item__label) {
    color: var(--text-secondary);
    font-weight: 500;
}

.el-dialog :deep(.el-input__wrapper) {
    background: var(--bg-main);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
}

.el-dialog :deep(.el-radio__inner) {
    background-color: var(--bg-main);
    border-color: var(--border-medium);
}

.el-dialog :deep(.el-radio.is-checked .el-radio__inner) {
    background-color: var(--primary-600);
    border-color: var(--primary-600);
}

.el-dialog :deep(.el-radio.is-checked .el-radio__label) {
    color: var(--primary-600);
}

/* --- Dropdown Menu Styles --- */
.el-dropdown-menu {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
}

.el-dropdown-menu__item {
    color: var(--text-primary);
    background: transparent;
}

.el-dropdown-menu__item:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.el-dropdown-menu__item.divider {
    border-top: 1px solid var(--border-light);
    margin: 4px 0;
    padding: 0;
    height: 1px;
    background: transparent;
}

/* --- Responsive Design --- */
@media screen and (max-width: 1200px) {
    .sidebar {
        width: 64px !important;
    }

    .sidebar-header .logo-text {
        display: none;
    }

    .sidebar-header {
        justify-content: center;
        padding: 18px 0;
    }

    .menu-item .el-icon {
        margin-right: 0;
    }

    .menu-item .menu-text {
        display: none;
    }
}

@media screen and (max-width: 768px) {
    .page-container {
        flex-direction: column;
    }

    .sidebar {
        width: 100% !important;
        height: auto;
        flex-direction: row;
        border-right: none;
        border-bottom: 1px solid var(--border-light);
    }

    .sidebar-header {
        display: none;
    }

    .sidebar-menu {
        display: flex;
        overflow-x: auto;
        overflow-y: hidden;
        margin-top: 0;
        padding: 8px;
    }

    .menu-item {
        margin: 0 4px;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .sidebar-footer {
        display: none;
    }

    .main-content {
        padding: 12px;
    }

    .content-card {
        height: calc(100% - 24px);
    }

    .header-actions {
        flex-direction: column;
        align-items: stretch;
        gap: 8px;
    }

    .search-input {
        width: 100%;
    }

    .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }

    .settings-view .el-form {
        max-width: 100%;
    }
}

/* --- Dark Mode Adaptation --- */
[data-theme="dark"] .page-container {
    background: var(--bg-main);
}

[data-theme="dark"] .sidebar {
    background: var(--bg-sidebar);
    border-right-color: var(--border-light);
}

[data-theme="dark"] .sidebar-header {
    border-bottom-color: var(--border-light);
}

[data-theme="dark"] .logo {
    color: var(--text-primary);
}

[data-theme="dark"] .sidebar-footer {
    border-top-color: var(--border-light);
}

[data-theme="dark"] .content-card {
    background: var(--bg-card);
    border-color: var(--border-light);
}

[data-theme="dark"] .el-card :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom-color: var(--border-light);
}

[data-theme="dark"] .file-table :deep(.el-table__row) {
    background-color: var(--bg-card);
}

[data-theme="dark"] .file-table :deep(.el-table__row:hover) {
    background-color: var(--bg-hover);
}

[data-theme="dark"] .settings-view .el-divider__text {
    background: var(--bg-card);
}

[data-theme="dark"] .el-dropdown-menu {
    background: var(--bg-card);
    border-color: var(--border-light);
}

[data-theme="dark"] .el-dropdown-menu__item:hover {
    background: var(--bg-hover);
}

[data-theme="dark"] .search-input :deep(.el-input__wrapper) {
    background: var(--bg-elevated);
}

[data-theme="dark"] .settings-view .el-input__wrapper {
    background: var(--bg-elevated);
}

[data-theme="dark"] .settings-view .el-radio__inner {
    background-color: var(--bg-elevated);
    border-color: var(--border-medium);
}

[data-theme="dark"] .el-dialog {
    background: var(--bg-card);
}

[data-theme="dark"] .el-dialog :deep(.el-dialog__header) {
    background: var(--bg-elevated);
    border-bottom-color: var(--border-light);
}

[data-theme="dark"] .el-dialog :deep(.el-input__wrapper) {
    background: var(--bg-elevated);
}

[data-theme="dark"] .el-dialog :deep(.el-radio__inner) {
    background-color: var(--bg-elevated);
    border-color: var(--border-medium);
}
</style>