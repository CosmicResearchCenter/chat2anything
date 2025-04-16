<template>
    <el-card class="chatlog-title">
        {{ title }}
        <div class="dropdown-container">
            <el-dropdown trigger="click">
                <span class="el-dropdown-link" @click.stop>
                    <el-icon>
                        <More />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="renameConversation">重命名</el-dropdown-item>
                        <el-dropdown-item @click="deleteConversation">删除</el-dropdown-item>
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

export default defineComponent({
    name: 'MessageItem',
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
                });
                const baseURL = import.meta.env.VITE_APP_BASE_URL;
                const response: any = await deleteRequest(baseURL + `/v1/api/mark/chat/conversation/mark/${this.conversation_id.toString()}`);
                console.log(response.code);
                if (response.code === 200) {
                    ElMessage.success(response.message);
                    this.$emit('refreshList'); // 可以在父组件中监听此事件并刷新对话列表
                } else {
                    ElMessage.error('删除失败');
                }
            } catch (error) {
                // 判断是否是取消操作
                if (error !== 'cancel') {
                    ElMessage.error('删除失败');
                } else {
                    ElMessage.info('删除取消');
                }
            }
        },

        async renameConversation() {
            const newName = await ElMessageBox.prompt('输入新的对话名称', '重命名', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
            }).catch(() => null);
            console.log(newName);
            console.log(this.conversation_id);
            const baseURL = import.meta.env.VITE_APP_BASE_URL;
            if (newName && newName.value) {
                const response: any = await postRequest(baseURL+'/v1/api/mark/chat/conversation-rename/', {
                    conversation_id: this.conversation_id.toString(),
                    new_name: newName.value,
                    user_id: 'mark',
                });
                if (response.code === 200) {
                    ElMessage.success('重命名成功');
                    this.$emit('updateTitle', response.data.conversation_name);  // 可以在父组件中监听此事件更新标题
                } else {
                    ElMessage.error('重命名失败');
                }
            }
        },
    },
});
</script>

<style>
.chatlog-title {
    text-align: center;
    position: relative;
}

.dropdown-container {
    position: absolute;
    bottom: 10px;
    right: 10px;
}
</style>
