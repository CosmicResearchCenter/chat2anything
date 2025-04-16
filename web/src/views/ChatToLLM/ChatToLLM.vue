<template>
  <el-container style="height: 100%; width: 100%;">
    <!-- Left Sidebar for Chat List -->
    <el-aside class="chat-aside">
      <el-button type="primary" @click="createConversation" class="create-button">新建对话</el-button>
      <div class="chat-list">
        <ChatLogItem class="chat-log-item" :class="{ active: currentConversationId === item.conversation_id }"
          v-for="item in conversionsList" :key="item.conversation_id" :title="String(item.conversationName)"
          :conversation_id="item.conversation_id" @click="handleItemClick(item.conversation_id)"
          @updateTitle="updateConversationTitle(item.conversation_id, $event)" @refreshList="getConversionsList" />
      </div>
    </el-aside>

    <!-- Main Chat Interface -->
    <el-main class="chat-main">
      <div class="chat-content" ref="chatContent">
        <div class="message-container" v-for="item in conversionMessage" :key="item.id">
          <div class="message-item-user">
            <MessageItem_User :message="String(item.query)" />
          </div>
          <div class="message-item-assistant">
            <MessageItem_Assistant :message="String(item.answer)" :retrievedDocs=item.retriever_docs />
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <el-input v-model="message" class="input-box" autosize type="textarea" placeholder="Type your message..."
          @keyup.enter="sendMessage" />
        <el-button type="primary" @click="sendMessage">Send</el-button>
        <el-loading v-if="loading" text="Sending..."></el-loading> <!-- Loading indicator -->
      </div>
    </el-main>

    <!-- Right Sidebar for Knowledge Base -->
    <el-aside class="chat-aside-right">
      <div class="knowledge-base-list">
        <KnowledgeBaseItem v-for="item in knowledgebaseList" :key="item.id" class="knowledge-base-item"
          :class="{ active: choosedKnowledgeBaseId === item.id }" :knowledgeBaseName="String(item.knowledgeBaseName)"
          :knowledgeBaseId="String(item.id)" @click="switchKnowledgeBase(item.id)" />
      </div>
    </el-aside>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import MessageItem_User from "@/components/MessageItem_User.vue";
import MessageItem_Assistant from "@/components/MessageItem_Assistant.vue";
import ChatLogItem from '@/components/ChatLogItem.vue';
import KnowledgeBaseItem from '@/components/KnowledgeBaseItem.vue';
import { getRequest, postRequest } from '@/utils/http';
import { ElMessageBox, ElMessage } from 'element-plus';
import { ElLoading } from 'element-plus';

const conversionsList = ref<any>([]);
let conversionMessage = ref<any>([]);
const knowledgebaseList = ref<any>([]);
const choosedKnowledgeBaseId = ref<any>('');
const message = ref<any>('');
const currentConversationId = ref<any>('');
let chatContent = ref<any>(null);
const loading = ref<boolean>(false);

async function sendMessage() {
  if (message.value === '') return;
  let tempValue = message.value;

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
      // removeToken(); // token 失效时清除
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
  const data = await getRequest<any>(baseURL+'/v1/api/mark/knowledgebase');
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
  getConversionsList();
  handleItemClick(data.data.conversation_id);
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
.chat-aside,
.chat-aside-right {
  width: 20% !important;
  background: rgba(248, 249, 250, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  margin: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.chat-main {
  width: 60% !important;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  margin: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.create-button {
  width: 100%;
  margin-bottom: 20px;
  border-radius: 12px;
  height: 45px;
  background: #0245a3;
  border: none;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 198, 251, 0.3);
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 198, 251, 0.5);
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 50px;
  /* background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%); */
  scrollbar-width: thin;
}

.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.message-container {
  display: flex;
  flex-direction: column;
}

.message-item-user {
  align-self: flex-end;
  max-width: 80%;
  margin: 10px 0;
}

.message-item-assistant {
  align-self: flex-start;
  max-width: 80%;
  margin: 10px 0;
}

.input-area {
  padding: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0 0 16px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-box {
  flex: 1;
}

.input-box :deep(.el-textarea__inner) {
  border-radius: 12px;
  min-height: 60px !important;
  resize: none;
  padding: 16px;
  font-size: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  background: rgba(248, 249, 250, 0.95);
}

.input-box :deep(.el-textarea__inner:focus) {
  box-shadow: 0 4px 16px rgba(0, 198, 251, 0.2);
  border-color: #8fbaf3;
}

.message-item-user,
.message-item-assistant {
  /* margin: 16px 0; */
  /* max-width: 80%; */
}

.chat-log-item {
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.chat-log-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.chat-log-item.active {
  background: #8fbaf3;
  color: #0b3763;
}

.knowledge-base-item {
  margin: 8px 0;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.knowledge-base-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 12px rgba(0, 198, 251, 0.15);
}

.knowledge-base-item.active {
  background: #0245a3;
  color: white;
  box-shadow: 0 6px 16px rgba(0, 198, 251, 0.25);
  border: none;
}

.knowledge-base-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Add some styles for loading */
.el-loading {
  margin-left: 10px;
  /* Adjust as needed */
}

.el-button {
  border-radius: 12px;
  height: 45px;
  background: #0245a3;
  border: none;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 198, 251, 0.3);
}

.el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 198, 251, 0.5);
}

/* 在小屏幕下，调整布局为上下排列 */
@media screen and (max-width: 768px) {
  .chat-aside,
  .chat-aside-right {
    width: 100% !important;
    margin: 0;
    display: none;
  }

  .chat-main {
    width: 100% !important;
    margin: 0;
  }

  .input-area {
    /* 调整输入区域样式 */
    flex-direction: column;
    align-items: stretch;
  }

  .input-box {
    width: 100%;
  }

  .el-button {
    width: 100%;
    margin-top: 10px;
  }
}
</style>
