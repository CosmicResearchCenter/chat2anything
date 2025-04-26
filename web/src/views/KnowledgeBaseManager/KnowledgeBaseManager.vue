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
                    window_size: parseInt(reindexWindowSize.value, 10),
                    step_size: parseInt(reindexStepSize.value, 10)
                };
            } else {
                 if (!reindexChunkSize.value || !reindexChunkOverlap.value || isNaN(Number(reindexChunkSize.value)) || isNaN(Number(reindexChunkOverlap.value))) {
                    ElMessage.warning('TextSplitter 参数必须是有效的数字');
                    return;
                }
                splitter_args = {
                    chunk_size: parseInt(reindexChunkSize.value, 10),
                    chunk_overlap: parseInt(reindexChunkOverlap.value, 10)
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
    height: 100vh;
    background-color: #f7f8fa; /* Slightly lighter background */
}

/* --- Sidebar Styles --- */
.sidebar {
    background: #0d1a2e; /* Darker, solid background */
    transition: width 0.3s ease;
    display: flex;
    flex-direction: column;
    height: 100%;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
    padding: 18px 15px;
    height: 60px; /* Match nav height */
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    overflow: hidden; /* Prevent text overflow during collapse */
}

.sidebar-header.collapsed {
    padding: 18px 0;
    justify-content: center;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #e0e0e0;
    font-size: 18px;
    font-weight: 600;
    white-space: nowrap; /* Prevent text wrapping */
}

.logo .el-icon {
    font-size: 22px;
    color: #409eff; /* Use theme primary color for icon */
}

.logo-text {
    opacity: 1;
    transition: opacity 0.3s ease;
}

.sidebar-header.collapsed .logo-text {
    opacity: 0;
    display: none; /* Hide text when collapsed */
}

.sidebar-menu {
    flex-grow: 1;
    border: none;
    overflow-y: auto; /* Allow scrolling if menu items exceed height */
    overflow-x: hidden;
    margin-top: 10px;
}

/* Hide scrollbar */
.sidebar-menu::-webkit-scrollbar { display: none; }
.sidebar-menu { -ms-overflow-style: none; scrollbar-width: none; }

.menu-item {
    margin: 4px 10px;
    border-radius: 6px;
    height: 44px;
    line-height: 44px;
    padding-left: 18px !important; /* Adjust padding for icon */
}

.menu-item .el-icon {
    margin-right: 12px; /* Space between icon and text */
    font-size: 18px;
}

.menu-item:not(.is-active):hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #ffffff !important;
}

.menu-item.is-active {
    background-color: #409eff !important; /* Theme primary color */
    color: #ffffff !important;
    font-weight: 500;
}

.sidebar-footer {
    padding: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    justify-content: center;
}

.collapse-btn {
    color: #a6adb4;
    width: 100%;
}
.collapse-btn:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #ffffff;
}

/* --- Main Content Styles --- */
.main-content {
    padding: 20px;
    height: 100vh;
    overflow-y: auto;
    box-sizing: border-box;
}

.content-wrapper {
    height: 100%;
}

.content-card {
    border: none; /* Remove default border */
    border-radius: 8px;
    background-color: #ffffff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    height: calc(100vh - 40px); /* Adjust based on padding */
    display: flex;
    flex-direction: column;
}

.el-card :deep(.el-card__header) {
    background-color: #f9fafc;
    border-bottom: 1px solid #e9ecef;
    padding: 15px 20px;
    font-weight: 500;
    color: #343a40;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.search-input {
    width: 250px;
}

.search-input .el-input__wrapper {
    border-radius: 6px;
}

.el-button {
    border-radius: 6px;
}

/* --- Document Table Styles --- */
.file-table {
    flex-grow: 1; /* Allow table to fill remaining space */
}

.file-table :deep(.el-table__header th) {
    background-color: #f8f9fa;
    color: #6c757d;
    font-weight: 500;
}

.file-table :deep(.el-table__row) {
    transition: background-color 0.2s ease;
}

.file-table :deep(.el-table__row:hover) {
    background-color: #f1f3f5;
}

.file-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.file-icon {
    color: #409eff; /* Theme color */
    font-size: 16px;
}

.file-name {
    color: #343a40;
    cursor: default; /* Indicate text is not directly clickable */
}

.el-tag--small {
    padding: 0 8px;
    line-height: 20px;
    height: 22px;
}

.action-more-btn {
    padding: 5px;
    border: none;
    background: transparent;
}
.action-more-btn:hover {
    background-color: #e9ecef;
}

.el-dropdown-menu__item.delete-item {
    color: var(--el-color-danger);
}
.el-dropdown-menu__item.delete-item:hover {
    background-color: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
}

/* --- Settings View Styles --- */
.settings-card :deep(.el-card__body) {
    padding: 30px;
}

.settings-view .el-form {
    max-width: 700px; /* Limit form width for readability */
    margin: 0 auto;
}

.settings-view .el-divider {
    margin: 30px 0;
}
.settings-view .el-divider__text {
    font-size: 15px;
    font-weight: 500;
    color: #495057;
}

.settings-view .el-form-item {
    margin-bottom: 20px;
}

.settings-view .el-form-item__label {
    color: #495057;
}

.settings-view .el-radio-group {
    margin-right: 10px;
}

.info-icon {
    margin-left: 8px;
    color: #adb5bd;
    cursor: help;
}

.setting-desc {
    margin-left: 10px;
    color: #6c757d;
    font-size: 12px;
    line-height: 1.5;
    display: inline-block; /* Ensure it aligns well */
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

/* Responsive adjustments (optional, refine as needed) */
@media screen and (max-width: 768px) {
    .sidebar {
        /* Consider making sidebar overlay on small screens */
    }
    .main-content {
        padding: 15px;
    }
    .header-actions {
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
    }
    .search-input {
        width: 100%;
    }
    .settings-view .el-form {
        max-width: 100%;
    }
}
</style>