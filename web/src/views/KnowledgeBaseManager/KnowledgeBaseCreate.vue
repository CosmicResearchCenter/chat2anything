<template>
  <div class="knowledge-base-create">
    <el-card class="main-card">
      <el-steps :active="activeStep" align-center finish-status="success" class="steps-container">
        <el-step title="选择数据源" icon="el-icon-upload"></el-step>
        <el-step title="数据清洗参数" icon="el-icon-setting"></el-step>
        <el-step title="完成创建" icon="el-icon-check"></el-step>
      </el-steps>

      <div class="step-container">
        <!-- 第一步：选择数据源 -->
        <div v-if="activeStep === 1" class="step-content fade-in">
          <h2 class="step-title">上传知识库文件</h2>
          
          <el-upload 
            class="upload-area" 
            drag 
            :http-request="uploadFile" 
            :limit="1" 
            :auto-upload="false"
            accept=".txt,.md,.pdf,.html,.xlsx,.xls,.docx,.csv,.bin,.py" 
            @change="handleFileChange" 
            :show-file-list="false">
            <i class="el-icon-upload upload-icon"></i>
            <div class="upload-text">
              拖拽文件至此，或<el-button type="text">选择文件</el-button>
            </div>
            <div class="upload-tip">
              支持 TXT, MARKDOWN, PDF, HTML, XLSX, XLS, DOCX, CSV, BIN, PY 格式，单个文件不超过15MB
            </div>
          </el-upload>

          <transition name="fade">
            <el-card v-if="fileName" class="file-card">
              <div class="file-info">
                <i class="el-icon-document file-icon"></i>
                <div class="file-details">
                  <h4 class="file-name">{{ fileName }}</h4>
                  <span class="file-size">{{ fileSize }}</span>
                </div>
              </div>
            </el-card>
          </transition>
          
          <div class="step-actions">
            <el-button type="primary" :disabled="!fileData" @click="nextStep" size="medium">
              <i class="el-icon-right"></i> 下一步
            </el-button>
          </div>
        </div>

        <!-- 第二步：文本分段与清洗 -->
        <div v-if="activeStep === 2" class="step-content fade-in">
          <h2 class="step-title">设置文本处理参数</h2>
          
          <el-card class="params-card">
            <div class="split-mode-selector">
              <h3>选择分段模式</h3>
              <el-radio-group v-model="splitMode" size="medium" class="mode-group">
                <el-radio-button label="llm">
                  <i class="el-icon-s-operation"></i> LLM拆分
                </el-radio-button>
                <el-radio-button label="textBlock">
                  <i class="el-icon-s-grid"></i> 文本块拆分
                </el-radio-button>
              </el-radio-group>
            </div>

            <el-divider content-position="center">参数设置</el-divider>

            <!-- LLM拆分模式参数 -->
            <transition name="fade" mode="out-in">
              <div v-if="splitMode === 'llm'" class="params-section">
                <h3>LLM拆分参数</h3>
                <div class="param-item">
                  <span class="param-label">窗口大小：</span>
                  <el-slider
                    v-model="windowSize"
                    :min="500"
                    :max="5000"
                    :step="100"
                    show-input
                    :marks="{500: '500', 2000: '2000', 5000: '5000'}"
                  ></el-slider>
                </div>
                <div class="param-item">
                  <span class="param-label">滑动距离：</span>
                  <el-slider
                    v-model="slideDistance"
                    :min="100"
                    :max="3000"
                    :step="100"
                    show-input
                    :marks="{100: '100', 1500: '1500', 3000: '3000'}"
                  ></el-slider>
                </div>
              </div>
              
              <!-- 文本块拆分模式参数 -->
              <div v-else-if="splitMode === 'textBlock'" class="params-section">
                <h3>文本块拆分参数</h3>
                <div class="param-item">
                  <span class="param-label">文本块大小：</span>
                  <el-slider
                    v-model="blockSize"
                    :min="50"
                    :max="500"
                    :step="10"
                    show-input
                    :marks="{50: '50', 200: '200', 500: '500'}"
                  ></el-slider>
                </div>
                <div class="param-item">
                  <span class="param-label">重叠长度：</span>
                  <el-slider
                    v-model="overLengthHandling"
                    :min="10"
                    :max="100"
                    :step="5"
                    show-input
                    :marks="{10: '10', 50: '50', 100: '100'}"
                  ></el-slider>
                </div>
              </div>
            </transition>
          </el-card>
          
          <div class="step-actions">
            <el-button @click="activeStep = 1" plain size="medium">
              <i class="el-icon-back"></i> 上一步
            </el-button>
            <el-button type="primary" @click="applySplitSettings" size="medium" :loading="processing">
              <i class="el-icon-right"></i> 下一步
            </el-button>
          </div>
        </div>

        <!-- 第三步：处理并完成 -->
        <div v-if="activeStep === 3" class="step-content fade-in">
          <h2 class="step-title">知识库创建完成</h2>
          
          <el-card class="success-card">
            <div class="success-content">
              <i class="el-icon-success success-icon"></i>
              <h3 class="success-title">处理成功！</h3>
              <p class="success-message">你的知识库文件已成功处理并建立索引，现在可以使用啦。</p>
            </div>
          </el-card>
          
          <div class="step-actions">
            <el-button @click="activeStep = 2" plain size="medium">
              <i class="el-icon-back"></i> 上一步
            </el-button>
            <el-button type="success" @click="toKnowledge" size="medium">
              <i class="el-icon-check"></i> 完成
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getRequest, putRequest, postRequest } from '@/utils/http';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

