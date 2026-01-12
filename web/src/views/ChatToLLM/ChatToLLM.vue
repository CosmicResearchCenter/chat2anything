<template>
  <div class="chat-layout">
    <!-- Left Sidebar Component -->
    <ChatList 
      :is-collapsed="isSidebarCollapsed"
      :loading="loadingList"
      :list="conversionsList"
      :current-id="currentConversationId"
      @create="createConversation"
      @select="handleItemClick"
      @delete="deleteConversation"
      @toggle="toggleSidebar"
    />

    <!-- Main Chat Area -->
    <main class="main-area">
      <!-- Top Navigation Bar -->
      <header class="chat-navbar glass-effect">
         <div class="nav-left">
           <div class="mobile-menu-btn" @click="toggleSidebar">
              <el-icon><Fold /></el-icon>
           </div>
           <h2 class="current-title">{{ getCurrentConversationTitle() }}</h2>
         </div>
         
         <div class="nav-right">
            <!-- Knowledge Base Selector -->
            <el-popover
              placement="bottom-end"
              title="切换知识库"
              :width="300"
              trigger="click"
            >
              <template #reference>
                <el-button class="kb-select-btn" :class="{ 'active': choosedKnowledgeBaseId }">
                  <el-icon><Collection /></el-icon>
                  <span class="kb-name">{{ getSelectedKnowledgeBaseName() || '选择知识库' }}</span>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
              </template>
              
              <div class="kb-list custom-scrollbar">
                 <div 
                    v-for="kb in knowledgebaseList" 
                    :key="kb.id" 
                    class="kb-option"
                    :class="{ 'selected': choosedKnowledgeBaseId === kb.id }"
                    @click="switchKnowledgeBase(kb.id)"
                 >
                    <el-icon><Monitor /></el-icon>
                    <span>{{ kb.knowledgeBaseName }}</span>
                 </div>
              </div>
            </el-popover>
         </div>
      </header>

      <!-- Chat Stream -->
      <div class="messages-wrapper custom-scrollbar" ref="chatContent">
        <!-- Empty State -->
        <div v-if="!conversionMessage.length" class="empty-state">
           <div class="brand-logo">
             <div class="logo-circle">
                <span class="logo-emoji">🤖</span>
             </div>
           </div>
           <h3>我可以为您做些什么？</h3>
           <div class="suggestion-grid">
              <div class="suggestion-card" @click="fillInput('帮我制定一个Python学习计划')">
                 <div class="card-icon">📚</div>
                 <div class="card-text">制定 Python 学习计划</div>
              </div>
              <div class="suggestion-card" @click="fillInput('解释一下什么是 RAG 技术')">
                 <div class="card-icon">🧠</div>
                 <div class="card-text">解释 RAG 技术原理</div>
              </div>
              <div class="suggestion-card" @click="fillInput('写一个 Vue3 的计数器组件')">
                 <div class="card-icon">💻</div>
                 <div class="card-text">生成 Vue3 代码示例</div>
              </div>
           </div>
        </div>

        <!-- Message List -->
        <div v-else class="message-list">
           <div v-for="(item, index) in conversionMessage" :key="index" class="message-row">
              <!-- User Message -->
              <div class="message-group user">
                 <div class="message-bubble user-bubble">
                    <v-md-preview :text="String(item.query)" />
                 </div>
              </div>

              <!-- Assistant Message -->
              <div class="message-group assistant">
                 <div class="avatar-container">
                    <div class="ai-avatar">AI</div>
                 </div>
                 <div class="assistant-content">
                    <div class="message-bubble assistant-bubble">
                        <!-- Thinking Process -->
                        <div v-if="parseMessageContent(String(item.answer)).hasThink" class="think-section">
                           <div class="think-header" @click="toggleThink(item)">
                              <el-icon><Cpu /></el-icon>
                              <span>思考过程</span>
                              <el-icon class="toggle-icon" :class="{ 'is-active': item.showThink }"><ArrowDown /></el-icon>
                           </div>
                           <v-md-preview 
                              v-show="item.showThink" 
                              :text="parseMessageContent(String(item.answer)).think" 
                              class="think-content" 
                           />
                        </div>

                        <!-- Answer Content -->
                        <v-md-preview :text="parseMessageContent(String(item.answer)).answer" />
                    </div>
                    
                    <!-- Retrieved Docs (Sources) -->
                    <div v-if="item.retriever_docs && item.retriever_docs.length > 0" class="sources-section">
                        <div class="sources-header" @click="toggleDocs(item)">
                           <el-icon><Document /></el-icon>
                           <span>参考文档 ({{ item.retriever_docs.length }})</span>
                           <el-icon class="toggle-icon" :class="{ 'is-active': item.showDocs }"><ArrowDown /></el-icon>
                        </div>
                        <div v-show="item.showDocs" class="sources-content">
                           <el-collapse accordion>
                              <el-collapse-item 
                                 v-for="(doc, idx) in item.retriever_docs" 
                                 :key="idx" 
                                 :title="doc.knowledge_doc_name" 
                                 :name="idx"
                              >
                                 <div class="doc-text">
                                    <v-md-preview :text="doc.content" />
                                 </div>
                              </el-collapse-item>
                           </el-collapse>
                        </div>
                    </div>
                 </div>
              </div>
           </div>
        </div>
        
        <!-- Loading Indicator -->
        <div v-if="loading" class="typing-indicator">
           <div class="dot"></div>
           <div class="dot"></div>
           <div class="dot"></div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-section">
         <div class="input-wrapper glass-effect">
            <el-input
              v-model="message"
              class="main-input"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 8 }"
              placeholder="发送消息给 AI..."
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.ctrl.enter="handleMultilineInput"
            />
            <div class="input-actions">
               <el-tooltip content="发送 (Enter)" placement="top">
                  <el-button 
                     type="primary" 
                     class="send-btn" 
                     :disabled="!message.trim() || loading" 
                     @click="sendMessage"
                     circle
                  >
                     <el-icon><Position /></el-icon>
                  </el-button>
               </el-tooltip>
            </div>
         </div>
         <div class="footer-disclaimer">
            AI 生成的内容可能包含错误，请自行核实。
         </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import { getRequest, postRequest, deleteRequest } from '@/utils/http';
