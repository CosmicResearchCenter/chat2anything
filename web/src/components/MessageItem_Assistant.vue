<template>
    <div class="msg-box">
        <div  class="avatar-box">
            <el-avatar class="avatar" shape="circle" size="100" fit="fit" :src="avatar_url" />
        </div>
        <v-md-preview  :text="message" class="msg"></v-md-preview > 
    </div>
    <!-- 显示召回文档的Box -->
    <div class="retriever-box">
        <el-collapse accordion>
            <el-collapse-item title="召回文档">
                <el-collapse accordion>
                    <el-collapse-item v-for="(doc, index) in retrievedDocs" :key="index" :title="(doc.knowledge_doc_name)">
                        <p>{{ doc.content }}</p>
                    </el-collapse-item>
                </el-collapse>
            </el-collapse-item> 
        </el-collapse>  
    </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
export default defineComponent({
    name: 'MessageItem_Assistant',
    props: {
        message: {
            type: String as PropType<string>,
            required: true,
        },
        avatar_url: {
            type: String as PropType<string>,
            required: false
        },
        retrievedDocs: {
            type: Array as PropType<Array<{ content: string, knowledge_doc_name: string }>>,
            required: true
        }
    },
});
</script>
<style>
.msg-box {
  display: flex;
  gap: 16px;
  margin: 24px 0;
  position: relative;
}

.avatar {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 2px solid #fff;
}

.msg {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 16px;
  padding: 16px 20px;
  border: 1px solid rgba(209, 213, 219, 0.3);
  box-shadow: 
    0 4px 24px -1px rgba(0, 0, 0, 0.1),
    0 2px 8px -1px rgba(0, 0, 0, 0.06);
  max-width: 80%;
  position: relative;
}

.msg::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 20px;
  width: 16px;
  height: 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  transform: rotate(45deg);
  border-left: 1px solid rgba(209, 213, 219, 0.3);
  border-bottom: 1px solid rgba(209, 213, 219, 0.3);
}

.retriever-box {
  margin: 16px 60px;
  padding: 15px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(209, 213, 219, 0.3);
  box-shadow: 
    0 4px 24px -1px rgba(0, 0, 0, 0.08),
    0 2px 8px -1px rgba(0, 0, 0, 0.04);
}

.retriever-box :deep(.el-collapse-item__header) {
  padding: 16px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  background: transparent;
  border-bottom: 1px solid rgba(209, 213, 219, 0.3);
  transition: all 0.3s ease;
}

.retriever-box :deep(.el-collapse-item__content) {
  padding: 20px;
  line-height: 1.6;
  color: #262626;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px) saturate(160%);
  -webkit-backdrop-filter: blur(10px) saturate(160%);
}
</style>