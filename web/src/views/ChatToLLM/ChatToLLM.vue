<template>
  <el-container class="chat-container">
    <!-- Left Sidebar for Chat List -->
    <el-aside class="chat-aside glass-panel">
      <div class="aside-header">
        <h3>会话列表</h3>
        <el-button type="primary" @click="createConversation" class="create-button">
          <el-icon><Plus /></el-icon>新建对话
        </el-button>
      </div>
      <div class="chat-list custom-scrollbar">
        <ChatLogItem class="chat-log-item" :class="{ active: currentConversationId === item.conversation_id }"
          v-for="item in conversionsList" :key="item.conversation_id" :title="String(item.conversationName)"
          :conversation_id="item.conversation_id" @click="handleItemClick(item.conversation_id)"
          @updateTitle="updateConversationTitle(item.conversation_id, $event)" @refreshList="getConversionsList" />
      </div>
    </el-aside>

    <!-- Main Chat Interface -->
    <el-main class="chat-main glass-panel">
      <div class="chat-header">
        <h2>{{ getCurrentConversationTitle() }}</h2>
        <span class="chat-subtitle">{{ getSelectedKnowledgeBaseName() }}</span>
      </div>
      
      <div class="chat-content custom-scrollbar" ref="chatContent">
        <div class="welcome-message" v-if="!conversionMessage.length">
          <div class="welcome-icon">🤖</div>
          <h3>欢迎使用智能助手</h3>
          <p>开始新的对话，探索AI的无限可能</p>
        </div>
        <div class="message-container" v-for="(item, index) in conversionMessage" :key="index">
          <div class="message-item-user">
            <MessageItem_User :message="String(item.query)" />
          </div>
          <div class="message-item-assistant">
            <MessageItem_Assistant :message="String(item.answer)" :retrievedDocs=item.retriever_docs />
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area glass-input">
        <el-input v-model="message" class="input-box" autosize type="textarea" placeholder="输入您的问题..."
          @keyup.enter.exact="sendMessage" @keyup.ctrl.enter="handleMultilineInput" />
        <div class="action-buttons">
          <el-tooltip content="发送消息" placement="top">
            <el-button type="primary" :disabled="loading || !message.trim()" @click="sendMessage" class="send-button">
              <el-icon><Position /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        <div class="loading-container" v-if="loading">
          <div class="thinking-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span class="loading-text">AI思考中</span>
        </div>
      </div>
    </el-main>

    <!-- Right Sidebar for Knowledge Base -->
    <el-aside class="chat-aside-right glass-panel">
      <div class="aside-header">
        <h3>知识库列表</h3>
      </div>
      <div class="knowledge-base-list custom-scrollbar">
        <KnowledgeBaseItem v-for="item in knowledgebaseList" :key="item.id" class="knowledge-base-item"
          :class="{ active: choosedKnowledgeBaseId === item.id }" :knowledgeBaseName="String(item.knowledgeBaseName)"
          :knowledgeBaseId="String(item.id)" @click="switchKnowledgeBase(item.id)" />
      </div>
    </el-aside>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import MessageItem_User from "@/components/MessageItem_User.vue";
import MessageItem_Assistant from "@/components/MessageItem_Assistant.vue";
import ChatLogItem from '@/components/ChatLogItem.vue';
import KnowledgeBaseItem from '@/components/KnowledgeBaseItem.vue';
import { getRequest, postRequest } from '@/utils/http';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Plus, Position } from '@element-plus/icons-vue';

const conversionsList = ref<any>([]);
let conversionMessage = ref<any>([]);
const knowledgebaseList = ref<any>([]);
const choosedKnowledgeBaseId = ref<any>('');
const message = ref<any>('');
const currentConversationId = ref<any>('');
let chatContent = ref<any>(null);
const loading = ref<boolean>(false);

// 获取当前会话标题
function getCurrentConversationTitle() {
  if (!currentConversationId.value) return '新对话';
  const conversation = conversionsList.value.find((item: { conversation_id: string; }) => 
    item.conversation_id === currentConversationId.value
  );
  return conversation ? conversation.conversationName : '对话';
}

