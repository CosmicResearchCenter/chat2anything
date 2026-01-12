<template>
  <aside class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <el-button 
        class="new-chat-btn" 
        @click="$emit('create')" 
        :icon="Plus"
        v-if="!isCollapsed"
      >
        新对话
      </el-button>
      <el-button 
        v-else 
        class="new-chat-btn-icon" 
        @click="$emit('create')" 
        :icon="Plus" 
        circle
      />
    </div>

    <div class="sidebar-content custom-scrollbar">
      <div v-if="loading" class="loading-state">
         <el-skeleton :rows="3" animated />
      </div>
      <div v-else class="conversation-list">
         <div 
          v-for="item in list" 
          :key="item.conversation_id"
          class="conversation-item"
          :class="{ active: currentId === item.conversation_id }"
          @click="$emit('select', item.conversation_id)"
         >
            <el-icon class="chat-icon"><ChatLineRound /></el-icon>
            <div class="item-content" v-if="!isCollapsed">
              <span class="item-title">{{ item.conversationName || '未命名对话' }}</span>
            </div>
            <div class="item-actions" v-if="!isCollapsed">
              <el-popconfirm
                title="确定删除此对话吗?"
                @confirm="$emit('delete', item.conversation_id)"
                width="200"
              >
                <template #reference>
                  <div class="delete-btn" @click.stop>
                     <el-icon><Delete /></el-icon>
                  </div>
                </template>
              </el-popconfirm>
            </div>
         </div>
      </div>
    </div>

    <div class="sidebar-footer">
      <el-tooltip content="折叠/展开侧边栏" placement="right" :disabled="!isCollapsed">
         <div class="collapse-trigger" @click="$emit('toggle')">
            <el-icon><component :is="isCollapsed ? Expand : Fold" /></el-icon>
         </div>
      </el-tooltip>
    </div>
  </aside>
</template>

<script lang="ts" setup>
import { Plus, ChatLineRound, Fold, Expand, Delete } from '@element-plus/icons-vue';

defineProps<{
  isCollapsed: boolean;
  loading: boolean;
  list: any[];
  currentId: string;
}>();

defineEmits<{
  (e: 'create'): void;
  (e: 'select', id: string): void;
  (e: 'delete', id: string): void;
  (e: 'toggle'): void;
}>();
</script>

<style scoped>
.sidebar {
  width: 260px;
  background: #f9f9f9;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
  z-index: 10;
  height: 100%;
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.new-chat-btn {
  width: 100%;
  border-radius: 8px;
  height: 44px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  background-color: white;
  border: 1px solid #e4e7ed;
  color: #303133;
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #c0c4cc;
  background-color: #fafafa;
  color: #000;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px 20px 10px;
}

.loading-state {
    padding: 20px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  color: #4a4a4a;
  transition: background 0.2s;
  height: 44px;
}

.conversation-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.conversation-item:hover .item-actions {
  opacity: 1;
}

.conversation-item.active {
  background: rgba(0, 0, 0, 0.06);
  color: #000;
  font-weight: 500;
}

.chat-icon {
  font-size: 18px;
  color: #666;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.item-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.delete-btn {
  padding: 4px;
  border-radius: 4px;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.delete-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: flex-end; 
}

.collapse-trigger {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
  border-radius: 4px;
  transition: background 0.2s;
}

.collapse-trigger:hover {
  background: rgba(0, 0, 0, 0.05);
}

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
  .sidebar {
    position: fixed;
    height: 100%;
    transform: translateX(-100%); 
    width: 280px;
    box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  }
  
  .sidebar.collapsed {
     transform: translateX(0) !important;
     width: 280px; 
  }
}
</style>
