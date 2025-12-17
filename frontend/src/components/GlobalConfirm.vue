<template>
  <Transition name="fade">
    <!-- 遮罩层 -->
    <div v-if="visible" class="fixed inset-0 z-[10000] flex items-center justify-center bg-black/80 backdrop-blur-sm">

      <!-- 弹窗主体 -->
      <div
        class="relative w-[450px] bg-[#0f0f13] border-2 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)] transform transition-all"
        :class="{
          'border-yellow-500/50 shadow-[0_0_30px_rgba(234,179,8,0.2)]': state.type === 'warning',
          'border-cyan-500/50 shadow-[0_0_30px_rgba(34,211,238,0.2)]': state.type === 'info',
          'border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.2)]': state.type === 'danger',
        }"
      >
        <!-- 顶部扫描线装饰 -->
        <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-white/50 to-transparent animate-scan"></div>

        <div class="p-8 text-center">
          <!-- 图标 -->
          <div class="mb-6 flex justify-center">
            <div v-if="state.type === 'warning'" class="w-16 h-16 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-500/30 text-yellow-400 animate-pulse">
              <AlertTriangle :size="32" />
            </div>
            <div v-else-if="state.type === 'danger'" class="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/30 text-red-400 animate-pulse">
              <AlertOctagon :size="32" />
            </div>
            <div v-else class="w-16 h-16 rounded-full bg-cyan-500/10 flex items-center justify-center border border-cyan-500/30 text-cyan-400 animate-pulse">
              <Info :size="32" />
            </div>
          </div>

          <!-- 标题与内容 -->
          <h3 class="text-2xl font-black text-white tracking-wider mb-3 uppercase">{{ state.title }}</h3>
          <p class="text-gray-400 text-base leading-relaxed mb-8">{{ state.message }}</p>

          <!-- 按钮组 -->
          <div class="flex gap-4">
            <button
              @click="handleCancel"
              class="flex-1 py-3 rounded-lg border border-white/10 text-gray-400 font-bold hover:bg-white/5 hover:text-white transition-all uppercase tracking-widest"
            >
              取消 / Cancel
            </button>
            <button
              @click="handleConfirm"
              class="flex-1 py-3 rounded-lg font-black text-black transition-all uppercase tracking-widest hover:scale-105 shadow-lg"
              :class="{
                'bg-gradient-to-r from-yellow-400 to-orange-500 hover:shadow-yellow-500/30': state.type === 'warning',
                'bg-gradient-to-r from-cyan-400 to-blue-500 hover:shadow-cyan-500/30': state.type === 'info',
                'bg-gradient-to-r from-red-500 to-pink-600 hover:shadow-red-500/30': state.type === 'danger',
              }"
            >
              确认 / Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useConfirm } from '../utils/confirm'; // 注意路径
import { AlertTriangle, AlertOctagon, Info } from 'lucide-vue-next';

const { visible, state, handleConfirm, handleCancel } = useConfirm();
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 进场时弹窗稍微放大一下 */
.fade-enter-active .relative {
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.fade-leave-active .relative {
  animation: popOut 0.2s ease-in;
}

@keyframes popIn {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
@keyframes popOut {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0; }
}

@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-scan {
  animation: scan 2s linear infinite;
}
</style>