export default defineComponent({
  setup() {
    const activeStep = ref(1);
    const fileName = ref('');
    const fileSize = ref('');
    const fileData = ref(null); // 保存上传的文件数据
    const splitMode = ref('llm');
    const windowSize = ref(2000);
    const slideDistance = ref(1500);
    const blockSize = ref(200);
    const overLengthHandling = ref(50);
    const baseId = ref('');
    const docId = ref('');
    const processing = ref(false);
    const route = useRoute();
    const router = useRouter();
    
    onMounted(() => {
      baseId.value = route.params.base_id as string;
      console.log("baseId:", baseId.value);
    });
    
    const toKnowledge = () => {
      router.push({ name: 'knowledge-base', params: { base_id: baseId.value } });
    };
    
    const handleFileChange = (file: any) => {
      fileName.value = file.name;
      fileSize.value = (file.size / 1024 / 1024).toFixed(2) + ' MB';
      fileData.value = file.raw;
    };

    const uploadFile = async () => {
      if (!fileData.value) {
        ElMessage.warning("请先选择文件");
        return;
      }

      const formData = new FormData();
      formData.append('file', fileData.value);
      processing.value = true;

      try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL;
        const response: any = await putRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId.value}`, formData);
        
        if (response.code === 200) {
          docId.value = response.data[0].doc_id;
          ElMessage.success("文件上传成功");
          activeStep.value = 2;
        } else {
          ElMessage.error("文件上传失败：" + (response.msg || "请重试"));
        }
      } catch (error) {
        console.error("上传文件时出错:", error);
        ElMessage.error("文件上传失败，请检查网络连接");
      } finally {
        processing.value = false;
      }
    };

    const applySplitSettings = async () => {
      if (!docId.value) {
        ElMessage.warning("请先上传文件");
        return;
      }

      const splitterModel = splitMode.value === 'llm' ? 0 : 1;
      const splitterArgs = splitMode.value === 'llm'
        ? { window_size: windowSize.value.toString(), step_size: slideDistance.value.toString() }
        : { chunk_size: blockSize.value.toString(), chunk_overlap: overLengthHandling.value.toString() };

      processing.value = true;
      try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL;
        const response: any = await postRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId.value}/doc/${docId.value}/index`, {
          "splitter_model": splitterModel,
          "splitter_args": splitterArgs
        });

        if (response.code === 200) {
          ElMessage.success("索引处理成功，正在建立知识库");
          activeStep.value = 3;
        } else {
          ElMessage.error("索引处理失败：" + (response.msg || "请重试"));
        }
      } catch (error) {
        console.error("索引处理时出错:", error);
        ElMessage.error("索引处理失败，请检查网络连接");
      } finally {
        processing.value = false;
      }
    };

    const nextStep = () => {
      if (activeStep.value === 1) {
        if (!fileData.value) {
          ElMessage.warning("请先选择文件");
          return;
        }
        uploadFile();
      } else if (activeStep.value === 2) {
        applySplitSettings();
      } else if (activeStep.value < 3) {
        activeStep.value += 1;
      }
    };

    return {
      activeStep,
      fileName,
      fileSize,
      fileData,
      splitMode,
      windowSize,
      slideDistance,
      blockSize,
      overLengthHandling,
      processing,
      handleFileChange,
      uploadFile,
      applySplitSettings,
      nextStep,
      toKnowledge
    };
  }
});
</script>

