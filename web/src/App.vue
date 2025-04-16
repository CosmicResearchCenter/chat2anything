<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ChatDotRound, Folder, Setting, User } from '@element-plus/icons-vue'
</script>

<template>
  <div class="container">
    <nav>
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
        <li>
          <RouterLink to="/admin">
            <el-icon><User /></el-icon>
            后台管理
          </RouterLink>
        </li>
      </ul>
    </nav>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  overflow-y: hidden;
  height: 100vh;
  width: 100vw;
  background: #f2fcfc;
  /* color: #000000; */
  position: fixed;
  top: 0;
  left: 0;
}

nav {
  width: 100%;
  background: #0245a3;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #3a3a4f;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
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
  color: #cfd8dc;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

li a:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

li a.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: 500;
}

.el-icon {
  margin-right: 4px;
}

main {
  flex: 1;
  overflow: hidden; 
  padding: 1rem;
  background: #f2fcfc;
  border-top: 1px solid #3a3a4f;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 4rem; /* 确保内容不被固定导航栏遮挡 */
}

/* 在小屏幕下，调整导航栏的布局 */
@media screen and (max-width: 768px) {
  nav ul {
    flex-direction: column;
    align-items: center;
  }

  nav li {
    margin: 10px 0;
  }

  main {
    margin-top: 5rem;
    padding: 1rem 0.5rem;
  }
}
</style>
