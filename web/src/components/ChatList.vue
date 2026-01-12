<template>
  <aside class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <el-button 
        class="new-chat-btn" 
        @click="$emit('create')" 
        :icon="Plus"
        v-if="showFull"
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
              <div class="item-content" v-if="showFull">
              <span class="item-title">{{ item.conversationName || '未命名对话' }}</span>
            </div>
              <div class="item-actions" v-if="showFull">
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
      <el-tooltip content="折叠/展开侧边栏" placement="right" :disabled="showFull">
         <div class="collapse-trigger" @click="$emit('toggle')">
            <el-icon><component :is="isCollapsed ? Expand : Fold" /></el-icon>
         </div>
      </el-tooltip>
    </div>
  </aside>
</template>

<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { Plus, ChatLineRound, Fold, Expand, Delete } from '@element-plus/icons-vue';

const props = defineProps<{
  isCollapsed: boolean;
  loading: boolean;
  list: any[];
  currentId: string;
}>();

const isMobile = ref(false);
let mediaQuery: MediaQueryList | null = null;
let onMediaChange: ((e: MediaQueryListEvent) => void) | null = null;

const showFull = computed(() => {
  // 移动端：isCollapsed 被用作“打开侧栏”，这里仍需要展示完整文字
  // 桌面端：isCollapsed 为折叠（仅图标）
  return isMobile.value || !props.isCollapsed;
});

onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 768px)');
  isMobile.value = mediaQuery.matches;

  onMediaChange = (e: MediaQueryListEvent) => {
    isMobile.value = e.matches;
  };

  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', onMediaChange);
  } else {
    // 兼容旧浏览器
    (mediaQuery as any).addListener(onMediaChange);
  }
});

onBeforeUnmount(() => {
  if (!mediaQuery || !onMediaChange) return;
  if (mediaQuery.removeEventListener) {
    mediaQuery.removeEventListener('change', onMediaChange);
  } else {
    (mediaQuery as any).removeListener(onMediaChange);
  }
});

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
  background: var(--bg-sidebar, var(--bg-card));
  border-right: 1px solid var(--border-light);
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
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
  background-color: var(--bg-card);
  border: 1px solid var(--border-light);
  color: var(--text-primary);
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-300);
  background-color: var(--bg-hover);
  color: var(--primary-700);
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
  color: var(--text-secondary);
  transition: background 0.2s;
  height: 44px;
}

.conversation-item:hover {
  background: var(--bg-hover);
}

.conversation-item:hover .item-actions {
  opacity: 1;
}

.conversation-item.active {
  background: var(--bg-active);
  color: var(--text-primary);
  font-weight: 500;
}

.chat-icon {
  font-size: 18px;
  color: var(--text-tertiary);
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
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.delete-btn:hover {
  color: var(--danger-500);
  background: var(--danger-100);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-light);
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
  color: var(--text-secondary);
  border-radius: 4px;
  transition: background 0.2s;
}

.collapse-trigger:hover {
  background: var(--bg-hover);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--border-light);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-medium);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100%;
    transform: translateX(-100%);
    width: 280px;
    box-shadow: var(--shadow-xl);
  }

  .sidebar.collapsed {
     transform: translateX(0) !important;
     width: 280px;
  }
}
</style>
