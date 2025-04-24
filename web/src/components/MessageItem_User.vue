<template>
  <div class="msg-box">
    <v-md-preview :text="message" class="msg_user"></v-md-preview>
    <div class="avatar-box">
      <el-avatar class="avatar" shape="circle" size="100" fit="fit" :src="avatar_url" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
export default defineComponent({
    name: 'MessageItem_User',
    props: {
        message: {
            type: String as PropType<string>,
            required: true,
        },
        avatar_url: {
            type: String as PropType<string>,
            required: false
        }
    },
});
</script>

<style>
.msg-box {
  display: flex;
  gap: 16px;
  margin: 24px 0;
  justify-content: flex-end;
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

.msg_user {
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 4px 18px 18px;
  padding: 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 4px 24px -1px rgba(3, 105, 225, 0.2),
    0 2px 8px -1px rgba(3, 105, 225, 0.1);
  max-width: 80%;
  position: relative;
  transition: all 0.3s ease;
}

.msg_user:hover {
  box-shadow: 
    0 6px 30px -1px rgba(3, 105, 225, 0.25),
    0 3px 10px -1px rgba(3, 105, 225, 0.15);
  transform: translateY(-2px);
}

.msg_user::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 20px;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #0245a3 0%, #0369e1 100%);
  transform: rotate(45deg);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.msg_user :deep(*) {
  color: #ffffff !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.msg_user :deep(code) {
  background-color: rgba(255, 255, 255, 0.15) !important;
  border-radius: 6px;
  padding: 2px 6px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.msg_user :deep(pre) {
  background-color: rgba(0, 0, 0, 0.2) !important;
  border-radius: 12px;
  padding: 12px 16px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin: 10px 0;
  overflow-x: auto;
}

.msg_user :deep(pre code) {
  background-color: transparent !important;
  border: none;
  padding: 0;
}

.msg_user :deep(p) {
  margin: 0;
  line-height: 1.6;
}

.msg_user :deep(h1),
.msg_user :deep(h2),
.msg_user :deep(h3),
.msg_user :deep(h4),
.msg_user :deep(h5),
.msg_user :deep(h6) {
  margin-top: 16px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.msg_user :deep(a) {
  color: #ffffff !important;
  text-decoration: underline;
  text-decoration-color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.msg_user :deep(a:hover) {
  text-decoration-color: rgba(255, 255, 255, 1);
}
</style>