<template>
    <div class="common-layout">
        <el-container>
            <el-aside width="">
               <ChatList></ChatList> 
            </el-aside>
            <el-main>
                <ChatToLLM></ChatToLLM>
            </el-main>
        </el-container>
    </div>
</template>
<script lang="ts" setup>
import ChatList from "./ChatList.vue";
import ChatToLLM from "./ChatToLLM.vue";
</script>