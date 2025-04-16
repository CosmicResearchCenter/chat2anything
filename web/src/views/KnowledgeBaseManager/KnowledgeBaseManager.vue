<template>
    <el-row class="page-content">
        <el-col :span="3" class="sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    <el-icon><Monitor /></el-icon>
                    <span>{{ settings.knowledgeBaseName }}</span>
                </div>
            </div>
            <el-menu :default-active="activeMenu" 
                     class="sidebar-menu" 
                     :collapse="isCollapse"
                     background-color="transparent"
                     text-color="#bdf1f6"
                     active-text-color="#ffffff">
                <el-menu-item index="1" @click="toggleSwitch('1')" class="menu-item">
                    <el-icon><Document /></el-icon>
                    <template #title>
                        <span class="menu-text">文档</span>
                    </template>
                </el-menu-item>

                <el-menu-item index="2" @click="toggleSwitch('2')" class="menu-item">
                    <el-icon><Setting /></el-icon>
                    <template #title>
                        <span class="menu-text">设置</span>
                    </template>
                </el-menu-item>
            </el-menu>
            
            <div class="sidebar-footer">
                <el-button class="collapse-btn" @click="toggleCollapse">
                    <el-icon><Fold v-if="!isCollapse"/><Expand v-else/></el-icon>
                </el-button>
            </div>
        </el-col>

        <!-- Main content -->
        <el-col :span="20" class="main-content">
            <div class="documentBox content-card" v-if="switchButton === '1'">
                <!-- Header -->
                <div class="header">
                    <el-input v-model="searchText" placeholder="搜索文档..." class="search-input" clearable>
                        <template #prefix>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                    <el-button type="primary" class="add-button" @click="addFile">
                        <el-icon><Plus /></el-icon>
                        添加文件
                    </el-button>
                </div>

                <!-- Table -->
                <el-table :data="files" style="width: 100%" class="file-table">
                    <el-table-column prop="index" label="#" width="50"></el-table-column>
                    <el-table-column prop="name" label="文件名" width="300" v-slot="scope">
                        <el-icon>
                            <Document />
                        </el-icon>
                        <span class="file-name">{{ scope.row.name }}</span>
                    </el-table-column>
                    <el-table-column prop="size" label="大小"></el-table-column>
                    <el-table-column prop="uploadDate" label="上传时间"></el-table-column>
                    <el-table-column prop="status" label="状态" width="100">
                        <template v-slot="scope">
                            <el-tag :type="scope.row.status === '可用' ? 'success' : 'warning'">
                                {{ scope.row.status }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="100">
                        <template v-slot="scope">
                            <el-dropdown trigger="click">
                                <span class="el-dropdown-link">
                                    <el-icon>
                                        <More />
                                    </el-icon>
                                </span>
                                <template #dropdown>
                                    <el-dropdown-menu>
                                        <el-dropdown-item @click="openRenameDialog(scope.row.docId)">重命名</el-dropdown-item>
                                        <!-- <el-dropdown-item>分段设置</el-dropdown-item> -->
                                        <!-- <el-dropdown-item>归档</el-dropdown-item> -->
                                        <el-dropdown-item @click="deleteFile">删除</el-dropdown-item>
                                    </el-dropdown-menu>
                                </template>
                            </el-dropdown>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <div class="settingBox content-card" v-else>
                <el-form :model="settings" label-width="120px">
                    <el-form-item label="知识库名字">
                        <el-input v-model="settings.knowledgeBaseName" placeholder="请输入知识库名字" />
                    </el-form-item>
                    <el-form-item label="RAG模式">
                        <el-radio-group v-model="settings.rag_model">
                            <el-radio label="0">混合检索（向量+模糊查询）</el-radio>
                            <el-radio label="1">向量检索</el-radio>
                            <el-radio label="2">模糊检索</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="启用二阶段重排">
                        <el-switch v-model="settings.is_rerank" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="saveSettings">保存设置</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </el-col>
    </el-row>
    <el-dialog
        v-model="renameDialogVisible"
        title="重命名文档"
        width="30%"
        :close-on-click-modal="false"
    >
        <el-form>
            <el-form-item label="新文件名">
                <el-input v-model="newDocName" placeholder="请输入新的文档名"></el-input>
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="renameDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmRename">确定</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { getRequest, postRequest,deleteRequest, putRequest } from '@/utils/http';

interface File {
    index: number;
    name: string;
    size: string;
    uploadDate: string;
    status: string;
    docId: string;
}

export default defineComponent({
    setup() {
        const router = useRouter();
        const route = useRoute();
        const switchButton = ref('1');
        const activeMenu = ref('1');
        const searchText = ref('');
        const files = ref<File[]>([]);

        const settings = ref({
            knowledgeBaseId:"",
            knowledgeBaseName: '',
            rag_model: 0,
            is_rerank: false
        });

        // 获取文档列表并获取每个文档的索引状态
        const fetchFiles = async () => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}`);
                if (response.code === 200) {
                    files.value = await Promise.all(response.data.map(async (doc: any, index: number) => {
                        // 获取索引状态
                        const baseURL = import.meta.env.VITE_APP_BASE_URL;
                        const statusResponse: any = await getRequest(
                           baseURL+ `/v1/api/mark/knowledgebase/${baseId}/doc/${doc.doc_id}/index_status`
                        );
                        const status = statusResponse.code === 200 && statusResponse.data[0].index_status === 1 ? '可用' : '未索引';
                        return {
                            index: index + 1,
                            name: doc.doc_name,
                            size: (doc.doc_size / 1024).toFixed(1) + 'k',
                            recalls: 0,
                            uploadDate: new Date(doc.create_time).toLocaleString(),
                            status,
                            docId: doc.doc_id
                        };
                    }));
                    ElMessage.success(response.message);
                } else {
                    ElMessage.error("Failed to retrieve files.");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("Error fetching documents.");
            }
        };

        const get_kb_config = async () => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await getRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}/config`);
                if (response.code === 200) {
                    settings.value = response.data[0];
                } else {
                    ElMessage.error("Failed to retrieve settings.");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("Error fetching settings.");
            }
        };

        const toggleSwitch = (menuIndex: string) => {
            if (switchButton.value !== menuIndex) {
                switchButton.value = menuIndex;
                activeMenu.value = menuIndex;
                ElMessage.info(`切换到${menuIndex === '1' ? '文档' : '设置'}`);
            }
        };

        const addFile = () => {
            const baseId = route.params.base_id as string;
            router.push(`/manager/${baseId}/create`);
        };

        const saveSettings = async () => {
            const baseId = route.params.base_id as string;
            settings.value.knowledgeBaseId = baseId;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await putRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}/config`, settings.value);
                if (response.code === 200) {
                    ElMessage.success("设置已保存");
                } else {
                    ElMessage.error("保存设置失败");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("保存设置时出错");
            }
        };
        const deleteFile = async () => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await deleteRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}/doc/${files.value[0].docId}`);
                if (response.code === 200) {
                    ElMessage.success("文件已删除");
                } else {
                    ElMessage.error("删除文件失败");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("删除文件时出错");
            }
        };
        const renameDoc = async () => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await postRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}/doc/${files.value[0].docId}/rename`, {
                    new_name: "new name"
                });
                if (response.code === 200) {
                    ElMessage.success("文件已重命名");
                } else {
                    ElMessage.error("重命名文件失败");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("重命名文件时出错");
            }
        };
        const isCollapse = ref(false);
        
        const toggleCollapse = () => {
            isCollapse.value = !isCollapse.value;
        };

        const renameDialogVisible = ref(false);
        const newDocName = ref('');
        const currentDocId = ref('');

        const openRenameDialog = (docId: string) => {
            currentDocId.value = docId;
            // 获取当前文档的名称作为默认值
            const currentDoc = files.value.find(file => file.docId === docId);
            newDocName.value = currentDoc ? currentDoc.name : '';
            renameDialogVisible.value = true;
        };

        const confirmRename = async () => {
            const baseId = route.params.base_id as string;
            try {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await putRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId}/doc/${currentDocId.value}/rename?new_name=${newDocName.value}`,{});
                if (response.code === 200) {
                    ElMessage.success("文件已重命名");
                    renameDialogVisible.value = false;
                    fetchFiles();
                } else {
                    ElMessage.error("重命名文件失败");
                }
            } catch (error) {
                console.error(error);
                ElMessage.error("重命名文件时出错");
            }
        };

        onMounted(() => {
            fetchFiles();
            get_kb_config();
        });

        return {
            switchButton,
            activeMenu,
            searchText,
            files,
            toggleSwitch,
            addFile,
            settings,
            saveSettings,
            get_kb_config,
            isCollapse,
            toggleCollapse,
            deleteFile,
            renameDoc,
            renameDialogVisible,
            newDocName,
            openRenameDialog,
            confirmRename
        };
    }
});
</script>


