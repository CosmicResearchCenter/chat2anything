<template>
  <div class="login-container">
    <!-- 科技感背景元素 -->
    <div class="tech-background">
      <div class="tech-line line-1"></div>
      <div class="tech-line line-2"></div>
      <div class="tech-circle circle-1"></div>
      <div class="tech-circle circle-2"></div>
      <div class="tech-grid"></div>
    </div>

    <div class="login-box">
      <!-- 品牌标识 -->
      <div class="brand-logo">
        <!-- <img src="assets/logo.png" alt="Logo" class="logo-image" onerror="this.style.display='none'"> -->
        <h1 class="brand-name">Chat2anything</h1>
      </div>

      <!-- 欢迎信息 -->
      <div class="welcome-text">
        <h2>{{ getWelcomeText() }}</h2>
        <p>欢迎使用我们的智能对话平台</p>
      </div>

      <div class="login-content">
        <!-- 简化的表单切换设计 - 只有登录和注册两个选项 -->
        <div class="form-tabs">
          <div 
            :class="['tab-item', { active: !isRegister }]" 
            @click="switchToLogin"
          >
            <i class="el-icon-user"></i>
            <span>登录</span>
          </div>
          <div 
            :class="['tab-item', { active: isRegister }]" 
            @click="switchToRegister"
          >
            <i class="el-icon-plus"></i>
            <span>注册</span>
          </div>
        </div>

        <div class="form-container" :class="currentFormClass">
          <!-- 登录表单 -->
          <div class="form-panel login-form" :class="{ active: !isRegister }">
            <div class="form-group animated">
              <el-input 
                v-model="username" 
                placeholder="用户名" 
                class="input-field"
                :prefix-icon="User"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="formErrors.username">{{ formErrors.username }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="password" 
                type="password" 
                placeholder="密码" 
                class="input-field"
                :prefix-icon="Lock"
                @keyup.enter="handleLogin"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="formErrors.password">{{ formErrors.password }}</div>
            </div>
            
            <div class="remember-me">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" class="forgot-password">忘记密码?</a>
            </div>
            
            <el-button 
              type="primary" 
              @click="handleLogin" 
              class="submit-button"
              :loading="loading"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </div>

          <!-- 注册表单 -->
          <div class="form-panel register-form" :class="{ active: isRegister && !isAdminRegister }">
            <div class="form-group animated">
              <el-input 
                v-model="registerForm.username" 
                placeholder="用户名" 
                class="input-field"
                :prefix-icon="User"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="registerFormErrors.username">{{ registerFormErrors.username }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="密码" 
                class="input-field"
                :prefix-icon="Lock"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="registerFormErrors.password">{{ registerFormErrors.password }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="确认密码" 
                class="input-field"
                :prefix-icon="Lock"
                @keyup.enter="register"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="registerFormErrors.confirmPassword">{{ registerFormErrors.confirmPassword }}</div>
            </div>
            <el-button 
              type="primary" 
              @click="register" 
              class="submit-button"
              :loading="loading"
            >
              {{ loading ? '注册中...' : '注 册' }}
            </el-button>
            
            <!-- 添加管理员注册切换链接 -->
            <div class="admin-register-toggle">
              <a href="#" @click.prevent="switchToAdminRegister">管理员注册</a>
            </div>
          </div>

          <!-- 管理员注册表单 -->
          <div class="form-panel admin-form" :class="{ active: isRegister && isAdminRegister }">
            <div class="form-group animated">
              <el-input 
                v-model="adminRegisterForm.username" 
                placeholder="管理员用户名" 
                class="input-field"
                :prefix-icon="User"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="adminFormErrors.username">{{ adminFormErrors.username }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="adminRegisterForm.password" 
                type="password" 
                placeholder="密码" 
                class="input-field"
                :prefix-icon="Lock"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="adminFormErrors.password">{{ adminFormErrors.password }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="adminRegisterForm.confirmPassword" 
                type="password" 
                placeholder="确认密码" 
                class="input-field"
                :prefix-icon="Lock"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="adminFormErrors.confirmPassword">{{ adminFormErrors.confirmPassword }}</div>
            </div>
            <div class="form-group animated">
              <el-input 
                v-model="adminRegisterForm.adminKey" 
                type="password" 
                placeholder="管理员密钥" 
                class="input-field"
                :prefix-icon="Key"
                @keyup.enter="registerAdmin"
                @focus="inputFocus"
                @blur="inputBlur"
              />
              <div class="form-error" v-if="adminFormErrors.adminKey">{{ adminFormErrors.adminKey }}</div>
            </div>
            <el-button 
              type="primary" 
              @click="registerAdmin" 
              class="submit-button"
              :loading="loading"
            >
              {{ loading ? '注册中...' : '管理员注册' }}
            </el-button>
            
            <!-- 添加返回普通注册的链接 -->
            <div class="admin-register-toggle">
              <a href="#" @click.prevent="switchToNormalRegister">返回普通注册</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock, Key } from '@element-plus/icons-vue'
import { login, signup, signupAdmin } from '@/utils/http';

const username = ref('');
const password = ref('');
const loading = ref(false);
const rememberMe = ref(false);
const router = useRouter();

const isRegister = ref(false);
const isAdminRegister = ref(false);

// 表单错误提示
const formErrors = reactive({
  username: '',
  password: ''
});

const registerFormErrors = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

const adminFormErrors = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  adminKey: ''
});

// 根据当前表单状态返回不同的CSS类
const currentFormClass = computed(() => {
  if (isRegister.value && isAdminRegister.value) return 'admin-active';
  if (isRegister.value) return 'register-active';
  return 'login-active';
});

// 根据当前表单状态返回不同的欢迎文本
const getWelcomeText = () => {
  if (isRegister.value && isAdminRegister.value) return '管理员注册';
  if (isRegister.value) return '创建您的账号';
  return '欢迎回来';
};

// 表单切换函数
const switchToLogin = () => {
  isRegister.value = false;
  isAdminRegister.value = false;
};

const switchToRegister = () => {
  isRegister.value = true;
  isAdminRegister.value = false;
};

const switchToAdminRegister = () => {
  isRegister.value = true;
  isAdminRegister.value = true;
};

const switchToNormalRegister = () => {
  isAdminRegister.value = false;
};

// 输入框焦点事件
const inputFocus = (e: Event) => {
  const target = e.target as HTMLElement;
  const parent = target.closest('.form-group') as HTMLElement;
  if (parent) parent.classList.add('focused');
};

const inputBlur = (e: Event) => {
  const target = e.target as HTMLElement;
  const parent = target.closest('.form-group') as HTMLElement;
  if (parent) parent.classList.remove('focused');
};

// 表单验证函数
const validateLoginForm = () => {
  let isValid = true;
  formErrors.username = '';
  formErrors.password = '';

  if (!username.value) {
    formErrors.username = '请输入用户名';
    isValid = false;
  }

  if (!password.value) {
    formErrors.password = '请输入密码';
    isValid = false;
  }

  return isValid;
};

const validateRegisterForm = () => {
  let isValid = true;
  registerFormErrors.username = '';
  registerFormErrors.password = '';
  registerFormErrors.confirmPassword = '';

  if (!registerForm.username) {
    registerFormErrors.username = '请输入用户名';
    isValid = false;
  } else if (registerForm.username.length < 3) {
    registerFormErrors.username = '用户名至少需要3个字符';
    isValid = false;
  }

  if (!registerForm.password) {
    registerFormErrors.password = '请输入密码';
    isValid = false;
  } else if (registerForm.password.length < 6) {
    registerFormErrors.password = '密码至少需要6个字符';
    isValid = false;
  }

  if (!registerForm.confirmPassword) {
    registerFormErrors.confirmPassword = '请确认密码';
    isValid = false;
  } else if (registerForm.password !== registerForm.confirmPassword) {
    registerFormErrors.confirmPassword = '两次输入的密码不一致';
    isValid = false;
  }

  return isValid;
};

const validateAdminForm = () => {
  let isValid = true;
  adminFormErrors.username = '';
  adminFormErrors.password = '';
  adminFormErrors.confirmPassword = '';
  adminFormErrors.adminKey = '';

  if (!adminRegisterForm.username) {
    adminFormErrors.username = '请输入用户名';
    isValid = false;
  }

  if (!adminRegisterForm.password) {
    adminFormErrors.password = '请输入密码';
    isValid = false;
  } else if (adminRegisterForm.password.length < 6) {
    adminFormErrors.password = '密码至少需要6个字符';
    isValid = false;
  }

  if (!adminRegisterForm.confirmPassword) {
    adminFormErrors.confirmPassword = '请确认密码';
    isValid = false;
  } else if (adminRegisterForm.password !== adminRegisterForm.confirmPassword) {
    adminFormErrors.confirmPassword = '两次输入的密码不一致';
    isValid = false;
  }

  if (!adminRegisterForm.adminKey) {
    adminFormErrors.adminKey = '请输入管理员密钥';
    isValid = false;
  }

  return isValid;
};

const handleLogin = async () => {
  if (!validateLoginForm()) return;
  
  loading.value = true;
  try {
    await login(username.value, password.value);
    // 如果勾选了记住我，保存用户名
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', username.value);
    } else {
      localStorage.removeItem('rememberedUsername');
    }
    
    ElMessage({
      message: '登录成功',
      type: 'success',
      duration: 2000
    });
    router.push('/');
  } catch (error: any) {
    ElMessage({
      message: error.message || '登录失败',
      type: 'error'
    });
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
  if (!validateRegisterForm()) return;

  loading.value = true;
  try {
    await signup(registerForm.username, registerForm.password);
    ElMessage({
      message: '注册成功',
      type: 'success'
    });
    switchToLogin(); // 切换到登录界面
    username.value = registerForm.username; // 自动填充用户名
    registerForm.password = '';
    registerForm.confirmPassword = '';
  } catch (error: any) {
    ElMessage({
      message: error.message || '注册失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
};

const adminRegisterForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  adminKey: ''
});

const registerAdmin = async () => {
  if (!validateAdminForm()) return;

  loading.value = true;
  try {
    await signupAdmin(
      adminRegisterForm.username, 
      adminRegisterForm.password, 
      adminRegisterForm.adminKey
    );
    ElMessage({
      message: '管理员注册成功',
      type: 'success'
    });
    switchToLogin(); // 切换到登录界面
    username.value = adminRegisterForm.username; // 自动填充用户名
    adminRegisterForm.password = '';
    adminRegisterForm.confirmPassword = '';
    adminRegisterForm.adminKey = '';
  } catch (error: any) {
    ElMessage({
      message: error.message || '管理员注册失败',
      type: 'error'
    });
  } finally {
    loading.value = false;
  }
};

// 初始化和恢复记住的用户名
onMounted(() => {
  // 如果有保存的用户名，恢复
  const savedUsername = localStorage.getItem('rememberedUsername');
  if (savedUsername) {
    username.value = savedUsername;
    rememberMe.value = true;
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a2a3a 0%, #2d3a4a 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 科技感背景元素 */
.tech-background {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.tech-line {
  position: absolute;
  background: linear-gradient(90deg, rgba(52, 152, 219, 0.05), rgba(52, 152, 219, 0.2));
  height: 2px;
  width: 100%;
  transform-origin: left;
}

.line-1 {
  top: 25%;
  animation: techLineMove 15s infinite linear;
}

.line-2 {
  bottom: 30%;
  animation: techLineMove 20s infinite linear;
}

.tech-circle {
  position: absolute;
  border: 1px solid rgba(52, 152, 219, 0.1);
  border-radius: 50%;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  border-width: 2px;
  animation: pulse 10s infinite alternate;
}

.circle-2 {
  width: 500px;
  height: 500px;
  bottom: -250px;
  left: -250px;
  border-width: 3px;
  animation: pulse 15s infinite alternate-reverse;
}

.tech-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(52, 152, 219, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(52, 152, 219, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridMove 60s infinite linear;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.2; }
  50% { transform: scale(1.05); opacity: 0.3; }
  100% { transform: scale(1); opacity: 0.2; }
}

@keyframes techLineMove {
  0% { transform: translateX(-100%) scaleX(1); }
  50% { transform: translateX(0%) scaleX(1.5); }
  100% { transform: translateX(100%) scaleX(1); }
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 50px 50px; }
}

.login-box {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  z-index: 1;
  animation: fadeIn 0.6s ease-out;
  transform: translateY(0);
  transition: all 0.3s ease;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.login-box:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  transform: translateY(-5px);
}

.brand-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  text-align: center;
}

.logo-image {
  width: 70px;
  height: 70px;
  margin-bottom: 10px;
}

.brand-name {
  font-size: 24px;
  color: #333;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(90deg, #3498db, #2c5364);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-text {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-text h2 {
  font-size: 22px;
  color: #2c3e50;
  margin: 0;
  margin-bottom: 8px;
}

.welcome-text p {
  color: #7f8c8d;
  margin: 0;
}

.login-content {
  display: flex;
  flex-direction: column;
}

.form-tabs {
  display: flex;
  background: #f5f8fa;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 30px;
}

.tab-item {
  flex: 1;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #7f8c8d;
  font-weight: 500;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.tab-item i {
  margin-bottom: 5px;
  font-size: 18px;
}

.tab-item.active {
  color: #3498db;
  background: #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.tab-item.active:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #3498db, #2980b9);
}

.form-container {
  position: relative;
  min-height: 250px;
  overflow: hidden;
}

.form-panel {
  position: absolute;
  width: 100%;
  opacity: 0;
  visibility: hidden;
  transform: translateX(30px);
  transition: all 0.5s cubic-bezier(0.445, 0.05, 0.55, 0.95);
}

.form-panel.active {
  opacity: 1;
  visibility: visible;
  transform: translateX(0);
}

.form-group {
  position: relative;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.form-group.animated {
  transform: translateY(0);
  transition: transform 0.3s ease, opacity 0.3s ease;
  opacity: 1;
}

.form-group.focused {
  transform: translateY(-5px);
}

.input-field {
  --el-input-bg-color: #fff !important;
  --el-input-border-color: #e0e6ed !important;
  --el-input-hover-border-color: #3498db !important;
  --el-input-focus-border-color: #3498db !important;
}

.input-field :deep(.el-input__wrapper) {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
  border-radius: 8px;
  padding: 10px 15px;
  transition: all 0.3s ease;
}

.input-field :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.2) !important;
}

.input-field :deep(.el-input__inner) {
  color: #333;
  height: 24px;
  font-size: 14px;
}

.input-field :deep(.el-input__inner::placeholder) {
  color: #95a5a6;
}

.submit-button {
  height: 48px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  border: none;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 500;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.remember-me {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  margin-top: -5px;
}

.forgot-password {
  color: #3498db;
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s ease;
}

.forgot-password:hover {
  color: #2980b9;
  text-decoration: underline;
}

.form-error {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
  display: block;
  animation: fadeIn 0.3s ease;
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
    margin-top: -100px;
  }
  
  .welcome-text h2 {
    font-size: 20px;
  }
  
  .welcome-text p {
    font-size: 14px;
  }
  
  .submit-button {
    height: 44px;
  }
}

@media (max-width: 480px) {
  .login-box {
    width: 95%;
    padding: 1.5rem;
  }
  
  .form-tabs {
    margin-bottom: 20px;
  }
  
  .tab-item {
    padding: 8px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }

  .input-field :deep(.el-input__wrapper) {
    padding: 8px 12px;
  }

  .submit-button {
    height: 40px;
    font-size: 14px;
  }
}

/* 为各个表单状态定义不同的容器高度 */
.form-container.login-active {
  min-height: 210px;
}

.form-container.register-active {
  min-height: 290px; /* 增加一点高度以适应新增的管理员链接 */
}

.form-container.admin-active {
  min-height: 360px; /* 增加一点高度以适应返回普通注册链接 */
}

/* 添加管理员注册切换链接样式 */
.admin-register-toggle {
  text-align: right;
  margin-top: 15px;
  font-size: 13px;
}

.admin-register-toggle a {
  color: #3498db;
  text-decoration: none;
  transition: all 0.2s ease;
}

.admin-register-toggle a:hover {
  color: #2980b9;
  text-decoration: underline;
}
</style>

<script lang="ts">
// 为TypeScript增加全局类型声明
declare global {
  interface Window {
    particlesJS: any;
  }
}
</script>
