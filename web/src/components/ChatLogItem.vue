<template>
    <el-card class="chatlog-title" shadow="hover">
        <div class="chatlog-content">
            <el-icon class="chatlog-icon"><ChatDotRound /></el-icon>
            <span class="chatlog-text">{{ title }}</span>
        </div>
        <div class="dropdown-container">
            <el-dropdown trigger="click">
                <span class="el-dropdown-link" @click.stop>
                    <el-icon>
                        <More />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="renameConversation">
                            <el-icon><Edit /></el-icon>重命名
                        </el-dropdown-item>
                        <el-dropdown-item @click="deleteConversation" class="delete-item">
                            <el-icon><Delete /></el-icon>删除
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </el-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
import { getRequest, postRequest, deleteRequest } from '@/utils/http';
import { ElMessageBox, ElMessage } from 'element-plus';
import { ChatDotRound, Edit, Delete, More } from '@element-plus/icons-vue';

export default defineComponent({
    name: 'MessageItem',
    components: {
        ChatDotRound,
        Edit,
        Delete,
        More
    },
    props: {
        title: {
            type: String as PropType<string>,
            required: true,
        },
        conversation_id: {
            type: String as PropType<string>,
            required: true,
        },
    },
    methods: {
        async deleteConversation() {
            try {
                await ElMessageBox.confirm('确定要删除这个对话吗?', '提示', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    confirmButtonClass: 'el-button--danger'
                });
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await deleteRequest(baseURL + `/v1/api/mark/chat/conversation/mark/${this.conversation_id.toString()}`);
                console.log(response.code);
                if (response.code === 200) {
                    ElMessage.success({
                        message: response.message,
                        duration: 2000,
                        showClose: true
                    });
                    this.$emit('refreshList'); 
                } else {
                    ElMessage.error('删除失败');
                }
            } catch (error) {
                // 判断是否是取消操作
                if (error !== 'cancel') {
                    ElMessage.error('删除失败');
                }
            }
        },

        async renameConversation() {
            const newName = await ElMessageBox.prompt('输入新的对话名称', '重命名', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                inputValidator: (value) => {
                    return value.trim() !== '' ? true : '对话名称不能为空'
                }
            }).catch(() => null);
            
            if (newName && newName.value) {
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await postRequest(baseURL+'/v1/api/mark/chat/conversation-rename/', {
                    conversation_id: this.conversation_id.toString(),
                    new_name: newName.value.trim(),
                    user_id: 'mark',
                });
                if (response.code === 200) {
                    ElMessage.success({
                        message: '重命名成功',
                        duration: 2000,
                        showClose: true
                    });
                    this.$emit('updateTitle', response.data.conversation_name);
                } else {
                    ElMessage.error('重命名失败');
                }
            }
        },
    },
});
</script>

<style scoped>
.chatlog-title {
    position: relative;
    transition: all 0.3s ease;
    cursor: pointer;
    overflow: hidden;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    margin-bottom: 8px;
}

.chatlog-title:hover {
    background: var(--bg-hover);
    border-color: var(--primary-300);
    transform: translateX(2px);
}

.chatlog-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.chatlog-icon {
    color: var(--primary-600);
    font-size: 16px;
}

.chatlog-text {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 14px;
    color: var(--text-primary);
}

.dropdown-container {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    transition: all 0.3s ease;
}

.chatlog-title:hover .dropdown-container {
    opacity: 1;
}

.el-dropdown-link {
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 6px;
    border-radius: 50%;
    transition: all 0.3s ease;
    color: var(--text-secondary);
}

.el-dropdown-link:hover {
    background-color: var(--bg-main);
    color: var(--text-primary);
}

.el-dropdown-menu :deep(.el-dropdown-item) {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 10px 15px;
    color: var(--text-primary);
}

.delete-item {
    color: var(--danger-500);
}

.el-dropdown-menu :deep(.el-dropdown-item:hover) {
    background-color: var(--bg-hover);
    color: var(--danger-600);
}

.el-dropdown-menu :deep(.el-dropdown-menu__item i) {
    margin-right: 5px;
}

/* 暗色模式适配 */
[data-theme="dark"] .chatlog-title {
    background: var(--bg-card);
    border-color: var(--border-light);
}

[data-theme="dark"] .chatlog-title:hover {
    background: var(--bg-hover);
    border-color: var(--primary-500);
}

[data-theme="dark"] .el-dropdown-link {
    color: var(--text-secondary);
}

[data-theme="dark"] .el-dropdown-link:hover {
    background-color: var(--bg-elevated);
    color: var(--text-primary);
}

[data-theme="dark"] .el-dropdown-menu :deep(.el-dropdown-item) {
    color: var(--text-primary);
}

[data-theme="dark"] .delete-item {
    color: var(--danger-400);
}

[data-theme="dark"] .el-dropdown-menu :deep(.el-dropdown-item:hover) {
    background-color: var(--bg-hover);
    color: var(--danger-500);
}
</style>