import { ElMessage } from 'element-plus';
import ChatList from '@/components/ChatList.vue';
import { 
  Position, 
  Fold, 
  Collection,
  Monitor,
  ArrowDown,
  Cpu,
  Document
} from '@element-plus/icons-vue';

// State
const isSidebarCollapsed = ref(false);
const loadingList = ref(false);
const conversionsList = ref<any>([]);
let conversionMessage = ref<any>([]);
const knowledgebaseList = ref<any>([]);
const choosedKnowledgeBaseId = ref<any>('');
const message = ref<any>('');
const currentConversationId = ref<any>('');
const chatContent = ref<HTMLElement | null>(null);
const loading = ref<boolean>(false);

// Helper to parse message content (Thinking vs Answer)
function parseMessageContent(message: string) {
  let hasThink = false;
  let think = '';
  let answer = message;

  // Check for THINKING: ... ANSWER: ... format
  if (message.includes('THINKING:')) {
      const answerMatch = message.match(/ANSWER:([\s\S]*)/);
      const thinkMatch = message.match(/THINKING:([\s\S]*?)(?=ANSWER:|$)/);
      
      if (thinkMatch) {
         hasThink = true;
         think = thinkMatch[1].trim();
      }
      if (answerMatch) {
         answer = answerMatch[1].trim();
      } else if (hasThink) {
         // If we have thinking but no ANSWER: tag yet, user might still be streaming thinking or finished thinking
         // We might want to clear answer if it's all thinking
         // But usually streaming appends.
         // Let's assume everything after THINKING is think until ANSWER appears
         answer = ''; 
      }
  } 
  // Check for <think>...</think> format
  else if (message.includes('<think>')) {
      hasThink = true;
      const thinkMatch = message.match(/<think>([\s\S]*?)<\/think>/);
      if (thinkMatch) {
          think = thinkMatch[1].trim();
          answer = message.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
      } else {
          // Open tag but no close tag? Streaming...
          const openMatch = message.match(/<think>([\s\S]*)/);
          if (openMatch) {
             think = openMatch[1].trim();
             answer = ''; // All is thinking
          }
      }
  }

  return { hasThink, think, answer };
}

