<template>
      <!-- 🔥 1. 插入全局通知组件 -->
    <GlobalToast />
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >

    <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <!-- 背景遮罩 -->
      <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="close"></div>

      <!-- 主窗口 -->
      <div class="relative w-full max-w-2xl bg-[#0F0F13] rounded-[2rem] border border-white/10 shadow-[0_0_80px_rgba(236,72,153,0.15)] overflow-hidden flex flex-col max-h-[90vh]">

        <!-- 顶部流光线条 -->
        <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-pink-500 to-transparent animate-pulse"></div>

        <!-- 1. 头部 -->
        <div class="p-8 pb-4 flex justify-between items-center shrink-0 relative z-10">
          <div>
            <div class="flex items-center gap-3 mb-1">
              <span class="px-2 py-0.5 rounded text-[10px] font-black bg-pink-500/20 text-pink-400 border border-pink-500/30">二创动态漫</span>
              <h2 class="text-2xl font-black text-white italic tracking-wide text-glow-pink">
                {{ projectName }}
              </h2>
            </div>
            <p class="text-xs text-gray-500 font-mono">PROJECT ID: {{ projectId }}</p>
          </div>
          <button @click="close" class="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-all">
            <X :size="20" />
          </button>
        </div>

        <!-- 2. 内容滚动区 -->
        <div class="p-8 pt-2 overflow-y-auto custom-scroll space-y-8 relative z-10">

          <!-- 如果已经完成（加载了历史数据），显示简化信息 -->
          <div v-if="isFinished" class="p-6 rounded-2xl bg-green-500/10 border border-green-500/30 flex items-center gap-4 animate-fade-in">
            <div class="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 shadow-[0_0_15px_rgba(34,197,94,0.4)]">
              <Check :size="28" stroke-width="3" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">分析已完成</h3>
              <p class="text-sm text-gray-400 mt-1">已自动加载历史记录，可直接进入编辑。</p>
            </div>
          </div>

          <!-- 常规解析模块 (未完成时显示) -->
          <div v-if="!isFinished" class="space-y-3">
            <label class="flex items-center gap-2 text-sm font-bold text-gray-300">
              <Link :size="16" class="text-pink-400" />
              源视频解析
            </label>
            <div class="flex gap-3">
              <div class="relative flex-1 group">
                <input
                  v-model="dyLink"
                  type="text"
                  placeholder="粘贴抖音/TikTok分享链接..."
                  class="w-full bg-[#0a0a0a] border border-white/20 rounded-xl px-4 py-3.5 text-white placeholder-gray-600 focus:outline-none focus:border-pink-500/50 focus:shadow-[0_0_20px_rgba(236,72,153,0.2)] transition-all"
                />
              </div>
              <button
                @click="handleParse"
                :disabled="isParsing || !dyLink"
                class="px-6 py-3.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(236,72,153,0.3)] flex items-center gap-2 shrink-0"
              >
                <span v-if="isParsing" class="animate-spin">⏳</span>
                <span v-else>解析链接</span>
              </button>
            </div>

            <!-- 解析结果展示 -->
            <Transition enter-active-class="transition duration-500 ease-out" enter-from-class="opacity-0 translate-y-4" enter-to-class="opacity-100 translate-y-0">
              <div v-if="parsedUrl" class="relative p-5 rounded-2xl bg-[#1a1a1f] border border-pink-500/30 group overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-r from-pink-500/5 via-purple-500/5 to-transparent pointer-events-none"></div>
                <div class="relative z-10 space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="text-xs font-bold text-pink-400 flex items-center gap-2">
                      <Check :size="14" /> 解析成功
                    </span>
                    <span class="text-[10px] text-gray-500 font-mono">NO WATERMARK</span>
                  </div>
                  <p class="text-sm text-gray-200 line-clamp-1 font-medium">{{ videoDesc || '未知标题' }}</p>
                  <div class="flex gap-2">
                    <div class="relative flex-1">
                      <input
                        readonly
                        :value="parsedUrl"
                        class="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-xs text-gray-400 font-mono focus:outline-none focus:border-pink-500/30"
                      />
                    </div>
                    <button
                      @click="handleLocalDownload"
                      :disabled="isDownloading"
                      class="px-4 py-2 rounded-lg bg-white/10 hover:bg-pink-500 hover:text-white text-gray-300 text-xs font-bold transition-all flex items-center gap-2 border border-white/10 hover:border-pink-400 hover:shadow-[0_0_15px_rgba(236,72,153,0.4)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span v-if="isDownloading" class="animate-spin">⏳</span>
                      <Download v-else :size="14" />
                      {{ isDownloading ? '下载中...' : '保存到本地' }}
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- 文件上传区域 (未完成时显示) -->
          <div v-if="!isFinished" class="grid grid-cols-2 gap-6">
            <!-- 上传字幕 (SRT) -->
            <div class="space-y-3">
              <label class="flex items-center gap-2 text-sm font-bold text-gray-300">
                <FileCode :size="16" class="text-cyan-400" /> 上传字幕 (SRT)
              </label>
              <div
                class="h-32 rounded-xl border-2 border-dashed border-white/10 bg-white/5 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all cursor-pointer flex flex-col items-center justify-center gap-2 relative overflow-hidden group"
                @click="triggerUpload('srt')"
              >
                <div v-if="!files.srt" class="flex flex-col items-center">
                  <UploadCloud :size="24" class="text-gray-500 group-hover:text-cyan-400 group-hover:scale-110 transition-all duration-300" />
                  <span class="text-xs text-gray-500 mt-2 font-medium">点击上传 .srt</span>
                </div>
                <div v-else class="flex flex-col items-center z-10">
                  <div class="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 mb-1">
                    <span class="text-[10px] font-black">SRT</span>
                  </div>
                  <span class="text-xs text-white mt-1 max-w-[120px] truncate">{{ files.srt.name }}</span>
                </div>
                <input type="file" ref="srtInput" class="hidden" accept=".srt" @change="(e) => onFileChange(e, 'srt')">
              </div>
            </div>

            <!-- 上传视频 -->
            <div class="space-y-3">
              <label class="flex items-center gap-2 text-sm font-bold text-gray-300">
                <Video :size="16" class="text-purple-400" /> 上传视频 (MP4)
              </label>
              <div
                class="h-32 rounded-xl border-2 border-dashed border-white/10 bg-white/5 hover:border-purple-500/50 hover:bg-purple-500/5 transition-all cursor-pointer flex flex-col items-center justify-center gap-2 relative overflow-hidden group"
                @click="triggerUpload('video')"
              >
                <div v-if="!files.video" class="flex flex-col items-center">
                  <UploadCloud :size="24" class="text-gray-500 group-hover:text-purple-400 group-hover:scale-110 transition-all duration-300" />
                  <span class="text-xs text-gray-500 mt-2 font-medium">点击上传 .mp4</span>
                </div>
                <div v-else class="flex flex-col items-center z-10">
                  <div class="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 mb-1">
                    <Video :size="20" />
                  </div>
                  <span class="text-xs text-white mt-1 max-w-[120px] truncate">{{ files.video.name }}</span>
                </div>
                <input type="file" ref="videoInput" class="hidden" accept="video/*" @change="(e) => onFileChange(e, 'video')">
              </div>
            </div>
          </div>

          <!-- C. 进度条 (仅在处理中显示) -->
          <div class="space-y-2" v-if="isProcessing">
            <div class="flex justify-between text-xs font-bold">
              <span class="text-gray-400">{{ statusMsg }}</span>
              <span class="text-pink-400">{{ progress.toFixed(0) }}%</span>
            </div>
            <div class="h-3 bg-[#0a0a0a] rounded-full overflow-hidden border border-white/10 relative">
              <div
                class="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 animate-gradient-x transition-all duration-300 rounded-full shadow-[0_0_15px_rgba(236,72,153,0.5)]"
                :style="{ width: progress + '%' }"
              ></div>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent w-full -translate-x-full animate-shine-fast"></div>
            </div>
          </div>

        </div>

        <!-- 3. 底部按钮组 -->
        <div class="p-8 pt-0 mt-4 relative z-10">

          <!-- A. 开始/处理中 -->
          <button
            v-if="!isFinished"
            @click="handleExtract"
            :disabled="isProcessing || !files.video"
            class="w-full py-4 rounded-xl relative group overflow-hidden transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-[length:200%_auto] animate-flow-bg"></div>
            <div class="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors"></div>
            <div class="relative flex items-center justify-center gap-3 text-white font-black text-lg tracking-widest uppercase">
              <Cpu :size="24" :class="{'animate-spin': isProcessing}" />
              <span>{{ isProcessing ? '正在处理中...' : '开始分析视频' }}</span>
            </div>
          </button>

          <!-- B. 处理完成 -> 下一步 -->
          <button
            v-else
            @click="handleNextStep"
            class="w-full py-4 rounded-xl relative group overflow-hidden transition-all hover:scale-[1.01] active:scale-[0.99] shadow-[0_0_30px_rgba(34,197,94,0.4)]"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-green-500 via-emerald-400 to-green-600 bg-[length:200%_auto] animate-flow-bg"></div>
            <div class="relative flex items-center justify-center gap-3 text-black font-black text-lg tracking-widest uppercase">
              <span>进入视频生成</span>
              <ArrowRight :size="24" class="group-hover:translate-x-1 transition-transform" />
            </div>
          </button>

        </div>

        <!-- 装饰背景 -->
        <div class="absolute -top-20 -right-20 w-64 h-64 bg-pink-600/20 blur-[100px] rounded-full pointer-events-none"></div>
        <div class="absolute -bottom-20 -left-20 w-64 h-64 bg-purple-600/20 blur-[100px] rounded-full pointer-events-none"></div>

      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { X, Link, Check, UploadCloud, FileText, Video, FileCheck, Cpu, Download, FileCode, ArrowRight } from 'lucide-vue-next';

