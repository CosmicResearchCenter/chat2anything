<template>
  <el-container>
    <el-aside width="200px"></el-aside>
    <el-main>
      <el-steps :active="activeStep" align-center finish-status="success">
        <el-step title="选择数据源"></el-step>
        <el-step title="数据清洗参数选择"></el-step>
        <el-step title="处理并完成"></el-step>
      </el-steps>

      <!-- 第一步：选择数据源 -->
      <div v-if="activeStep === 1" class="step1">
        <el-upload class="upload-demo" drag :http-request="uploadFile" :limit="1" :auto-upload="false"
          accept=".txt,.md,.pdf,.html,.xlsx,.xls,.docx,.csv,.bin,.py" @change="handleFileChange" show-file-list="false">
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">
            拖拽文件至此，或者
            <el-button type="text">选择文件</el-button>
          </div>
          <div class="el-upload__tip" slot="tip">
            已支持TXT, MARKDOWN, PDF, HTML, XLSX, XLS, DOCX, CSV, BIN, PY, 每个文件不超过15MB.
          </div>
        </el-upload>

        <el-card v-if="fileName" class="box-card">
          <div slot="header" class="clearfix">
            <span>{{ fileName }}</span>
          </div>
          <div class="text">文件大小: {{ fileSize }}</div>
        </el-card>
        <el-button style="margin-top: 20px;" type="primary" size="small" @click="nextStep">下一步</el-button>
      </div>

      <!-- 第二步：文本分段与清洗 -->
      <div v-if="activeStep === 2" class="step2">
        <el-row :gutter="20" class="step-content">
          <el-col :span="12">
            <el-card>
              <h3>选择分段模式</h3>
              <el-radio-group v-model="splitMode">
                <el-radio label="llm">LLM拆分</el-radio>
                <el-radio label="textBlock">文本块拆分</el-radio>
              </el-radio-group>
              <el-divider></el-divider>

              <!-- LLM拆分模式参数 -->
              <div v-if="splitMode === 'llm'">
                <h3>LLM拆分参数</h3>
                <el-input-number v-model="windowSize" :min="1" label="窗口大小" style="width: 150px;"></el-input-number>
                <el-input-number v-model="slideDistance" :min="1" label="滑动距离" style="width: 150px; margin-top: 10px;"></el-input-number>
              </div>

              <!-- 文本块拆分模式参数 -->
              <div v-else-if="splitMode === 'textBlock'">
                <h3>文本块拆分参数</h3>
                <el-input-number v-model="blockSize" :min="100" label="文本块大小" style="width: 150px;"></el-input-number>
                <el-input-number v-model="overLengthHandling" :min="20" label="运行超出长度" style="width: 150px;"></el-input-number>
              </div>

              <!-- <el-button @click="applySplitSettings" type="primary" size="small" style="margin-top: 20px;">应用</el-button> -->
            </el-card>
          </el-col>
        </el-row>
        <el-button style="margin-top: 20px;" type="primary" @click="applySplitSettings">下一步</el-button>
      </div>

      <!-- 第三步：处理并完成 -->
      <div v-if="activeStep === 3" class="step3">
        <el-card>
          <h3>处理完成！</h3>
          <p>你已经完成了所有步骤。</p>
        </el-card>
        <el-button style="margin-top: 20px;" type="primary" @click="toKnowledge">完成 </el-button>
      </div>
    </el-main>
  </el-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { getRequest, putRequest, postRequest } from '@/utils/http';
import { useRoute,useRouter } from 'vue-router';

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
        alert("请先选择文件！");
        return;
      }

      const formData = new FormData();
      formData.append('file', fileData.value);

      try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL;
        const headers= {
          'Authorization': 'Bearer ' + localStorage.getItem('token'),
          // 'Content-Type': 'multipart/form-data'
        }
        const response: any = await putRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId.value}`, formData);
        console.log(response);
        if (response.code === 200) {
          docId.value = response.data[0].doc_id;
          alert("文件上传成功！");
          activeStep.value = 2;
        } else {
          alert("文件上传失败，请重试！");
        }
      } catch (error) {
        console.error("上传文件时出错:", error);
        alert("文件上传失败，请检查网络连接！");
      }
    };

    const applySplitSettings = async () => {
      if (!docId.value) {
        alert("请先上传文件！");
        return;
      }

      const splitterModel = splitMode.value === 'llm' ? 0 : 1;
      const splitterArgs = splitMode.value === 'llm'
        ? { window_size: windowSize.value.toString(), step_size: slideDistance.value.toString() }
        : { chunk_size: blockSize.value.toString(), chunk_overlap: overLengthHandling.value.toString() };

      try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL;
        const response: any = await postRequest(baseURL+`/v1/api/mark/knowledgebase/${baseId.value}/doc/${docId.value}/index`, {
          "splitter_model": splitterModel,
          "splitter_args": splitterArgs
        });

        if (response.code === 200) {
          alert("索引处理成功，正在建立索引！");
          activeStep.value = 3;
          nextStep();
        } else {
          alert("索引处理失败，请重试！");
        }
      } catch (error) {
        console.error("索引处理时出错:", error);
        alert("索引处理失败，请检查网络连接！");
      }
    };

    const nextStep = () => {
      if (activeStep.value === 1) {
        if (!fileData.value) {
          alert("请先选择文件！");
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
.step-content {
  margin-top: 20px;
}

.segment-preview {
  margin-bottom: 10px;
}

/* 在小屏幕下调整步骤条为竖直方向 */
@media screen and (max-width: 768px) {
  .el-steps {
    flex-direction: column;
  }

  .step-content {
    flex-direction: column;
  }

  .el-col {
    width: 100%;
  }
}
</style>