<style scoped>
.knowledge-base-create {
  padding: 20px;
}

.main-card {
  margin: 0 auto;
  width: auto;
  height: auto;
  max-width: 1000px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.steps-container {
  margin-bottom: 30px;
  padding-top: 10px;
}

.step-container {
  min-height: 400px;
  padding: 10px;
  overflow-y: auto; /* 添加垂直滚动条，防止内容溢出 */
}

.step-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.step-title {
  color: #303133;
  margin-bottom: 30px;
  text-align: center;
  font-weight: 500;
}

.upload-area {
  width: 100%;
  max-width: 500px;
  margin: 20px auto;
}

.upload-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 6px;
}

.upload-tip {
  font-size: 13px;
  color: #909399;
}

.file-card {
  width: 100%;
  max-width: 500px;
  margin: 20px auto;
  transition: all 0.3s;
}

.file-info {
  display: flex;
  align-items: center;
}

.file-icon {
  font-size: 28px;
  margin-right: 15px;
  color: #409EFF;
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0;
  font-weight: 500;
  color: #303133;
  word-break: break-all;
}

.file-size {
  color: #909399;
  font-size: 13px;
}

.params-card {
  width: 100%;
  max-width: 700px;
  margin: 20px auto;
  overflow: hidden; /* 确保内容不溢出卡片 */
}

.split-mode-selector {
  margin-bottom: 20px;
  text-align: center;
}

.mode-group {
  margin-top: 15px;
}

.params-section {
  padding: 10px;
}

.param-item {
  margin: 20px 0;
}

.param-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
}

.success-card {
  width: 100%;
  max-width: 500px;
  margin: 20px auto;
}

.success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.success-icon {
  font-size: 60px;
  color: #67C23A;
  margin-bottom: 20px;
}

.success-title {
  color: #303133;
  font-weight: 500;
  margin-bottom: 10px;
}

.success-message {
  color: #606266;
  text-align: center;
}

.step-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 动画效果 */
.fade-in {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .knowledge-base-create {
    padding: 10px 5px;
  }

  .main-card {
    box-shadow: none;
    border: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }
  
  .step-title {
    font-size: 18px;
    margin-bottom: 15px;
  }
  
  .file-card, .params-card, .success-card {
    max-width: 100%;
    margin: 10px 0;
  }

  .step-container {
    padding: 5px;
    min-height: calc(100vh - 150px); /* 动态设置容器高度，避免溢出 */
  }

  .step-content {
    padding: 10px 0;
  }

  /* 滑块样式优化 */
  .el-slider {
    margin-bottom: 15px;
  }
  
  .el-slider__runway {
    width: 100% !important;
  }
  
  .el-slider__input {
    width: 80px !important;
  }

  .param-item {
    margin: 10px 0;
  }

  .param-label {
    font-size: 14px;
  }
  
  /* 修复模式选择按钮组响应式问题 */
  .mode-group {
    display: flex;
    flex-direction: column;
    width: 100%;
    align-items: center;
  }
  
  .mode-group .el-radio-button {
    margin-bottom: 10px;
    width: 80%;
  }
  
  .mode-group .el-radio-button__inner {
    width: 100%;
  }
  
  /* 确保步骤操作按钮响应式 */
  .step-actions {
    flex-wrap: wrap;
    margin-top: 15px;
  }
  
  .step-actions .el-button {
    margin: 5px;
  }
}

/* 针对超小屏幕的额外优化 */
@media screen and (max-width: 480px) {
  .upload-icon {
    font-size: 36px;
  }
  
  .upload-text {
    font-size: 14px;
  }
  
  .upload-tip {
    font-size: 12px;
  }
  
  .success-icon {
    font-size: 48px;
  }
  
  /* 优化滑块在超小屏幕上的显示 */
  .el-slider__runway {
    margin: 10px 0;
  }
  
  .el-slider__button-wrapper {
    transform: translateX(-50%);
  }
  
  .el-slider__input {
    width: 60px !important;
  }
  
  /* 调整参数标题大小 */
  .params-section h3 {
    font-size: 16px;
  }
}
</style>