// 获取选中的知识库名称
function getSelectedKnowledgeBaseName() {
  if (!choosedKnowledgeBaseId.value) return '';
  const knowledgeBase = knowledgebaseList.value.find((item: { id: string; }) => 
    item.id === choosedKnowledgeBaseId.value
  );
  return knowledgeBase ? `使用知识库: ${knowledgeBase.knowledgeBaseName}` : '';
}

// 处理多行输入
function handleMultilineInput(e: KeyboardEvent) {
  e.preventDefault(); // 阻止默认的回车发送
  message.value += '\n'; // 添加换行符
}

async function sendMessage() {
  if (!message.value.trim()) return;
  let tempValue = message.value;

  // 检查是否有当前选中的对话，如果没有则创建新对话
  if (!currentConversationId.value) {
    await createConversation();
  }

  loading.value = true; // 显示加载状态
  let chatItemUser: any = {
    id: Date.now(),
    query: tempValue,
    answer: '',
  };
  message.value = '';
  conversionMessage.value.push(chatItemUser);
  scrollToBottom();
  let message_length = conversionMessage.value.length;
  
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const token = localStorage.getItem('token') // 获取 token
    const response: any = await fetch(baseURL + '/v1/api/mark/chat/chat-message', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '' // 添加 token 到请求头
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
      return;
    }

    if (!response.ok) throw new Error('网络错误，无法发送消息');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let resultText = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      resultText += decoder.decode(value, { stream: true });
      conversionMessage.value[message_length - 1].answer = resultText;
      scrollToBottom();
    }

  } catch (error: any) {
    console.error(error);
    message.value = tempValue;
    ElMessage.error('发送失败，请重试');

  } finally {
    loading.value = false; // 隐藏加载状态
    reGetConversionsList();
    handleItemClick(currentConversationId.value);
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContent.value) {
      chatContent.value.scrollTop = chatContent.value.scrollHeight;
    }
  });
}

async function getConversionsList() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/chat/chat-message/mark');
  conversionsList.value = data.data.reverse();

  if (conversionsList.value.length > 0) {
    const latestConversationId = conversionsList.value[0].conversation_id;
    handleItemClick(latestConversationId);
  }
}
async function reGetConversionsList() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL + '/v1/api/mark/chat/chat-message/ai');
  conversionsList.value = data.data.reverse();
}
async function handleItemClick(conversation_id: string) {
  currentConversationId.value = conversation_id;
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  // 加载当前对话的历史消息
  const data = await getRequest<any>(baseURL+'/v1/api/mark/chat/chat-history/' + conversation_id);
  conversionMessage.value = data.data;

  // 设置为当前对话关联的知识库 ID
  let dataLength = data.data.length;
  choosedKnowledgeBaseId.value = data.data[dataLength - 1]?.current_knowledge_baseid || '';

  scrollToBottom();
}

async function getKnowledgeBaseList() {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await getRequest<any>(baseURL+'/v1/api/mark/chat/knowledge_base');
  knowledgebaseList.value = data.data;
}

async function switchKnowledgeBase(knowledgeBaseId: string) {
  choosedKnowledgeBaseId.value = knowledgeBaseId;
  if (!currentConversationId.value) return;
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const response: any = await postRequest<any>(baseURL+'/v1/api/mark/chat/knowledge_base', {
    "user_id": "mark",
    "conversation_id": currentConversationId.value.toString(),
    "knowledge_base_id": knowledgeBaseId
  });

  if (response.code === 200) {
    ElMessage.info('切换知识库成功！');
    // await handleItemClick(currentConversationId.value);
  }
}

async function createConversation() {
  const knowledge_base_id = knowledgebaseList.value[0]?.id || '';
  const user_id = "mark";
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const data = await postRequest<any>(baseURL+'/v1/api/mark/chat/create-conversation', {
    "knowledge_base_id": knowledge_base_id,
    "username": user_id
  });
  
  // 设置当前对话ID
  currentConversationId.value = data.data.conversation_id;
  
  // 更新对话列表并选中新创建的对话
  await getConversionsList();
  await handleItemClick(data.data.conversation_id);
  
  return data.data.conversation_id;
}

function updateConversationTitle(conversationId: string, newTitle: string) {
  const conversation = conversionsList.value.find((item: { conversation_id: string; }) => item.conversation_id === conversationId);
  if (conversation) {
    conversation.conversationName = newTitle;
  }
}

