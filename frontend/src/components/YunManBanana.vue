<template>
  <div class="w-full h-full flex flex-col p-6 gap-6 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[100px] pointer-events-none"></div>

    <!-- 顶部配置栏 (输入API地址) -->
    <div class="flex items-center gap-4 p-4 rounded-2xl bg-[#18181b]/60 border border-white/5 backdrop-blur-md shrink-0 z-10">
      <div class="flex items-center gap-2 text-cyan-400 font-bold">
        <Server :size="20" />
        <span>服务器连接</span>
      </div>
      <input
        v-model="serverUrl"
        type="text"
        placeholder="请输入仙宫云公网链接 (例如 https://xxxxx-7860.container.x-gpu.com/)"
        class="flex-1 bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-sm text-gray-300 focus:border-cyan-500 focus:text-white transition-all outline-none font-mono"
      />
      <div class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold"
           :class="isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'">
        <span class="w-2 h-2 rounded-full animate-pulse" :class="isConnected ? 'bg-green-400' : 'bg-red-400'"></span>
        {{ isConnected ? '已连接' : '未连接' }}
      </div>
    </div>

    <!-- 主工作区 -->
    <div class="flex-1 flex gap-6 min-h-0 z-10">

      <!-- 左侧：控制面板 -->
      <div class="w-[400px] flex flex-col gap-6 overflow-y-auto scrollbar-hide pr-2">

        <!-- 提示词输入 -->
        <div class="panel-card group">
          <div class="card-header">
            <Sparkles :size="18" class="text-purple-400" />
            <span class="font-bold text-gray-200">画面描述 (Prompt)</span>
          </div>
          <div class="relative mt-2">
            <textarea
              v-model="form.prompt"
              rows="5"
              placeholder="描述你想生成的画面..."
              class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl p-4 text-white placeholder-gray-600 focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all resize-none custom-scroll"
            ></textarea>
            <button @click="clearPrompt" class="absolute bottom-3 right-3 text-xs text-gray-500 hover:text-white transition-colors">清空</button>
          </div>
        </div>

        <!-- 参数控制 -->
        <div class="panel-card space-y-6">
          <div class="card-header mb-4">
            <Sliders :size="18" class="text-cyan-400" />
            <span class="font-bold text-gray-200">生成参数</span>
          </div>

          <!-- 尺寸选择 -->
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">分辨率 ({{ form.width }} x {{ form.height }})</span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="input-group">
                <span class="label">宽</span>
                <input type="number" v-model.number="form.width" class="input-number" step="64">
              </div>
              <div class="input-group">
                <span class="label">高</span>
                <input type="number" v-model.number="form.height" class="input-number" step="64">
              </div>
            </div>
            <input type="range" v-model.number="form.width" min="512" max="2048" step="64" class="w-full accent-cyan-500 h-1 bg-white/10 rounded-lg appearance-none cursor-pointer">
          </div>

          <!-- 步数 & 种子 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm text-gray-400">迭代步数</label>
              <div class="relative">
                <input type="number" v-model.number="form.steps" class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white text-center font-mono focus:border-cyan-500 outline-none">
              </div>
            </div>
            <div class="space-y-2">
              <label class="text-sm text-gray-400">随机种子 (-1随机)</label>
              <div class="relative">
                 <input type="number" v-model.number="form.seed" class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white text-center font-mono focus:border-cyan-500 outline-none">
                 <button @click="form.seed = -1" class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-cyan-400" title="重置随机">
                   <RefreshCw :size="14" />
                 </button>
              </div>
            </div>
          </div>

          <!-- 画质增强开关 -->
          <div class="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 cursor-pointer hover:bg-white/10 transition-colors" @click="form.useEnhancer = !form.useEnhancer">
            <div class="flex items-center gap-3">
              <Wand2 :size="18" :class="form.useEnhancer ? 'text-yellow-400' : 'text-gray-500'" />
              <div class="flex flex-col">
                <span class="text-sm font-bold text-gray-200">自动画质增强</span>
                <span class="text-xs text-gray-500">添加细节修饰词，提升质感</span>
              </div>
            </div>
            <div class="w-10 h-5 rounded-full relative transition-colors duration-300" :class="form.useEnhancer ? 'bg-cyan-500' : 'bg-gray-700'">
              <div class="absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-transform duration-300" :class="form.useEnhancer ? 'translate-x-5' : 'translate-x-0'"></div>
            </div>
          </div>
        </div>

        <!-- 生成按钮 -->
        <button
          @click="handleGenerate"
          :disabled="generating || !isConnected"
          class="btn-generate group"
        >
          <div class="relative z-10 flex items-center justify-center gap-2">
            <Loader2 v-if="generating" class="animate-spin" />
            <Zap v-else class="group-hover:scale-110 transition-transform" />
            <span>{{ generating ? '云端生成中...' : '立即生成 (RUN)' }}</span>
          </div>
          <!-- 流光背景 -->
          <div class="absolute inset-0 bg-gradient-to-r from-purple-600 via-cyan-500 to-purple-600 bg-[length:200%_auto] animate-gradient opacity-80 group-hover:opacity-100"></div>
        </button>

      </div>

      <!-- 右侧：结果展示 -->
      <div class="flex-1 flex flex-col gap-4 min-w-0">
        <!-- 预览区 -->
        <div class="flex-1 rounded-2xl bg-[#0a0a0a] border border-white/10 relative overflow-hidden group flex items-center justify-center shadow-2xl">

          <!-- 空状态 -->
          <div v-if="!resultImage && !generating" class="text-center">
            <div class="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4 border border-white/10 group-hover:border-cyan-500/50 transition-colors">
              <Image :size="32" class="text-gray-600 group-hover:text-cyan-500/50 transition-colors" />
            </div>
            <p class="text-gray-500 font-mono text-sm">等待生成指令...</p>
          </div>

          <!-- 生成中动画 -->
          <div v-if="generating" class="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm z-20">
            <div class="relative w-32 h-32">
               <div class="absolute inset-0 rounded-full border-t-2 border-cyan-500 animate-spin"></div>
               <div class="absolute inset-4 rounded-full border-r-2 border-purple-500 animate-spin-reverse"></div>
            </div>
            <p class="mt-8 text-cyan-400 font-bold tracking-widest animate-pulse">AI PAINTING...</p>
            <p class="mt-2 text-xs text-gray-500 font-mono">{{ statusMsg }}</p>
          </div>

          <!-- 结果图片 -->
          <img
            v-if="resultImage"
            :src="resultImage"
            class="w-full h-full object-contain relative z-10 transition-all duration-500"
            :class="generating ? 'blur-lg scale-105' : 'blur-0 scale-100'"
          />

          <!-- 悬浮下载栏 -->
          <div v-if="resultImage && !generating" class="absolute bottom-6 left-1/2 -translate-x-1/2 px-6 py-3 bg-black/60 backdrop-blur-md rounded-full border border-white/10 flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-4 group-hover:translate-y-0 z-30">
            <button @click="downloadImage" class="flex items-center gap-2 text-white hover:text-cyan-400 transition-colors text-sm font-bold">
              <Download :size="16" /> 下载原图
            </button>
            <div class="w-[1px] h-4 bg-white/20"></div>
            <button @click="openImageNewTab" class="flex items-center gap-2 text-white hover:text-purple-400 transition-colors text-sm font-bold">
              <Maximize2 :size="16" /> 全屏查看
            </button>
          </div>
        </div>

        <!-- 终端日志 (仿黑客风格) -->
        <div class="h-48 rounded-xl bg-[#0F0F13] border border-white/10 p-4 font-mono text-xs overflow-hidden flex flex-col">
          <div class="flex items-center justify-between mb-2 text-gray-500 border-b border-white/5 pb-2">
            <div class="flex items-center gap-2">
              <Terminal :size="14" />
              <span>SERVER CONSOLE</span>
            </div>
            <div class="flex gap-1.5">
              <div class="w-2.5 h-2.5 rounded-full bg-red-500/20"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/20"></div>
              <div class="w-2.5 h-2.5 rounded-full bg-green-500/20"></div>
            </div>
          </div>
          <div ref="logContainer" class="flex-1 overflow-y-auto custom-scroll space-y-1 text-gray-400">
             <div v-for="(log, i) in logs" :key="i" class="break-all">
               <span class="text-purple-500 mr-2">[{{ getCurrentTime() }}]</span>
               <span :class="{'text-green-400': log.includes('✅'), 'text-red-400': log.includes('❌')}">{{ log }}</span>
             </div>
             <div v-if="generating" class="animate-pulse text-cyan-500">_ waiting for response...</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue';