// 1. 引用同级组件 (兄弟关系)
import GlobalToast from './GlobalToast.vue';

// 2. 🔥 修改这里：使用相对路径 "../" 返回上一级找到 utils
import { useToast } from '../utils/toast';

// 🔥 2. 获取 toast 实例
const toast = useToast();

const props = defineProps<{
  isOpen: boolean;
  projectName: string;
  projectId: string | number;
}>();

const emit = defineEmits(['close', 'next', 'extract']); // 'extract' 用于向父组件传数据

// 状态
const dyLink = ref('');
const isParsing = ref(false);
const isDownloading = ref(false);
const parsedUrl = ref('');
const videoDesc = ref('');
const files = reactive<{ srt: File | null; video: File | null }>({
  srt: null,
  video: null
});
const progress = ref(0);
const isProcessing = ref(false);
const isFinished = ref(false);
const status = ref('idle');

const srtInput = ref<HTMLInputElement | null>(null);
const videoInput = ref<HTMLInputElement | null>(null);

// 监听弹窗打开，尝试加载历史数据
watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.projectName) {
    // 重置状态
    isFinished.value = false;
    isProcessing.value = false;
    progress.value = 0;
    files.srt = null;
    files.video = null;
    dyLink.value = '';
    parsedUrl.value = '';
await checkHistoryData(); // <--- 这里会自动去后端查，如果查到了，就会把 isFinished 设为 true
    await checkHistoryData();
  }
});

