<template>
    <div class="msg-box">
        <div class="avatar-box">
            <el-avatar class="avatar" shape="circle" size="100" fit="fit" :src="avatar_url" />
        </div>
        <div class="message-content">
            <!-- 思考内容部分 -->
            <div v-if="hasThinkContent" class="think-box">
                <div class="think-header" @click="toggleThinkContent">
                    <el-icon><Cpu /></el-icon>
                    <span>思考过程</span>
                    <el-icon class="toggle-icon" :class="{'is-active': showThinkContent}">
                        <ArrowDown />
                    </el-icon>
                </div>
                <v-md-preview v-show="showThinkContent" :text="thinkContent" class="think-content"></v-md-preview>
            </div>
            <!-- 回答内容部分 -->
            <v-md-preview :text="answerContent" class="msg"></v-md-preview>
        </div>
    </div>
    <!-- 显示召回文档的Box -->
    <div v-if="hasRetrievedDocs" class="retriever-box">
        <div class="retriever-header" @click="toggleDocsContent">
            <el-icon><Document /></el-icon>
            <span>信息来源 ({{ retrievedDocs.length }})</span>
            <el-icon class="toggle-icon" :class="{'is-active': showDocsContent}">
                <ArrowDown />
            </el-icon>
        </div>
        <div v-show="showDocsContent" class="retriever-content">
            <el-collapse accordion>
                <el-collapse-item v-for="(doc, index) in retrievedDocs" 
                                 :key="index" 
                                 :title="doc.knowledge_doc_name"
                                 :name="index">
                    <div class="doc-content">
                        <v-md-preview :text="doc.content"></v-md-preview>
                    </div>
                </el-collapse-item>
            </el-collapse>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue';
import type { PropType } from 'vue';
import { Cpu, ArrowDown, Document } from '@element-plus/icons-vue';

export default defineComponent({
    name: 'MessageItem_Assistant',
    components: {
        Cpu,
        ArrowDown,
        Document
    },
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
    setup(props) {
        const showThinkContent = ref(false);
        const showDocsContent = ref(false);
        
        // 解析消息内容，分离思考和回答部分
        const hasThinkContent = computed(() => {
            return props.message.includes('THINKING:') || 
                   props.message.includes('<think>');
        });

        const hasRetrievedDocs = computed(() => {
            return props.retrievedDocs && props.retrievedDocs.length > 0;
        });

        const thinkContent = computed(() => {
            if (!hasThinkContent.value) return '';
            
            // 检查是否有 THINKING: 格式
            const thinkingMatch = props.message.match(/THINKING:([\s\S]*?)(?=ANSWER:|$)/);
            if (thinkingMatch) return thinkingMatch[1].trim();
            
            // 检查是否有 <think></think> 格式
            const thinkTagMatch = props.message.match(/<think>([\s\S]*?)<\/think>/);
            return thinkTagMatch ? thinkTagMatch[1].trim() : '';
        });

        const answerContent = computed(() => {
            if (!hasThinkContent.value) return props.message;
            
            let processedMessage = props.message;
            
            // 处理 THINKING: 和 ANSWER: 格式
            if (processedMessage.includes('THINKING:')) {
                const answerMatch = processedMessage.match(/ANSWER:([\s\S]*)/);
                return answerMatch ? answerMatch[1].trim() : '';
            }
            
            // 处理 <think></think> 格式，移除标签及其内容
            // 使用更精确的正则表达式，确保完全移除think标签及其内容
            processedMessage = processedMessage.replace(/<think>[\s\S]*?<\/think>/g, '');
            
            // 去除可能的前后空白
            return processedMessage.trim();
        });

        const toggleThinkContent = () => {
            showThinkContent.value = !showThinkContent.value;
        };

        const toggleDocsContent = () => {
            showDocsContent.value = !showDocsContent.value;
        };

        return {
            hasThinkContent,
            thinkContent,
            answerContent,
            showThinkContent,
            toggleThinkContent,
            hasRetrievedDocs,
            showDocsContent,
            toggleDocsContent
        };
    }
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
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 2px solid #fff;
  transition: all 0.3s ease;
}

.avatar-box:hover .avatar {
  transform: scale(1.05);
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 90%;
}

.msg {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 4px 18px 18px 18px;
  padding: 16px 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 
    0 4px 24px -1px rgba(0, 0, 0, 0.08),
    0 2px 8px -1px rgba(0, 0, 0, 0.03);
  position: relative;
  transition: all 0.3s ease;
}

.msg:hover {
  box-shadow: 
    0 6px 30px -1px rgba(0, 0, 0, 0.12),
    0 3px 10px -1px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.msg::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 20px;
  width: 16px;
  height: 16px;
  background: #ffffff;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  transform: rotate(45deg);
  border-left: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.think-box {
  background: rgba(228, 237, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 16px;
  padding: 16px 20px;
  border: 1px solid rgba(57, 108, 240, 0.15);
  box-shadow: 
    0 4px 24px -1px rgba(57, 108, 240, 0.1),
    0 2px 8px -1px rgba(57, 108, 240, 0.06);
  position: relative;
  transition: all 0.3s ease;
}

.think-box:hover {
  box-shadow: 
    0 6px 30px -1px rgba(57, 108, 240, 0.15),
    0 3px 10px -1px rgba(57, 108, 240, 0.1);
}

.think-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  margin-bottom: 10px;
  border-bottom: 1px dashed rgba(57, 108, 240, 0.3);
  color: #3f51b5;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.think-header:hover {
  color: #0369e1;
}

.toggle-icon {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.toggle-icon.is-active {
  transform: rotate(180deg);
}

.think-content {
  color: #263238;
  font-size: 0.95em;
  font-family: 'Courier New', monospace;
  padding: 10px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}

/* 召回文档区域的样式优化 */
.retriever-box {
  margin: 16px 60px;
  padding: 15px;
  border-radius: 16px;
  background: rgba(245, 247, 250, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 
    0 4px 20px -1px rgba(0, 0, 0, 0.08),
    0 2px 8px -1px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease-in-out;
}

.retriever-box:hover {
  box-shadow: 
    0 6px 26px -1px rgba(0, 0, 0, 0.12),
    0 3px 10px -1px rgba(0, 0, 0, 0.06);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.retriever-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 5px;
  color: #444;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retriever-header:hover {
  color: #0369e1;
}

.retriever-header .el-icon {
  font-size: 18px;
  color: #1a73e8;
}

.retriever-content {
  margin-top: 10px;
  animation: fadeIn 0.3s ease-in-out;
}

.retriever-content :deep(.el-collapse) {
  border: none;
}

.retriever-content :deep(.el-collapse-item__header) {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.retriever-content :deep(.el-collapse-item__header:hover) {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.retriever-content :deep(.el-collapse-item__content) {
  padding: 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.doc-content {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 10px;
  font-size: 14px;
  line-height: 1.6;
}

/* 美化滚动条 */
.doc-content::-webkit-scrollbar {
  width: 6px;
}

.doc-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.doc-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.doc-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 代码块样式美化 */
.msg :deep(code) {
  background-color: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.msg :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 10px 0;
  overflow-x: auto;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.msg :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

/* 表格美化 */
.msg :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 15px 0;
}

.msg :deep(th),
.msg :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.msg :deep(th) {
  background-color: #f2f2f2;
  font-weight: 600;
}

.msg :deep(tr:nth-child(even)) {
  background-color: #f9f9f9;
}
</style>