import {
  Sparkles, Sliders, RefreshCw, Wand2, Zap, Loader2,
  Image, Download, Maximize2, Terminal, Server
} from 'lucide-vue-next';
import { useToast } from '../utils/toast';

const toast = useToast();

// === 状态定义 ===
// 默认填入你的仙宫云链接
const serverUrl = ref('https://xxxxx-7860.container.x-gpu.com/');
const generating = ref(false);
const resultImage = ref('');
// 这里的 isConnected 改为表示“是否准备就绪”，默认给True即可，因为是无状态请求
const isConnected = ref(true);
const statusMsg = ref('系统就绪...');
const logContainer = ref<HTMLElement | null>(null);
const logs = ref<string[]>(["等待指令..."]);

const form = reactive({
  prompt: "Young Chinese woman, hanfu, cyberpunk city background, neon lights, 8k masterpiece",
  width: 1024, // 注意：后端那边默认可能是1024，这里保持一致
  height: 768,
  steps: 6,
  seed: -1,
  useEnhancer: true
});

// === 辅助工具：添加日志 ===
const addLog = (msg: string) => {
  logs.value.push(msg);
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  });
};

const getCurrentTime = () => {
  const now = new Date();
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
};

// === 核心：调用本地 Python 后端 ===
const handleGenerate = async () => {
  if (!serverUrl.value) {
    toast.error("请输入服务器链接");
    return;
  }

  // 1. 准备工作
  generating.value = true;
  statusMsg.value = "正在请求本地后端...";
  resultImage.value = '';
  addLog(`🚀 发起请求 -> 本地后端 -> 仙宫云`);
  addLog(`🔗 目标服务器: ${serverUrl.value}`);
  addLog(`🎨 参数: [${form.width}x${form.height}] Steps:${form.steps}`);

  try {
    // 2. 发送请求给 main.py (banana_images.py)
    // 注意：这里访问的是你本地启动的 Python 服务端口 8000
    const response = await fetch('http://127.0.0.1:8000/api/banana/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        server_url: serverUrl.value,
        prompt: form.prompt,
        steps: form.steps,
        seed: form.seed,
        width: form.width,
        height: form.height,
        use_enhancer: form.useEnhancer
      })
    });

    // 3. 处理响应
    const data = await response.json();

    if (data.status === 'success') {
      // 成功！
      // data.image_url 是后端返回的相对路径，如 /banana_storage/xxx.webp
      // 我们需要加上后端地址 http://127.0.0.1:8000
      const fullImageUrl = `http://127.0.0.1:8000${data.image_url}`;

      resultImage.value = fullImageUrl;
      addLog(`📄 云端日志: ${data.server_log}`);
      addLog(`✅ 图片已下载到本地: ${data.local_path}`);
      toast.success("生成成功！");
    } else {
      // 失败
      throw new Error(data.msg || "未知错误");
    }

  } catch (e: any) {
    console.error(e);
    addLog(`❌ 生成失败: ${e.message}`);
    toast.error(`错误: ${e.message}`);
  } finally {
    generating.value = false;
    statusMsg.value = "就绪";
  }
};

