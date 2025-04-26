<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ChatDotRound, Folder, Setting, User } from '@element-plus/icons-vue'
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

// 管理员状态响应式变量
const isAdmin = ref(false)
const route = useRoute()

// 检查用户是否为管理员
async function checkIsAdmin() {
  const token = localStorage.getItem('token')
  if (!token) {
    isAdmin.value = false
    return
  }
  
  const baseURL = import.meta.env.VITE_APP_BASE_URL
  try {
    const response = await fetch(`${baseURL}/v1/api/mark/admin/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    isAdmin.value = response.ok
  } catch (error) {
    console.error('Error checking admin status:', error)
    isAdmin.value = false
  }
}

// 组件挂载时检查管理员状态
onMounted(async () => {
  await checkIsAdmin()
})

// 监听路由变化，重新检查管理员状态
watch(
  () => route.path,
  async () => {
    await checkIsAdmin()
  }
)
</script>

<template>
  <div class="container">
    
    <nav class="glass-nav">
      <!-- <h1>Chat2Anything</h1> -->
      <ul>
        <li>
          <RouterLink to="/">
            <el-icon><ChatDotRound /></el-icon>
            智能问答
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/manager">
            <el-icon><Folder /></el-icon>
            知识库
          </RouterLink>
        </li>
        <!-- <li>
          <RouterLink to="/settings">
            <el-icon><Setting /></el-icon>
            设置
          </RouterLink>
        </li> -->
        <li v-if="isAdmin">
          <RouterLink to="/admin">
            <el-icon><User /></el-icon>
            后台管理
          </RouterLink>
        </li>
      </ul>
    </nav>
    <!-- Remove padding from main if child components handle it -->
    <main> 
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  height: 100vh;
  width: 100vw;
  /* background: linear-gradient(135deg, #f0f7fa 0%, #e0f0f8 100%); */ /* Moved background to specific views or keep global */
  background-color: #f7f8fa; /* Use a consistent light background */
  position: fixed;
  top: 0;
  left: 0;
}

nav {
  width: 100%;
  height: 60px; /* Ensure consistent height */
  display: flex;
  /* padding: 1rem; */
  /* position: fixed; */
  /* top: 0; */
  /* left: 0; */
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.glass-nav {
  
  background: rgba(2, 69, 163, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.18);
  transition: all 0.3s ease;
}

ul {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  justify-content: center;
  width: 100%;
}

li {
  margin: 0 1.5rem;
}

li a {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.85);
  padding: 0.6rem 1.2rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

li a::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(100%);
  transition: transform 0.3s ease;
  z-index: -1;
  border-radius: 12px;
}

li a:hover {
  color: #ffffff;
  transform: translateY(-2px);
}

li a:hover::before {
  transform: translateY(0);
}

li a.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.el-icon {
  margin-right: 8px;
  transition: transform 0.3s ease;
}

li a:hover .el-icon {
  transform: scale(1.1);
}

main {
  flex: 1;
  overflow: hidden; /* Let child components handle scrolling */
  /* Remove padding: padding: 1rem; */ 
  /* Remove margin-top: margin-top: 4rem; */
  /* background: linear-gradient(135deg, #f0f7fa 0%, #e0f0f8 100%); */ /* Remove background if child handles it */
  /* box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05); */ /* Remove inset shadow */
  /* Remove scrollbar styles if child handles scrolling */
  /* scrollbar-width: thin; */
  /* scrollbar-color: rgba(0, 0, 0, 0.2) rgba(0, 0, 0, 0.1); */
}

/* main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
}

main::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
} */

/* 在小屏幕下，调整导航栏的布局 */
@media screen and (max-width: 768px) {
  nav ul {
    flex-direction: column;
    align-items: center;
  }

  nav li {
    margin: 10px 0;
    width: 80%;
  }

  li a {
    justify-content: center;
  }

  main {
    /* Remove margin-top: margin-top: 5rem; */
    /* Remove padding: padding: 1rem 0.5rem; */
  }
}
</style>
