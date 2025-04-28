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

    <!-- 主内容卡片 -->
    <el-card class="main-card">
      <!-- LLM和Embedding切换标签 -->
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="config-tabs">
        <el-tab-pane label="LLM 模型配置" name="llm">
          <div class="tab-header">
            <div class="left-section">
              <div class="tab-title">LLM模型配置列表</div>
              <el-input
                v-model="llmSearchText"
                placeholder="搜索模型名称或供应商"
                class="search-input"
                clearable
                prefix-icon="Search"
              />
            </div>
            <el-button type="primary" @click="openCreateDialog('llm')">
              <el-icon><Plus /></el-icon>添加LLM配置
            </el-button>
          </div>
          
          <!-- LLM配置列表 -->
          <el-table 
            :data="filteredLlmConfigs" 
            stripe 
            v-loading="loading.llm"
            empty-text="暂无LLM模型配置数据"
            class="config-table"
          >
            <el-table-column prop="id" label="ID" width="60" align="center" />
            <el-table-column prop="vendor_type" label="供应商" width="120">
              <template #default="scope">
                <el-tag size="small" :type="getVendorTagType(scope.row.vendor_type)">
                  {{ scope.row.vendor_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="model" label="模型名称" min-width="140" show-overflow-tooltip />
            <el-table-column prop="base_url" label="基础URL" min-width="180" show-overflow-tooltip />
            <el-table-column prop="api_key_masked" label="API密钥" width="120" show-overflow-tooltip />
            <el-table-column label="对话默认" width="90" align="center">
              <template #default="scope">
                <el-switch 
                  :model-value="scope.row.is_default_chat" 
                  disabled 
                  active-color="#13ce66" 
                  inactive-color="#dcdfe6"
                />
              </template>
            </el-table-column>
            <el-table-column label="拆分默认" width="90" align="center">
              <template #default="scope">
                <el-switch 
                  :model-value="scope.row.is_default_splitter" 
                  disabled 
                  active-color="#13ce66" 
                  inactive-color="#dcdfe6"
                />
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="150" show-overflow-tooltip>
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-tooltip content="编辑配置" placement="top" :hide-after="1500">
                  <el-button type="primary" link @click="editConfig('llm', scope.row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="设为默认对话模型" placement="top" :hide-after="1500">
                  <el-button 
                    type="success" 
                    link 
                    @click="confirmSetDefault('llm', scope.row.id, 'chat')" 
                    :disabled="scope.row.is_default_chat"
                  >
                    <el-icon><ChatDotRound /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="设为默认拆分模型" placement="top" :hide-after="1500">
                  <el-button 
                    type="warning" 
                    link 
                    @click="confirmSetDefault('llm', scope.row.id, 'splitter')" 
                    :disabled="scope.row.is_default_splitter"
                  >
                    <el-icon><Grid /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除配置" placement="top" :hide-after="1500">
                  <el-button type="danger" link @click="confirmDelete('llm', scope.row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-placeholder" v-if="filteredLlmConfigs.length === 0 && !loading.llm">
            <el-empty description="暂无LLM模型配置数据" />
            <el-button type="primary" @click="openCreateDialog('llm')">添加第一个配置</el-button>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Embedding 模型配置" name="embedding">
          <div class="tab-header">
            <div class="left-section">
              <div class="tab-title">Embedding模型配置列表</div>
              <el-input
                v-model="embeddingSearchText"
                placeholder="搜索模型名称或供应商"
                class="search-input"
                clearable
                prefix-icon="Search"
              />
            </div>
            <el-button type="primary" @click="openCreateDialog('embedding')">
              <el-icon><Plus /></el-icon>添加Embedding配置
            </el-button>
          </div>
          
          <!-- Embedding配置列表 -->
          <el-table 
            :data="filteredEmbeddingConfigs" 
            stripe 
            v-loading="loading.embedding"
            empty-text="暂无Embedding模型配置数据"
            class="config-table"
          >
            <el-table-column prop="id" label="ID" width="60" align="center" />
            <el-table-column prop="vendor_type" label="供应商" width="120">
              <template #default="scope">
                <el-tag size="small" :type="getVendorTagType(scope.row.vendor_type)">
                  {{ scope.row.vendor_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="model" label="模型名称" min-width="140" show-overflow-tooltip />
            <el-table-column prop="base_url" label="基础URL" min-width="180" show-overflow-tooltip />
            <el-table-column prop="api_key_masked" label="API密钥" width="120" show-overflow-tooltip />
            <el-table-column label="默认配置" width="90" align="center">
              <template #default="scope">
                <el-switch 
                  :model-value="scope.row.is_default" 
                  disabled 
                  active-color="#13ce66" 
                  inactive-color="#dcdfe6"
                />
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="150" show-overflow-tooltip>
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="scope">
                <el-tooltip content="编辑配置" placement="top" :hide-after="1500">
                  <el-button type="primary" link @click="editConfig('embedding', scope.row)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="设为默认" placement="top" :hide-after="1500">
                  <el-button 
                    type="success" 
                    link 
                    @click="confirmSetDefault('embedding', scope.row.id)" 
                    :disabled="scope.row.is_default"
                  >
                    <el-icon><Check /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除配置" placement="top" :hide-after="1500">
                  <el-button type="danger" link @click="confirmDelete('embedding', scope.row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-placeholder" v-if="filteredEmbeddingConfigs.length === 0 && !loading.embedding">
            <el-empty description="暂无Embedding模型配置数据" />
            <el-button type="primary" @click="openCreateDialog('embedding')">添加第一个配置</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? `添加${configType === 'llm' ? 'LLM' : 'Embedding'}配置` : `编辑${configType === 'llm' ? 'LLM' : 'Embedding'}配置`"
      width="600px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" class="config-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商类型" prop="vendor_type">
              <el-select v-model="configForm.vendor_type" placeholder="请选择供应商类型" class="full-width">
                <el-option 
                  v-for="vendor in availableVendors[configType]"
                  :key="vendor"
                  :label="vendor"
                  :value="vendor"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模型名称" prop="model">
              <el-input v-model="configForm.model" placeholder="请输入模型名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="基础URL" prop="base_url">
          <el-input v-model="configForm.base_url" placeholder="请输入基础URL">
            <template #append v-if="configForm.base_url">
              <el-tooltip content="测试连接" placement="top">
                <el-button :icon="Link"></el-button>
              </el-tooltip>
            </template>
          </el-input>
          <div class="form-tip">可选项，留空将使用默认URL</div>
        </el-form-item>
        
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="configForm.api_key" placeholder="请输入API密钥" show-password />
          <div class="form-tip" v-if="dialogType === 'edit'">留空表示不修改API密钥</div>
        </el-form-item>
        
        <el-divider content-position="left">高级配置</el-divider>
        
        <el-form-item label="配置信息" prop="configStr">
          <el-input
            v-model="configForm.configStr"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的配置信息"
          />
          <div class="form-tip">可选，JSON格式，配置模型的特定参数</div>
        </el-form-item>
        
        <!-- LLM 特有设置 -->
        <template v-if="configType === 'llm'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="默认对话" prop="is_default_chat">
                <el-switch v-model="configForm.is_default_chat" />
                <div class="form-tip">设置为默认对话模型</div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="默认拆分" prop="is_default_splitter">
                <el-switch v-model="configForm.is_default_splitter" />
                <div class="form-tip">设置为默认拆分模型</div>
              </el-form-item>
            </el-col>
          </el-row>
        </template>
        
        <!-- Embedding 特有设置 -->
        <template v-if="configType === 'embedding'">
          <el-form-item label="设为默认" prop="is_default">
            <el-switch v-model="configForm.is_default" />
            <div class="form-tip">设置为默认Embedding模型</div>
          </el-form-item>
        </template>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="loading.submit">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="delete-confirm">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p>确定要删除此配置吗？此操作不可恢复。</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteConfig" :loading="loading.delete">确定删除</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 设为默认确认对话框 -->
    <el-dialog
      v-model="setDefaultDialogVisible"
      :title="`设置默认${getDefaultTypeText}`"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="confirm-content">
        <p>确定要将此配置设为默认{{getDefaultTypeText}}吗？</p>
        <p class="confirm-tip">注意：系统中只能有一个默认{{getDefaultTypeText}}，设置后会取消其他配置的默认状态。</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="setDefaultDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="setAsDefault" :loading="loading.setDefault">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Setting, Edit, Delete, Plus, Check, Search, ChatDotRound, Link,
  WarningFilled, Grid
} from '@element-plus/icons-vue';
import { getRequest, postRequest, putRequest, deleteRequest } from '@/utils/http';

// 数据部分
const activeTab = ref('llm');
const llmConfigs = ref<any[]>([]);
const embeddingConfigs = ref<any[]>([]);
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const configType = ref<'llm' | 'embedding'>('llm');
const deleteDialogVisible = ref(false);
const setDefaultDialogVisible = ref(false);
const currentConfig = ref<any>(null);
const defaultSettingType = ref<'chat' | 'splitter' | null>(null);
const llmSearchText = ref('');
const embeddingSearchText = ref('');

// 过滤后的配置列表
const filteredLlmConfigs = computed(() => {
  if (!llmSearchText.value) return llmConfigs.value;
  
  const searchTerm = llmSearchText.value.toLowerCase();
  return llmConfigs.value.filter(config => 
    config.model.toLowerCase().includes(searchTerm) || 
    config.vendor_type.toLowerCase().includes(searchTerm)
  );
});

const filteredEmbeddingConfigs = computed(() => {
  if (!embeddingSearchText.value) return embeddingConfigs.value;
  
  const searchTerm = embeddingSearchText.value.toLowerCase();
  return embeddingConfigs.value.filter(config => 
    config.model.toLowerCase().includes(searchTerm) || 
    config.vendor_type.toLowerCase().includes(searchTerm)
  );
});

// 获取默认类型文本描述
const getDefaultTypeText = computed(() => {
  if (configType.value === 'embedding') return 'Embedding模型';
  if (defaultSettingType.value === 'chat') return '对话模型';
  if (defaultSettingType.value === 'splitter') return '拆分模型';
  return '模型';
});

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
    { validator: (rule: any, value: any, callback: (error?: Error) => void) => {
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
    { validator: (rule: any, value: any, callback: (error?: Error) => void) => {
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
  delete: false,
  setDefault: false
});

// 可用的供应商类型
const availableVendors = {
  llm: ['OPENAI', 'DOUBAO', 'ZHIPUAI', 'SPARKAI', 'ONEAPI', 'SILICONFLOW'],
  embedding: ['OPENAI', 'ONEAPI', 'ZHIPUAI', 'DOUBAO', 'SILICONFLOW']
};

// 处理标签页切换
const handleTabClick = () => {
  // 标签切换时的逻辑
  if (activeTab.value === 'llm' && llmConfigs.value.length === 0) {
    fetchLlmConfigs();
  } else if (activeTab.value === 'embedding' && embeddingConfigs.value.length === 0) {
    fetchEmbeddingConfigs();
  }
};

// 格式化日期显示
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateString;
  }
};

// 根据供应商类型获取标签类型
const getVendorTagType = (vendor: string) => {
  const typeMap: Record<string, string> = {
    'OPENAI': 'success',
    'ZHIPUAI': 'warning',
    'DOUBAO': 'info',
    'SPARKAI': 'danger',
    'ONEAPI': 'primary',
    'SILICONFLOW': ''
  };
  return typeMap[vendor] || '';
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
      ElMessage.success({
        message: dialogType.value === 'create' ? '添加成功' : '更新成功',
        type: 'success'
      });
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

// 确认设为默认
const confirmSetDefault = (type: 'llm' | 'embedding', id: number, defaultType?: 'chat' | 'splitter') => {
  configType.value = type;
  currentConfig.value = { id };
  defaultSettingType.value = defaultType || null;
  setDefaultDialogVisible.value = true;
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
      ElMessage.success({
        message: '删除成功',
        type: 'success'
      });
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
const setAsDefault = async () => {
  if (!currentConfig.value) return;
  
  loading.setDefault = true;
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  let url;
  
  if (configType.value === 'llm') {
    if (defaultSettingType.value === 'chat') {
      url = `/v1/api/mark/admin/llm_configs/${currentConfig.value.id}/set_default_chat`;
    } else if (defaultSettingType.value === 'splitter') {
      url = `/v1/api/mark/admin/llm_configs/${currentConfig.value.id}/set_default_splitter`;
    } else {
      url = `/v1/api/mark/admin/llm_configs/${currentConfig.value.id}/set_default_chat`;
    }
  } else {
    url = `/v1/api/mark/admin/embedding_configs/${currentConfig.value.id}/set_default`;
  }
  
  try {
    const response = await postRequest<any>(`${baseURL}${url}`, {});
    if (response?.code === 200) {
      ElMessage.success({
        message: '设置默认配置成功',
        type: 'success'
      });
      setDefaultDialogVisible.value = false;
      
      // 刷新数据
      if (configType.value === 'llm') {
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
  } finally {
    loading.setDefault = false;
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
  margin-bottom: 20px;
  padding: 0 10px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title h2 {
  font-size: 22px;
  font-weight: 500;
  margin: 0;
  color: #303133;
}

.page-title .el-icon {
  font-size: 22px;
  color: #409eff;
}

.main-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.config-tabs {
  margin-top: 8px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tab-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.search-input {
  width: 240px;
}

.config-table {
  margin-bottom: 20px;
  border-radius: 4px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.full-width {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.delete-confirm {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}

.warning-icon {
  font-size: 24px;
  color: #f56c6c;
}

.confirm-content {
  padding: 12px;
  line-height: 1.6;
}

.confirm-tip {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px 0;
}

.config-form :deep(.el-form-item__label) {
  font-weight: 500;
}

/* 响应式设计 */
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
  
  .left-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>