// Helper to toggle thinking visibility
function toggleThink(item: any) {
  item.showThink = !item.showThink;
}

// Helper to toggle docs visibility
function toggleDocs(item: any) {
  item.showDocs = !item.showDocs;
}

// Core Logic
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
}

function fillInput(text: string) {
  message.value = text;
  // Optional: auto focus input
}

function getCurrentConversationTitle() {
  if (!currentConversationId.value) return '新对话';
  const conversation = conversionsList.value.find((item: any) => 
    item.conversation_id === currentConversationId.value
  );
  return conversation ? conversation.conversationName : '新对话';
}

function getSelectedKnowledgeBaseName() {
  if (!choosedKnowledgeBaseId.value) return '';
  const knowledgeBase = knowledgebaseList.value.find((item: any) => 
    item.id === choosedKnowledgeBaseId.value
  );
  return knowledgeBase ? knowledgeBase.knowledgeBaseName : '';
}

function handleMultilineInput(e: KeyboardEvent) {
  message.value += '\n';
}

async function sendMessage() {
  if (!message.value.trim() || loading.value) return;
  
  let tempValue = message.value;
  message.value = ''; // clear immediately

  // 检查是否有当前选中的对话，如果没有则创建新对话
  if (!currentConversationId.value) {
    await createConversation();
  }

  loading.value = true;
  let chatItemUser: any = {
    id: Date.now(),
    query: tempValue,
    answer: '',
  };
  
  conversionMessage.value.push(chatItemUser);
  scrollToBottom();
  
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const token = localStorage.getItem('token');
    
    const response: any = await fetch(baseURL + '/v1/api/mark/chat/chat-message', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify({
        "conversation_id": currentConversationId.value.toString(),
        "message": tempValue,
        "user_id": "mark",
        "streaming": true
      })
    });

    if (response.status === 401) {
      ElMessage.error('认证失败，请重新登录');
      loading.value = false;
      return;
    }

    if (!response.ok) throw new Error('网络错误');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let resultText = '';
    const lastMsgIndex = conversionMessage.value.length - 1;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      resultText += decoder.decode(value, { stream: true });
      conversionMessage.value[lastMsgIndex].answer = resultText;
      scrollToBottom();
    }

  } catch (error: any) {
    console.error(error);
    message.value = tempValue; // restore if failed
    ElMessage.error('发送失败，请重试');
  } finally {
    loading.value = false;
    reGetConversionsList();
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContent.value) {
      const el = chatContent.value;
      el.scrollTo({
         top: el.scrollHeight,
         behavior: 'smooth'
      });
    }
  });
}

async function getConversionsList() {
  loadingList.value = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const data = await getRequest<any>(baseURL + '/v1/api/mark/chat/chat-message/mark');
    conversionsList.value = data.data.reverse();

    if (conversionsList.value.length > 0 && !currentConversationId.value) {
      const latestConversationId = conversionsList.value[0].conversation_id;
      handleItemClick(latestConversationId);
    }
  } finally {
    loadingList.value = false;
  }
}

async function reGetConversionsList() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/chat/chat-message/mark');
  conversionsList.value = data.data.reverse();
}

async function handleItemClick(conversation_id: string) {
  if (currentConversationId.value === conversation_id && conversionMessage.value.length > 0) return;
  
  currentConversationId.value = conversation_id;
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  
  const data = await getRequest<any>(baseURL+'/v1/api/mark/chat/chat-history/' + conversation_id);
  conversionMessage.value = data.data || [];

  const lastMsg = data.data[data.data.length - 1];
  if (lastMsg) {
    choosedKnowledgeBaseId.value = lastMsg.current_knowledge_baseid || '';
  }

  scrollToBottom();
}

async function getKnowledgeBaseList() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL+'/v1/api/mark/chat/knowledge_base');
  knowledgebaseList.value = data.data;
}