<style scoped>
.page-content {
    display: flex;
    min-height: 100vh;
    background-color: #f5f7fa;
}

.sidebar {
    background: linear-gradient(135deg, #0245a3 0%, #0a4fab 100%);
    backdrop-filter: blur(10px);
    min-height: 100vh;
    position: relative;
    transition: all 0.3s ease;
    box-shadow: 0 0 20px rgba(2, 69, 163, 0.1);
}

.sidebar-header {
    padding: 24px 16px;
    border-bottom: 1px solid rgba(189, 241, 246, 0.1);
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
    font-size: 20px;
    font-weight: 600;
}

.logo .el-icon {
    font-size: 24px;
}

.sidebar-menu {
    border: none;
    margin-top: 16px;
}

.menu-item {
    margin: 8px 12px;
    border-radius: 8px;
    height: 48px !important;
    line-height: 48px;
}

.menu-item:hover {
    background: rgba(143, 186, 243, 0.15) !important;
    backdrop-filter: blur(5px);
}

.menu-item.is-active {
    background: rgba(143, 186, 243, 0.25) !important;
}

.menu-text {
    font-size: 15px;
    margin-left: 8px;
}

.el-menu-item .el-icon {
    font-size: 18px;
}

.sidebar-footer {
    position: absolute;
    bottom: 20px;
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 0 16px;
}

.collapse-btn {
    background: transparent;
    border: none;
    color: #bdf1f6;
    cursor: pointer;
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.collapse-btn:hover {
    background: rgba(143, 186, 243, 0.15);
    color: #ffffff;
}

/* 在小屏幕下调整布局 */
@media screen and (max-width: 768px) {
    .sidebar {
        position: fixed;
        z-index: 1000;
        width: 60px;
    }
    
    .logo span,
    .menu-text {
        display: none;
    }
}

.main-content {
    padding: 24px;
    background-color: #f5f7fa;
}

.content-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.search-input {
    width: 300px;
    .el-input__inner {
        border-radius: 8px;
        border: 1px solid #e4e7ed;
    }
}

.add-button {
    background-color: #0245a3;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    transition: all 0.3s ease;
    
    &:hover {
        background-color: #8fbaf3;
        transform: translateY(-2px);
    }
}

.file-table {
    border-radius: 8px;
    overflow: hidden;
    
    .el-table__header th {
        background-color: #f8f9fa;
    }
    
    .el-table__row {
        transition: all 0.3s ease;
        
        &:hover {
            background-color: #f0f9ff;
        }
    }
}

.file-name {
    margin-left: 10px;
    color: #0245a3;
    font-weight: 500;
}

.el-tag {
    border-radius: 6px;
    padding: 4px 12px;
}

.settingBox {
    .el-form-item {
        margin-bottom: 24px;
    }
    
    .el-switch {
        margin-left: 8px;
    }
    
    .el-button {
        padding: 12px 24px;
    }
}

@media screen and (max-width: 768px) {
    .page-content {
        flex-direction: column;
    }

    .sidebar, .main-content {
        width: 100%;
    }
    
    .content-card {
        margin: 12px;
        padding: 16px;
    }
    
    .search-input {
        width: 200px;
    }
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}
</style>