onMounted(() => {
  getConversionsList();
  scrollToBottom();
  getKnowledgeBaseList();
});
</script>

<style scoped>
.chat-container {
  height: 100%;
  width: 100%;
  gap: 15px;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chat-aside,
.chat-aside-right {
  width: 20% !important;
  display: flex;
  flex-direction: column;
  margin: 12px;
  transition: all 0.3s ease;
}

.aside-header {
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.aside-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chat-main {
  width: 60% !important;
  margin: 12px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  padding: 0 !important;
}

.chat-header {
  padding: 20px 30px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  text-align: center;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.chat-subtitle {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  display: block;
}

.create-button {
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  border-radius: 12px;
  height: 40px;
  border: none;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #fff;
  box-shadow: 0 4px 12px rgba(3, 105, 225, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(3, 105, 225, 0.5);
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  position: relative;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  text-align: center;
  padding: 20px;
  animation: fadeIn 0.5s ease-in-out;
}

.welcome-icon {
  font-size: 50px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-container {
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-in-out;
}

.message-item-user {
  align-self: flex-end;
  max-width: 80%;
  margin: 10px 0;
  transform-origin: right bottom;
  animation: popIn 0.3s ease-in-out;
}

.message-item-assistant {
  align-self: flex-start;
  max-width: 90%;
  margin: 10px 0;
  transform-origin: left bottom;
  animation: popIn 0.3s ease-in-out;
}

@keyframes popIn {
  0% { opacity: 0; transform: scale(0.95); }
  100% { opacity: 1; transform: scale(1); }
}

.glass-input {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  position: relative;
}

.input-area {
  padding: 20px 30px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.input-box {
  flex: 1;
}

.input-box :deep(.el-textarea__inner) {
  border-radius: 16px;
  min-height: 60px !important;
  max-height: 150px;
  resize: none;
  padding: 16px;
  font-size: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.95);
}

.input-box :deep(.el-textarea__inner:focus) {
  box-shadow: 0 4px 16px rgba(3, 105, 225, 0.15);
  border-color: #8fbaf3;
}

.action-buttons {
  display: flex;
  align-items: center;
}

.send-button {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  box-shadow: 0 4px 12px rgba(3, 105, 225, 0.3);
  transition: all 0.3s ease;
}

.send-button:hover {
  transform: translateY(-2px) rotate(5deg);
  box-shadow: 0 6px 20px rgba(3, 105, 225, 0.5);
}

.send-button:disabled {
  background: #cccccc;
  box-shadow: none;
  transform: none;
}

.loading-container {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.3s ease-in-out;
  z-index: 10;
}

.loading-text {
  font-size: 14px;
}

.thinking-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.thinking-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
  animation: dotPulse 1.5s infinite;
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotPulse {
  0%, 60%, 100% { transform: scale(1); opacity: 1; }
  30% { transform: scale(1.5); opacity: 0.7; }
}

.chat-log-item {
  padding: 12px 16px;
  margin: 8px 10px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.chat-log-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chat-log-item.active {
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(3, 105, 225, 0.2);
}

.knowledge-base-item {
  margin: 8px 10px;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.knowledge-base-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.knowledge-base-item.active {
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  color: white;
  box-shadow: 0 6px 16px rgba(3, 105, 225, 0.2);
}

/* 自定义滚动条 */
.custom-scrollbar {
  scrollbar-width: thin;
  overflow-y: scroll;
  scrollbar-color: rgba(0, 0, 0, 0.2) rgba(0, 0, 0, 0.05);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

/* 在小屏幕下的响应式设计 */
@media screen and (max-width: 992px) {
  .chat-aside, .chat-aside-right {
    width: 30% !important;
  }
  
  .chat-main {
    width: 40% !important;
  }
}

@media screen and (max-width: 768px) {
  .chat-container {
    flex-direction: column;
  }
  
  .chat-aside, .chat-aside-right {
    width: calc(100% - 24px) !important;
    margin: 12px;
    height: auto;
    max-height: 250px;
  }
  
  .chat-main {
    width: calc(100% - 24px) !important;
    margin: 0 12px;
    flex: 1;
  }
  
  .input-area {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}
</style>
