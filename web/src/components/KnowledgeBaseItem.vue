<template>
    <el-card shadow="hover" :class="cardClass">
        {{ knowledgeBaseName }}
    </el-card>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
export default defineComponent({
    name: 'KnowledgeBaseItem',
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
            console.log('Checked:', this.checked);  // 用于调试
            return this.checked ? 'kb-box-checked' : 'kb-box';
        },
    },
});
</script>
<style>
.kb-box {
    background-color: #ffffff;
}

.kb-box-checked {
    background-color: #337ce8;
}
</style>