<template>
    <el-card shadow="hover" :class="cardClass">
        <div class="kb-content">
            <el-icon class="kb-icon"><Collection /></el-icon>
            <span class="kb-name">{{ knowledgeBaseName }}</span>
            <el-icon v-if="checked" class="kb-check-icon"><Check /></el-icon>
        </div>
    </el-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
import { Collection, Check } from '@element-plus/icons-vue';

export default defineComponent({
    name: 'KnowledgeBaseItem',
    components: {
        Collection,
        Check
    },
    props: {
        knowledgeBaseName: {
            type: String as PropType<string>,
            required: true,
        },
        knowledgeBaseId: {
            type: String as PropType<string>,
            required: true,
        },
        checked: {
            type: Boolean as PropType<boolean>,
            default: false,
        },
    },
    computed: {
        cardClass() {
            return this.checked ? 'kb-box-checked' : 'kb-box';
        },
    },
});
</script>

<style scoped>
.kb-box, .kb-box-checked {
    transition: all 0.3s ease;
    cursor: pointer;
    margin-bottom: 10px;
}

.kb-box {
    background-color: var(--bg-card);
    border: 1px solid var(--border-light);
}

.kb-box:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    background-color: var(--bg-hover);
    border-color: var(--primary-300);
}

.kb-box-checked {
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-500) 100%);
    box-shadow: 0 8px 16px rgba(3, 105, 225, 0.25);
    border: 1px solid var(--primary-400);
}

.kb-box-checked:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(3, 105, 225, 0.35);
}

.kb-content {
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    padding: 5px 0;
}

.kb-icon {
    color: var(--primary-600);
    font-size: 16px;
}

.kb-box-checked .kb-icon {
    color: #ffffff;
}

.kb-name {
    flex: 1;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text-primary);
}

.kb-box-checked .kb-name {
    color: #ffffff;
    font-weight: 500;
}

.kb-check-icon {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    padding: 3px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 暗色模式适配 */
[data-theme="dark"] .kb-box {
    background-color: var(--bg-card);
    border-color: var(--border-light);
}

[data-theme="dark"] .kb-box:hover {
    background-color: var(--bg-hover);
    border-color: var(--primary-400);
}

[data-theme="dark"] .kb-name {
    color: var(--text-primary);
}

/* Element Plus Card 组件样式覆盖 */
.el-card {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-light) !important;
    background: var(--bg-card) !important;
}

.el-card:hover {
    border-color: var(--primary-300) !important;
}

.kb-box-checked + .el-card {
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-500) 100%) !important;
    border: none !important;
}

.el-card :deep(.el-card__body) {
    padding: 12px 16px !important;
}
</style>