async function switchKnowledgeBase(knowledgeBaseId: string) {
  choosedKnowledgeBaseId.value = knowledgeBaseId;
  const kbName = getSelectedKnowledgeBaseName();
  ElMessage.success(`已切换至: ${kbName}`);
  
  if (!currentConversationId.value) return;
  
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  await postRequest<any>(baseURL+'/v1/api/mark/chat/knowledge_base', {
    "user_id": "mark",
    "conversation_id": currentConversationId.value.toString(),
    "knowledge_base_id": knowledgeBaseId
  });
}

async function createConversation() {
  const knowledge_base_id = knowledgebaseList.value[0]?.id || '';
  const user_id = "mark";
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await postRequest<any>(baseURL+'/v1/api/mark/chat/create-conversation', {
    "knowledge_base_id": knowledge_base_id,
    "username": user_id
  });
  
  currentConversationId.value = data.data.conversation_id;
  
  await getConversionsList();
  conversionMessage.value = []; 
}

async function deleteConversation(conversationId: string) {
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const user_id = "mark"; // Keeping consistent with other hardcoded user_id usage
    
    // API endpoint per backend spec: /conversation/{user_id}/{conversation_id}
    await deleteRequest<any>(`${baseURL}/v1/api/mark/chat/conversation/${user_id}/${conversationId}`);
    
    ElMessage.success('对话已删除');
    
    // Refresh list
    await getConversionsList();
    
    // If deleted current conversation, reset state
    if (currentConversationId.value === conversationId) {
       currentConversationId.value = '';
       conversionMessage.value = [];
       // If list not empty, select first available
       if (conversionsList.value.length > 0) {
          handleItemClick(conversionsList.value[0].conversation_id);
       }
    }
  } catch (error) {
    console.error('Failed to delete conversation:', error);
    ElMessage.error('删除失败，请重试');
  }
}

onMounted(() => {
  getConversionsList();
  getKnowledgeBaseList();
});
</script>

<style scoped>
/* Reset & Layout */
.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
  background: #ffffff;
  /* position: absolute; */ /* Removed absolute positioning to prevent overlap with App navbar */
  /* top: 0; */
  /* left: 0; */
  /* right: 0; */
  /* bottom: 0; */
  overflow: hidden;
  position: relative; /* Ensure it stays within parent flow */
}

/* Main Area */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #f7f9fb;
}

.chat-navbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  z-index: 5;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-menu-btn {
  display: none;
  cursor: pointer;
}

.current-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.kb-select-btn {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 6px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #555;
  transition: all 0.2s;
  cursor: pointer;
}

.kb-select-btn:hover {
  background: #f9f9f9;
  border-color: rgba(0,0,0,0.15);
  color: #333;
}

.kb-select-btn.active {
   background: #e6f0ff;
   border-color: #3a7afe;
   color: #0256d0;
}

/* Messages */
.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center; /* Center content horizontally */
}

.messages-wrapper > * {
  width: 100%;
  max-width: 800px;
}

