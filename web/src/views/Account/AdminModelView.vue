<template>
  <div class="model-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon><Setting /></el-icon>
        <h2>模型配置管理</h2>
      </div>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/admin' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>模型配置</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- LLM和Embedding切换标签 -->
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="LLM 模型配置" name="llm">
        <div class="tab-header">
          <div class="tab-title">LLM模型配置列表</div>
          <el-button type="primary" @click="openCreateDialog('llm')">添加LLM配置</el-button>
        </div>
        
        <!-- LLM配置列表 -->
        <el-table :data="llmConfigs" stripe border v-loading="loading.llm">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="vendor_type" label="供应商类型" width="120" />
          <el-table-column prop="model" label="模型名称" min-width="160" />
          <el-table-column prop="base_url" label="基础URL" min-width="200" />
          <el-table-column prop="api_key_masked" label="API密钥" width="150" />
          <el-table-column label="默认配置" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_default ? 'success' : 'info'">
                {{ scope.row.is_default ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250">
            <template #default="scope">
              <el-button type="primary" link @click="editConfig('llm', scope.row)">编辑</el-button>
              <el-button type="success" link @click="setAsDefault('llm', scope.row.id)" :disabled="scope.row.is_default">
                设为默认
              </el-button>
              <el-button type="danger" link @click="confirmDelete('llm', scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="Embedding 模型配置" name="embedding">
        <div class="tab-header">
          <div class="tab-title">Embedding模型配置列表</div>
          <el-button type="primary" @click="openCreateDialog('embedding')">添加Embedding配置</el-button>
        </div>
        
        <!-- Embedding配置列表 -->
        <el-table :data="embeddingConfigs" stripe border v-loading="loading.embedding">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="vendor_type" label="供应商类型" width="120" />
          <el-table-column prop="model" label="模型名称" min-width="160" />
          <el-table-column prop="base_url" label="基础URL" min-width="200" />
          <el-table-column prop="api_key_masked" label="API密钥" width="150" />
          <el-table-column label="默认配置" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_default ? 'success' : 'info'">
                {{ scope.row.is_default ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250">
            <template #default="scope">
              <el-button type="primary" link @click="editConfig('embedding', scope.row)">编辑</el-button>
              <el-button type="success" link @click="setAsDefault('embedding', scope.row.id)" :disabled="scope.row.is_default">
                设为默认
              </el-button>
              <el-button type="danger" link @click="confirmDelete('embedding', scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? `添加${configType === 'llm' ? 'LLM' : 'Embedding'}配置` : `编辑${configType === 'llm' ? 'LLM' : 'Embedding'}配置`"
      width="50%"
    >
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="120px">
        <el-form-item label="供应商类型" prop="vendor_type">
          <el-select v-model="configForm.vendor_type" placeholder="请选择供应商类型">
            <el-option 
              v-for="vendor in availableVendors[configType]"
              :key="vendor"
              :label="vendor"
              :value="vendor"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model">
          <el-input v-model="configForm.model" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="configForm.base_url" placeholder="请输入基础URL" />
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="configForm.api_key" placeholder="请输入API密钥" show-password />
          <div v-if="dialogType === 'edit'" class="api-key-hint">留空表示不修改API密钥</div>
        </el-form-item>
        <el-form-item label="配置信息" prop="configStr">
          <el-input
            v-model="configForm.configStr"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的配置信息"
          />
        </el-form-item>
        <!-- LLM 特有设置 -->
        <template v-if="configType === 'llm'">
          <el-form-item label="设为默认的对话" prop="is_default_chat">
            <el-switch v-model="configForm.is_default_chat" />
          </el-form-item>
          <el-form-item label="设为默认的拆分模型" prop="is_default_splitter">
            <el-switch v-model="configForm.is_default_splitter" />
          </el-form-item>
        </template>
        <!-- Embedding 特有设置 -->
        <template v-if="configType === 'embedding'">
          <el-form-item label="设为默认" prop="is_default">
            <el-switch v-model="configForm.is_default" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading.submit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="30%"
    >
      <div>确定要删除此配置吗？此操作不可恢复。</div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteConfig" :loading="loading.delete">确定删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Setting } from '@element-plus/icons-vue';
import { getRequest, postRequest, putRequest, deleteRequest } from '@/utils/http';

// 数据部分
const activeTab = ref('llm');
const llmConfigs = ref<any[]>([]);
const embeddingConfigs = ref<any[]>([]);
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const configType = ref<'llm' | 'embedding'>('llm');
const deleteDialogVisible = ref(false);
const currentConfig = ref<any>(null);

// 表单数据
const configForm = reactive({
  id: 0,
  vendor_type: '',
  model: '',
  base_url: '',
  api_key: '',
  config: {},
  configStr: '',  // JSON字符串版的config
  is_default_chat: false,
  is_default_splitter: false,
  is_default: false
});

// 表单引用
const configFormRef = ref();

// 表单验证规则
const configRules = {
  vendor_type: [{ required: true, message: '请选择供应商类型', trigger: 'change' }],
  model: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  base_url: [{ required: false, message: '请输入基础URL', trigger: 'blur' }],
  api_key: [
    { required: false, message: '请输入API密钥', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (dialogType.value === 'create' && !value) {
          callback(new Error('创建时API密钥必填'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ],
  configStr: [
    { required: false },
    { validator: (rule, value, callback) => {
        if (value && value.trim()) {
          try {
            JSON.parse(value);
            callback();
          } catch (e) {
            callback(new Error('配置信息必须是有效的JSON格式'));
          }
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 加载状态
const loading = reactive({
  llm: false,
  embedding: false,
  submit: false,
  delete: false
});

// 可用的供应商类型
const availableVendors = {
  llm: ['OPENAI', 'DOUBAO', 'ZHIPUAI', 'SPARKAI', 'ONEAPI', 'SILICONFLOW', 'SILICONFLOW'],
  embedding: ['OPENAI', 'ONEAPI', 'ZHIPUAI', 'DOUBAO', 'SILICONFLOW']
};

// 处理标签页切换
const handleTabClick = () => {
  // 可以在这里添加标签切换时的逻辑
};

// 格式化日期显示
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleString();
  } catch (e) {
    return dateString;
  }
};

// 获取LLM配置列表
const fetchLlmConfigs = async () => {
  loading.llm = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/llm_configs`);
    if (response?.code === 200) {
      llmConfigs.value = response.data || [];
    } else {
      ElMessage.error(response?.message || '获取LLM配置列表失败');
    }
  } catch (error) {
    console.error('获取LLM配置列表出错:', error);
    ElMessage.error('获取LLM配置列表出错');
  } finally {
    loading.llm = false;
  }
};

// 获取Embedding配置列表
const fetchEmbeddingConfigs = async () => {
  loading.embedding = true;
  try {
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const response = await getRequest<any>(`${baseURL}/v1/api/mark/admin/embedding_configs`);
    if (response?.code === 200) {
      embeddingConfigs.value = response.data || [];
    } else {
      ElMessage.error(response?.message || '获取Embedding配置列表失败');
    }
  } catch (error) {
    console.error('获取Embedding配置列表出错:', error);
    ElMessage.error('获取Embedding配置列表出错');
  } finally {
    loading.embedding = false;
  }
};

// 打开创建对话框
const openCreateDialog = (type: 'llm' | 'embedding') => {
  configType.value = type;
  dialogType.value = 'create';
  resetForm();
  dialogVisible.value = true;
};

// 打开编辑对话框
const editConfig = (type: 'llm' | 'embedding', config: any) => {
  configType.value = type;
  dialogType.value = 'edit';
  resetForm();
  
  // 填充表单数据
  configForm.id = config.id;
  configForm.vendor_type = config.vendor_type;
  configForm.model = config.model;
  configForm.base_url = config.base_url;
  configForm.api_key = ''; // 不填充API密钥，需要用户重新输入
  
  // 根据配置类型填充特定字段
  if (type === 'llm') {
    configForm.is_default_chat = config.is_default_chat || false;
    configForm.is_default_splitter = config.is_default_splitter || false;
  } else {
    configForm.is_default = config.is_default || false;
  }
  
  // 处理配置信息
  if (config.config) {
    configForm.config = config.config;
    configForm.configStr = JSON.stringify(config.config, null, 2);
  } else {
    configForm.config = {};
    configForm.configStr = '';
  }
  
  dialogVisible.value = true;
};

// 重置表单
const resetForm = () => {
  configForm.id = 0;
  configForm.vendor_type = '';
  configForm.model = '';
  configForm.base_url = '';
  configForm.api_key = '';
  configForm.config = {};
  configForm.configStr = '';
  
  // 根据配置类型重置特定字段
  if (configType.value === 'llm') {
    configForm.is_default_chat = false;
    configForm.is_default_splitter = false;
  } else {
    configForm.is_default = false;
  }
  
  // 重置表单验证状态
  if (configFormRef.value) {
    configFormRef.value.resetFields();
  }
};

// 提交表单
const submitForm = async () => {
  if (!configFormRef.value) return;
  
  try {
    await configFormRef.value.validate();
    
    // 解析JSON字符串为对象
    try {
      if (configForm.configStr.trim()) {
        configForm.config = JSON.parse(configForm.configStr);
      } else {
        configForm.config = {};
      }
    } catch (e) {
      ElMessage.error('配置信息JSON格式无效');
      return;
    }
    
    loading.submit = true;
    const baseURL = import.meta.env.VITE_APP_BASE_URL;
    const url = configType.value === 'llm' ? '/v1/api/mark/admin/llm_configs' : '/v1/api/mark/admin/embedding_configs';
    const fullUrl = dialogType.value === 'create' ? 
      `${baseURL}${url}` : 
      `${baseURL}${url}/${configForm.id}`;
    
    // 根据配置类型准备请求数据
    const requestData: any = {
      vendor_type: configForm.vendor_type,
      model: configForm.model,
      base_url: configForm.base_url,
      config: configForm.config
    };
    
    // 仅当API密钥有值时才添加到请求中
    if (configForm.api_key) {
      requestData.api_key = configForm.api_key;
    }
    
    // 根据配置类型添加特定字段
    if (configType.value === 'llm') {
      requestData.is_default_chat = configForm.is_default_chat;
      requestData.is_default_splitter = configForm.is_default_splitter;
    } else {
      requestData.is_default = configForm.is_default;
    }
    
    let response;
    if (dialogType.value === 'create') {
      response = await postRequest<any>(fullUrl, requestData);
    } else {
      response = await putRequest<any>(fullUrl, requestData);
    }
    
    if (response?.code === 200) {
      ElMessage.success(dialogType.value === 'create' ? '添加成功' : '更新成功');
      dialogVisible.value = false;
      
      // 刷新数据
      if (configType.value === 'llm') {
        fetchLlmConfigs();
      } else {
        fetchEmbeddingConfigs();
      }
    } else {
      ElMessage.error(response?.message || (dialogType.value === 'create' ? '添加失败' : '更新失败'));
    }
  } catch (error: any) {
    console.error(dialogType.value === 'create' ? '添加配置出错:' : '更新配置出错:', error);
    if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error(dialogType.value === 'create' ? '添加配置出错' : '更新配置出错');
    }
  } finally {
    loading.submit = false;
  }
};

// 确认删除
const confirmDelete = (type: 'llm' | 'embedding', config: any) => {
  configType.value = type;
  currentConfig.value = config;
  deleteDialogVisible.value = true;
};

// 删除配置
const deleteConfig = async () => {
  if (!currentConfig.value) return;
  
  loading.delete = true;
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const url = configType.value === 'llm' ? 
    `/v1/api/mark/admin/llm_configs/${currentConfig.value.id}` : 
    `/v1/api/mark/admin/embedding_configs/${currentConfig.value.id}`;
  
  try {
    const response = await deleteRequest<any>(`${baseURL}${url}`);
    if (response?.code === 200) {
      ElMessage.success('删除成功');
      deleteDialogVisible.value = false;
      
      // 刷新数据
      if (configType.value === 'llm') {
        fetchLlmConfigs();
      } else {
        fetchEmbeddingConfigs();
      }
    } else {
      ElMessage.error(response?.message || '删除失败');
    }
  } catch (error) {
    console.error('删除配置出错:', error);
    ElMessage.error('删除配置出错');
  } finally {
    loading.delete = false;
  }
};

// 设置为默认配置
const setAsDefault = async (type: 'llm' | 'embedding', id: number) => {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const url = type === 'llm' ? 
    `/v1/api/mark/admin/llm_configs/${id}/set_default` : 
    `/v1/api/mark/admin/embedding_configs/${id}/set_default`;
  
  try {
    const response = await postRequest<any>(`${baseURL}${url}`, {});
    if (response?.code === 200) {
      ElMessage.success('设置默认配置成功');
      
      // 刷新数据
      if (type === 'llm') {
        fetchLlmConfigs();
      } else {
        fetchEmbeddingConfigs();
      }
    } else {
      ElMessage.error(response?.message || '设置默认配置失败');
    }
  } catch (error) {
    console.error('设置默认配置出错:', error);
    ElMessage.error('设置默认配置出错');
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchLlmConfigs();
  fetchEmbeddingConfigs();
});
</script>

<style scoped>
.model-container {
  padding: 24px;
  min-height: calc(100vh - 48px);
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title h2 {
  font-size: 24px;
  font-weight: 500;
  margin: 0;
  color: #1a1a1a;
}

.page-title .el-icon {
  font-size: 24px;
  color: #409eff;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tab-title {
  font-size: 18px;
  font-weight: 500;
}

.api-key-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .model-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .tab-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
