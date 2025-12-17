<template>
  <!-- 通知容器：固定在右上角或顶部居中 -->
  <div class="fixed top-24 right-6 z-[9999] flex flex-col gap-3 pointer-events-none w-80">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="relative pointer-events-auto group overflow-hidden"
      >
        <!-- 核心卡片 -->
        <div
          class="relative bg-[#0a0a0f]/95 backdrop-blur-xl border-l-4 p-4 rounded-r-lg shadow-2xl overflow-hidden min-h-[80px] flex items-center gap-4"
          :class="{
            'border-green-500 shadow-[0_0_20px_rgba(34,197,94,0.2)]': toast.type === 'success',
            'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.2)]': toast.type === 'error',
            'border-yellow-500 shadow-[0_0_20px_rgba(234,179,8,0.2)]': toast.type === 'warning',
            'border-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.2)]': toast.type === 'info',
          }"
        >
          <!-- 背景扫描网格 -->
          <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none"></div>

          <!-- 动态扫描线 (仅装饰) -->
          <div class="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent animate-scan"></div>

          <!-- 图标 -->
          <div class="shrink-0">
            <div v-if="toast.type === 'success'" class="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center border border-green-500/30 text-green-400">
              <CheckCircle :size="20" />
            </div>
            <div v-else-if="toast.type === 'error'" class="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/30 text-red-400">
              <AlertOctagon :size="20" />
            </div>
            <div v-else-if="toast.type === 'warning'" class="w-10 h-10 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-500/30 text-yellow-400">
              <AlertTriangle :size="20" />
            </div>
            <div v-else class="w-10 h-10 rounded-full bg-cyan-500/10 flex items-center justify-center border border-cyan-500/30 text-cyan-400">
              <Info :size="20" />
            </div>
          </div>

          <!-- 文本内容 -->
          <div class="flex-1 min-w-0">
            <h4
              class="font-black tracking-wider text-sm uppercase mb-0.5"
              :class="{
                'text-green-400': toast.type === 'success',
                'text-red-400': toast.type === 'error',
                'text-yellow-400': toast.type === 'warning',
                'text-cyan-400': toast.type === 'info',
              }"
            >
              {{ toast.title }}
            </h4>
            <p v-if="toast.message" class="text-xs text-gray-400 font-mono break-words leading-tight">{{ toast.message }}</p>
          </div>

          <!-- 关闭按钮 -->
          <button @click="remove(toast.id)" class="absolute top-2 right-2 text-gray-600 hover:text-white transition-colors">
            <X :size="14" />
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '../utils/toast';
import { CheckCircle, AlertOctagon, AlertTriangle, Info, X } from 'lucide-vue-next';

// 获取全局状态
const { toasts, remove } = useToast();
</script>

<style scoped>
/* 进场/离场动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px) skewX(-10deg);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}

/* 扫描线动画 */
@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-scan {
  animation: scan 2s linear infinite;
}
</style>