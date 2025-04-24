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

<style>
.kb-box, .kb-box-checked {
    transition: all 0.3s ease;
    cursor: pointer;
    margin-bottom: 10px;
}

.kb-box {
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.kb-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    border-color: rgba(0, 0, 0, 0.08);
}

.kb-box-checked {
    background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
    box-shadow: 0 8px 16px rgba(3, 105, 225, 0.2);
    border: none;
}

.kb-box-checked:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(3, 105, 225, 0.25);
}

.kb-content {
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    padding: 5px 0;
}

.kb-icon {
    color: #0245a3;
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
}

.kb-box-checked .kb-name {
    color: #ffffff;
}

.kb-check-icon {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    padding: 3px;
    font-size: 12px;
}
</style>