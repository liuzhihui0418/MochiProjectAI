<template>
  <div class="w-full h-full relative overflow-hidden flex flex-col">
    <!-- 顶部标题栏 -->
    <header class="h-24 px-12 flex items-center justify-between z-20 shrink-0 border-b border-white/5 bg-[#0a0a0a]/50 backdrop-blur-sm">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-400 flex items-center justify-center shadow-[0_0_20px_rgba(34,211,238,0.4)]">
          <Box :size="24" class="text-white" />
        </div>
        <div>
          <h1 class="text-2xl font-black text-white italic tracking-wide">
            ULTRA <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">UPSCALE</span>
          </h1>
          <p class="text-xs text-gray-400 font-mono mt-1">AI 智能无损放大 / 画质增强工作台</p>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="flex-1 flex overflow-hidden relative z-10">

      <!-- 左侧：功能选择与参数 -->
      <div class="w-[400px] border-r border-white/10 bg-[#0a0a0a]/80 backdrop-blur-xl p-8 flex flex-col gap-8 h-full overflow-y-auto custom-scroll">

        <!-- 模式切换 -->
        <div class="p-1 bg-white/5 rounded-xl flex">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="switchTab(tab.id)"
            class="flex-1 py-3 text-sm font-bold rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
            :class="currentTab === tab.id ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'"
          >
            <component :is="tab.icon" :size="16" />
            {{ tab.name }}
          </button>
        </div>

        <!-- 通用控制面板 (图片和视频共用结构) -->
        <div class="flex flex-col gap-6 animate-fade-in" :key="currentTab">

          <div class="space-y-3">
            <label class="text-sm font-bold text-gray-400">放大倍数</label>
            <div class="grid grid-cols-3 gap-3">
              <button
                v-for="s in [2, 3, 4]"
                :key="s"
                @click="config.scale = s"
                class="py-2 border rounded-lg text-sm font-mono transition-all"
                :class="config.scale === s ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10' : 'border-white/10 text-gray-500 hover:border-white/30'"
              >
                {{ s }}x
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <label class="text-sm font-bold text-gray-400">AI 模型</label>
            <select v-model="config.model" class="w-full bg-[#151518] border border-white/10 text-gray-300 text-sm rounded-xl px-4 py-3 focus:outline-none focus:border-cyan-500 transition-colors">
              <option value="realesrgan-x4plus-anime">二次元动漫专用 (推荐)</option>
              <option value="realesrgan-x4plus">真实照片/实景</option>
            </select>
          </div>

          <!-- 上传区域 -->
          <div
            class="border-2 border-dashed rounded-2xl h-48 flex flex-col items-center justify-center gap-3 transition-all cursor-pointer relative overflow-hidden group"
            :class="file ? 'border-cyan-500/50 bg-cyan-500/5' : 'border-white/10 hover:border-cyan-500/30 hover:bg-white/5'"
            @click="triggerUpload"
          >
            <!-- 动态 accept -->
            <input type="file" ref="fileInput" class="hidden"
                   :accept="currentTab === 'image' ? 'image/png, image/jpeg, image/jpg' : 'video/mp4, video/mov'"
                   @change="handleFileChange">

            <template v-if="!file">
              <UploadCloud :size="40" class="text-gray-500 group-hover:text-cyan-400 transition-colors duration-300" />
              <p class="text-sm text-gray-400 font-medium">点击或拖拽上传{{ currentTab === 'image' ? '图片' : '视频' }}</p>
              <span class="text-xs text-gray-600">{{ currentTab === 'image' ? '支持 PNG, JPG' : '支持 MP4 (建议 < 30秒)' }}</span>
            </template>

            <template v-else>
               <!-- 视频或图片的预览 -->
               <img v-if="currentTab === 'image'" :src="previewUrl" class="absolute inset-0 w-full h-full object-cover opacity-60" />
               <video v-else :src="previewUrl" class="absolute inset-0 w-full h-full object-cover opacity-60" autoplay muted loop></video>

               <div class="relative z-10 bg-black/70 px-4 py-2 rounded-full flex items-center gap-2 backdrop-blur-md border border-white/10">
                 <span class="text-xs text-white truncate max-w-[150px]">{{ file.name }}</span>
                 <X :size="14" class="text-gray-400 hover:text-red-400 cursor-pointer" @click.stop="clearFile" />
               </div>
            </template>
          </div>

          <button
            @click="startUpscale"
            :disabled="!file || processing"
            class="w-full py-4 rounded-xl font-black text-lg tracking-wider uppercase transition-all duration-300 relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
            :class="processing ? 'bg-gray-800 text-gray-500' : 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-[0_0_30px_rgba(59,130,246,0.4)] hover:shadow-[0_0_50px_rgba(34,211,238,0.6)] hover:scale-[1.02]'"
          >
            <span v-if="processing" class="flex items-center justify-center gap-2">
              <Loader2 :size="20" class="animate-spin" />
              {{ currentTab === 'video' ? '视频渲染中...' : '正在增强...' }}
            </span>
            <span v-else>开始增强 START</span>
          </button>

          <p v-if="currentTab === 'video'" class="text-xs text-center text-gray-500">
            * 视频处理极其消耗显卡，请耐心等待。<br>首次使用会自动下载模型(约300MB)。
          </p>

        </div>
      </div>

      <!-- 右侧：结果展示区 -->
      <div class="flex-1 bg-[#050505] relative flex items-center justify-center p-8">
        <!-- 网格背景 -->
        <div class="absolute inset-0 opacity-20" style="background-image: radial-gradient(#333 1px, transparent 1px); background-size: 20px 20px;"></div>

        <!-- 结果显示 -->
        <div v-if="resultUrl" class="relative w-full h-full max-w-5xl max-h-[800px] bg-[#0a0a0a] rounded-2xl border border-white/10 shadow-2xl overflow-hidden group flex items-center justify-center">

          <!-- 图片结果 -->
          <img v-if="currentTab === 'image'" :src="resultUrl" class="w-full h-full object-contain" />

          <!-- 视频结果 -->
          <video v-else :src="resultUrl" controls autoplay loop class="w-full h-full object-contain"></video>

          <!-- 下载浮层 -->
          <div class="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-black/90 to-transparent flex justify-between items-end translate-y-full group-hover:translate-y-0 transition-transform duration-300">
             <div>
               <h3 class="text-white font-bold text-lg">处理完成</h3>
               <p class="text-cyan-400 text-sm font-mono">{{ config.scale }}x Upscaled • {{ config.model }}</p>
             </div>
             <a :href="resultUrl" :download="`upscaled_${currentTab}`" class="px-6 py-2 bg-white text-black font-bold rounded-lg hover:bg-cyan-300 transition-colors flex items-center gap-2">
               <Download :size="18" /> 下载{{ currentTab === 'image' ? '图片' : '视频' }}
             </a>
          </div>
        </div>

        <!-- 默认状态 -->
        <div v-else-if="!processing" class="text-center">
          <div class="w-24 h-24 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-6 animate-pulse-slow">
            <component :is="currentTab === 'image' ? Image : Film" :size="40" class="text-gray-600" />
          </div>
          <p class="text-gray-500 font-mono text-lg">等待任务开始...</p>
        </div>

        <!-- 加载动画 -->
        <div v-if="processing" class="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm z-50">
            <div class="relative w-24 h-24">
                <div class="absolute inset-0 border-4 border-cyan-500/30 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-t-cyan-400 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
            </div>
            <p class="mt-8 text-cyan-300 font-bold text-xl tracking-widest animate-pulse">
              AI 正在重绘像素...
            </p>
            <p v-if="currentTab === 'video'" class="mt-2 text-gray-500 text-sm">正在逐帧修复，请勿关闭窗口</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { Box, Image, Film, UploadCloud, X, Loader2, Download } from 'lucide-vue-next';