const clearPrompt = () => { form.prompt = ''; };

const downloadImage = () => {
  if (!resultImage.value) return;
  const a = document.createElement('a');
  a.href = resultImage.value;
  // 🔥 这里改成 .png
  a.download = `Banana_Gen_${Date.now()}.png`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

const openImageNewTab = () => {
  if (resultImage.value) window.open(resultImage.value, '_blank');
};
</script>

<style scoped>
/* 样式复用与增强 */
.panel-card {
  @apply bg-[#151518] border border-white/5 rounded-2xl p-5 hover:border-white/10 transition-colors shadow-lg;
}
.card-header {
  @apply flex items-center gap-2 mb-2;
}

.input-group {
  @apply flex items-center bg-black/30 border border-white/10 rounded-lg overflow-hidden;
}
.input-group .label {
  @apply px-3 text-xs text-gray-500 font-bold bg-white/5 h-full flex items-center;
}
.input-number {
  @apply w-full bg-transparent text-white p-2 text-sm font-mono outline-none text-right;
}

.btn-generate {
  @apply w-full py-4 rounded-xl relative overflow-hidden font-black text-lg text-white shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_40px_rgba(168,85,247,0.5)] active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed;
}

.custom-scroll::-webkit-scrollbar {
  width: 4px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 2px;
}

.animate-spin-reverse {
  animation: spin-reverse 1.5s linear infinite;
}
@keyframes spin-reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient {
  animation: gradient 3s ease infinite;
}
</style>