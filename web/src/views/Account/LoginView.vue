<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-content">
        <div class="form-switch">
          <span 
            :class="{ active: !isRegister }" 
            @click="isRegister = false"
          >登录</span>
          <span 
            :class="{ active: isRegister }" 
            @click="isRegister = true"
          >注册</span>
        </div>

        <template v-if="!isRegister">
          <div class="form-group">
            <el-input 
              v-model="username" 
              placeholder="用户名" 
              class="input-field"
              :prefix-icon="User"
            />
          </div>
          <div class="form-group">
            <el-input 
              v-model="password" 
              type="password" 
              placeholder="密码" 
              class="input-field"
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
            />
          </div>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            class="login-button"
            :loading="loading"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </template>

        <template v-else>
          <div class="form-group">
            <el-input 
              v-model="registerForm.username" 
              placeholder="用户名" 
              class="input-field"
              :prefix-icon="User"
            />
          </div>
          <div class="form-group">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="密码" 
              class="input-field"
              :prefix-icon="Lock"
            />
          </div>
          <div class="form-group">
            <el-input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="确认密码" 
              class="input-field"
              :prefix-icon="Lock"
              @keyup.enter="register"
            />
          </div>
          <el-button 
            type="primary" 
            @click="register" 
            class="login-button"
            :loading="loading"
          >
            {{ loading ? '注册中...' : '注 册' }}
          </el-button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue'
import { login, signup } from '@/utils/http';

const username = ref('');
const password = ref('');
const loading = ref(false);
const router = useRouter();

const isRegister = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码');
    return;
  }
  
  loading.value = true;
  try {
    await login(username.value, password.value);
    ElMessage.success({
      message: '登录成功',
      duration: 2000
    });
    router.push('/');
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败');
  } finally {
    loading.value = false;
  }
};

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

const register = async () => {
  if (!registerForm.username || !registerForm.password || !registerForm.confirmPassword) {
    ElMessage.warning('请填写完整注册信息');
    return;
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致');
    return;
  }

  loading.value = true;
  try {
    await signup(registerForm.username, registerForm.password);
    ElMessage.success('注册成功');
    isRegister.value = false; // 切换到登录界面
    username.value = registerForm.username; // 自动填充用户名
    registerForm.password = '';
    registerForm.confirmPassword = '';
  } catch (error: any) {
    ElMessage.error(error.message || '注册失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  /* background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%); */
  position: relative;
  overflow: hidden;
}

.login-box {
  position: relative;
  margin-top: -200px;
  width: 100%;
  max-width: 400px;
  background: rgb(255, 255, 255);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1;
  animation: fadeIn 0.5s ease-out;
}

.login-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

h2 {
  color: #fff;
  font-size: 1.8rem;
  margin: 0 0 1rem;
  text-align: center;
  letter-spacing: 2px;
}

.form-group {
  position: relative;
}

.input-field {
  --el-input-bg-color: rgb(255, 255, 255) !important;
  --el-input-border-color: rgba(0, 0, 0, 0.1) !important;
  --el-input-hover-border-color: rgba(0, 0, 0, 0.2) !important;
}

.input-field :deep(.el-input__wrapper) {
  background-color: rgb(255, 255, 255);
  box-shadow: none;
  border-radius: 12px;
  padding: 8px 15px;
}

.input-field :deep(.el-input__inner) {
  color: #333;
}

.input-field :deep(.el-input__inner::placeholder) {
  color: #999;
}

.login-button {
  height: 48px;
  font-size: 1.1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #00c6fb 0%, #005bea 100%);
  border: none;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 198, 251, 0.4);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    width: 85%;
    padding: 2rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  .login-button {
    height: 44px;
  }
}

@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }

  .login-box {
    padding: 1rem;
  }

  .input-field :deep(.el-input__wrapper) {
    padding: 6px 10px;
  }

  .login-button {
    height: 40px;
  }
}

.form-switch {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1rem;
}

.form-switch span {
  color: rgb(0, 0, 0);
  cursor: pointer;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
}

.form-switch span.active {
  color: #409EFF;
  font-weight: bold;
  border-bottom: 2px solid #409EFF;
}
</style>