/* Welcome Screen */
.empty-state {
  margin-top: 10vh;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: white;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.logo-emoji {
  font-size: 40px;
}

.empty-state h3 {
  font-size: 24px;
  color: #333;
  margin-bottom: 40px;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  width: 100%;
  max-width: 700px;
}

.suggestion-card {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: left;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.suggestion-card:hover {
  border-color: #3a7afe;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 122, 254, 0.1);
}

.card-icon {
  font-size: 24px;
}

.card-text {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

/* Message Bubbles */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 40px;
}

.message-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-group {
  display: flex;
  gap: 16px;
  width: 100%;
}

.message-group.user {
  justify-content: flex-end;
}

.message-group.assistant {
  justify-content: flex-start;
}

.user-bubble {
  background: #3a7afe; /* Primary Blue for User */
  color: white;
  padding: 12px 18px;
  border-radius: 18px 18px 2px 18px; /* Classic bubble shape */
  max-width: 85%;
  font-size: 15px;
  line-height: 1.6;
  box-shadow: 0 2px 6px rgba(58, 122, 254, 0.2);
}

/* Override child text colors if needed */
.user-bubble :deep(p) {
  margin: 0;
}

.assistant-bubble {
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  background: transparent;
  width: 100%;
}

.assistant-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0; /* Important for flex child to shrink */
}

/* User Message Styles Override */
.user-bubble :deep(.v-md-editor-preview) {
  padding: 0;
  color: white;
  background: transparent;
}
.user-bubble :deep(.github-markdown-body) {
  padding: 0;
  color: white;
  background: transparent;
  font-family: inherit;
  font-size: 15px;
}
.user-bubble :deep(p) {
  margin: 0;
  white-space: pre-wrap;
}

/* Assistant Message Styles Override */
.assistant-bubble :deep(.v-md-editor-preview) {
  padding: 0 8px;
  background: transparent;
}
.assistant-bubble :deep(.github-markdown-body) {
  padding: 0;
  background: transparent;
  font-family: inherit;
  font-size: 15px;
  color: #333;
}

/* Think Section */
.think-section {
  margin-bottom: 12px;
  border-radius: 8px;
  background: #f0f4ff;
  border: 1px solid rgba(58, 122, 254, 0.1);
  overflow: hidden;
}

.think-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  color: #3a7afe;
  font-size: 13px;
  font-weight: 500;
  background: rgba(58, 122, 254, 0.05);
  transition: background 0.2s;
}

.think-header:hover {
  background: rgba(58, 122, 254, 0.1);
}

.think-content {
  padding: 12px;
  background: rgba(255,255,255,0.5);
  font-size: 13px;
  color: #666;
}

.think-content :deep(.github-markdown-body) {
  font-family: 'Consolas', 'Monaco', monospace;
  color: #666;
  background: transparent;
}

/* Sources Section */
.sources-section {
  margin-left: 8px;
  max-width: 600px;
}

.sources-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 0;
  transition: color 0.2s;
}

.sources-header:hover {
  color: #3a7afe;
}

.sources-content {
  margin-top: 8px;
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.toggle-icon {
  margin-left: auto;
  transition: transform 0.2s;
  font-size: 12px;
}

.toggle-icon.is-active {
  transform: rotate(180deg);
}

/* Doc Content */
.doc-text {
  max-height: 200px;
  overflow-y: auto;
  font-size: 13px;
}

.doc-text :deep(.github-markdown-body) {
  padding: 0;
  font-size: 13px;
  background: transparent;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 0;
  box-shadow: 0 4px 10px rgba(3, 105, 225, 0.2);
}

/* Input Area */
.input-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 24px 24px 24px;
  background: linear-gradient(to bottom, rgba(247,249,251,0), #f7f9fb 30%);
}

.input-wrapper {
  width: 100%;
  max-width: 800px;
  position: relative;
  background: #fff;
  border: 1px solid rgba(0,0,0,0.08); /* Lighter border */
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: #3a7afe;
  box-shadow: 0 4px 24px rgba(58, 122, 254, 0.12);
  transform: translateY(-2px);
}

.main-input :deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
  padding: 16px 60px 16px 16px !important;
  resize: none;
  font-family: inherit;
  font-size: 15px;
  color: #333;
}

.input-actions {
  position: absolute;
  bottom: 10px;
  right: 12px;
}

.send-btn {
  width: 36px;
  height: 36px;
  display: flex !important;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.footer-disclaimer {
  font-size: 12px;
  color: #999;
  margin-top: 12px;
  text-align: center;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  margin-left: 52px;
  background: #fff;
  border-radius: 0 16px 16px 16px;
  width: fit-content;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  margin-bottom: 24px; /* Space it out */
}

.dot {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* KB List Popover Content */
.kb-list {
  max-height: 300px;
  overflow-y: auto;
}

.kb-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
  color: #555;
}

.kb-option:hover {
  background: #f5f7fa;
  color: #333;
}

.kb-option.selected {
  background: #e6f0ff;
  color: #0256d0;
  font-weight: 500;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
    padding: 8px;
    margin-right: 8px;
  }
}
</style>