const checkHistoryData = async () => {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/project_data/${encodeURIComponent(props.projectName)}`);
    const resData = await res.json();

    if (resData.status === 'success') {
      // 自动恢复状态
      isFinished.value = true;
      emit('extract', resData.data); // 把数据传给父组件
      console.log("已自动加载历史分析数据");
    }
  } catch (e) {
    console.log("无历史数据或加载失败");
  }
};

const statusMsg = computed(() => {
  if (status.value === 'uploading') return '🚀 正在上传视频和字幕...';
  if (status.value === 'cutting') return '✂️ AI 正在智能拆分镜头...';
  if (status.value === 'done') return '✅ 处理完成！';
  return '等待开始...';
});

const close = () => {
  if (isProcessing.value && !isFinished.value) {
    if (!confirm('任务正在处理中，确定要关闭吗？')) return;
  }
  emit('close');
};

const handleParse = async () => {
  if (!dyLink.value) return;
  isParsing.value = true;
  try {
    const res = await fetch('http://127.0.0.1:8000/api/parse_video', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ url: dyLink.value }) });
    const data = await res.json();
    if (data.status === 'success') { parsedUrl.value = data.video_url; videoDesc.value = data.desc; } else { toast.success(data.msg); }
  } catch { toast.error('解析失败'); } finally { isParsing.value = false; }
};

const handleLocalDownload = async () => {
  isDownloading.value = true;
  try {
    const res = await fetch('http://127.0.0.1:8000/api/download_video_local', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ video_url: parsedUrl.value, desc: videoDesc.value }) });
    const data = await res.json();
    if (data.status === 'success') toast.success(data.msg);
  } catch { toast.error('下载失败'); } finally { isDownloading.value = false; }
};

const triggerUpload = (t: 'srt' | 'video') => t==='srt' ? srtInput.value?.click() : videoInput.value?.click();
const onFileChange = (e: Event, t: 'srt' | 'video') => { if ((e.target as HTMLInputElement).files?.length) files[t] = (e.target as HTMLInputElement).files![0]; };

const handleExtract = async () => {
  if (!files.video) return toast.warning("请先上传视频");
  isProcessing.value = true;
  status.value = 'uploading';
  progress.value = 0;

  const fd = new FormData();
  fd.append('video_file', files.video);
  if (files.srt) fd.append('srt_file', files.srt);
  fd.append('project_id', String(props.projectId));
  fd.append('project_name', props.projectName);

  const timer = setInterval(() => {
    if (progress.value < 50) progress.value += 2;
    else if (progress.value < 80) { progress.value += 0.5; status.value = 'cutting'; }
    else if (progress.value < 99) progress.value += 0.1;
  }, 100);

  try {
    const res = await fetch('http://127.0.0.1:8000/api/analyze_video', { method: 'POST', body: fd });
    const data = await res.json();
    clearInterval(timer);

    if (data.status === 'success') {
      progress.value = 100;
      isFinished.value = true;
      isProcessing.value = false;
      emit('extract', data.data); // 传递数据
    } else {
      toast.error(`失败: ${data.msg}`);
      isProcessing.value = false;
    }
  } catch (e) {
    clearInterval(timer); toast.error("网络错误"); isProcessing.value = false;
  }
};

const handleNextStep = () => {
  emit('next');
  close();
};
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(236,72,153,0.3); border-radius: 4px; }
.text-glow-pink { text-shadow: 0 0 20px rgba(236, 72, 153, 0.5); }
@keyframes shine-fast { from { transform: translateX(-100%); } to { transform: translateX(200%); } }
.animate-shine-fast { animation: shine-fast 1.5s infinite linear; }
@keyframes flowBg { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
.animate-flow-bg { animation: flowBg 2s linear infinite; }
.animate-fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>