import { useToast } from '../utils/toast';

const toast = useToast();

const tabs = [
  { id: 'image', name: '图片增强', icon: Image },
  { id: 'video', name: '视频增强', icon: Film },
];
const currentTab = ref('image');

const fileInput = ref<HTMLInputElement | null>(null);
const file = ref<File | null>(null);
const previewUrl = ref('');
const resultUrl = ref('');
const processing = ref(false);

const config = reactive({
  scale: 2,
  model: 'realesrgan-x4plus-anime'
});

const switchTab = (tabId: string) => {
  currentTab.value = tabId;
  clearFile();
};

const triggerUpload = () => fileInput.value?.click();

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const f = target.files[0];

    // 简单的类型检查
    if (currentTab.value === 'image' && !f.type.startsWith('image/')) {
      toast.error('请上传图片文件');
      return;
    }
    if (currentTab.value === 'video' && !f.type.startsWith('video/')) {
      toast.error('请上传视频文件');
      return;
    }

    file.value = f;
    previewUrl.value = URL.createObjectURL(f);
    resultUrl.value = '';
  }
};

const clearFile = () => {
  file.value = null;
  previewUrl.value = '';
  resultUrl.value = '';
  if (fileInput.value) fileInput.value.value = '';
};

const startUpscale = async () => {
  if (!file.value) return;

  processing.value = true;
  resultUrl.value = '';

  const formData = new FormData();
  formData.append('file', file.value);
  formData.append('scale', config.scale.toString());
  formData.append('model', config.model);

  // 区分接口
  const apiUrl = currentTab.value === 'image'
    ? 'http://127.0.0.1:8000/api/upscale/image'
    : 'http://127.0.0.1:8000/api/upscale/video';

  try {
    // 视频处理可能需要较长时间，设置较长的 timeout (这里依赖浏览器的默认设置，通常足够演示)
    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.status === 'success') {
      resultUrl.value = `http://127.0.0.1:8000${data.url}`;
      toast.success(currentTab.value === 'video' ? '视频处理完成！' : '图片处理成功！');
    } else {
      toast.error(data.msg || '处理失败');
    }
  } catch (error) {
    toast.error('网络连接错误，请检查后端服务');
    console.error(error);
  } finally {
    processing.value = false;
  }
};
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }
.animate-pulse-slow { animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
</style>