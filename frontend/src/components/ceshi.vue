<template>
  <div class="font-sans text-gray-100 w-full h-screen bg-[#0a0a0f] overflow-hidden flex flex-col selection:bg-cyan-500/30 relative">
    <!-- 在顶部标题或按钮组附近 -->
<div class="flex flex-col items-end mr-4">
  <span class="text-xs font-bold transition-colors duration-300"
      :class="{
        'text-gray-500': saveStatus === 'saved',
        'text-yellow-400': saveStatus === 'saving',
        'text-red-500': saveStatus === 'error'
      }">
    <!-- 图标 + 文字 -->
    <template v-if="saveStatus === 'saving'">
       <Loader2 :size="12" class="inline animate-spin mr-1"/> 保存中...
    </template>
    <template v-else-if="saveStatus === 'error'">
       ⚠️ 保存失败
    </template>
    <template v-else>
       ☁️ 已保存 {{ lastSaveTime }}
    </template>
  </span>
</div>
<!-- 🟢 这是新窗口组件 (对应蓝色按钮) -->
<!-- 只要 showNewModal 变成 true，它就会显示 -->
<!-- 🟢 1. 新窗口组件 -->
<CharacterLibraryModal
  ref="libraryModalRef"
  v-if="showNewModal"
  :initial-data="characterList"
  :project-name="projectName"
  @close="showNewModal = false"
  @save="handleSaveCharacters"
/>
    <!-- ================= 0. 增强粒子背景特效层 ================= -->
    <canvas ref="canvasRef" class="absolute inset-0 w-full h-full z-0 pointer-events-auto"></canvas>
    <div class="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/90 via-[#0a0a0f]/60 to-[#0a0a0f]/90 z-0 pointer-events-none"></div>

    <!-- 扫描线效果 -->
    <div class="absolute inset-0 z-0 pointer-events-none opacity-20">
      <div class="absolute inset-0 bg-[linear-gradient(rgba(12,12,18,0.8)_1px,transparent_1px)] bg-[size:100%_2px]"></div>
      <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(12,12,18,0.8)_1px,transparent_1px)] bg-[size:2px_100%]"></div>
    </div>

    <!-- 霓虹光晕 -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-full blur-[120px] z-0"></div>
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-full blur-[120px] z-0"></div>

    <!-- ================= 顶部导航 ================= -->
    <header class="h-20 px-6 border-b border-white/5 bg-gradient-to-b from-black/90 via-[#05050a]/90 to-black/80 backdrop-blur-xl flex justify-between items-center shrink-0 z-50 relative overflow-hidden">
      <!-- 霓虹边框效果 -->
      <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-cyan-500/0 opacity-30"></div>

      <!-- 顶部扫描线 -->
      <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_8px_#22d3ee] animate-pulse"></div>

      <!-- 导航发光装饰 -->
      <div class="absolute -bottom-1 left-1/4 w-1/2 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/70 to-transparent blur-[2px]"></div>

      <div class="flex items-center gap-4 group/logo cursor-pointer z-10">
        <!-- 返回按钮 - 霓虹效果 -->
        <button @click="$emit('back')" class="p-2.5 rounded-xl bg-gradient-to-br from-[#111118] to-[#05050a] hover:from-[#1a1a2a] hover:to-[#0a0a1a] text-cyan-300 hover:text-white transition-all duration-300 border border-cyan-500/20 hover:border-cyan-400/40 shadow-[0_0_10px_rgba(34,211,238,0.1)] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] group/back">
          <ArrowLeft :size="20" class="group-hover/back:translate-x-[-2px] transition-transform" />
          <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover/back:opacity-100 transition-opacity duration-500 -z-10"></div>
        </button>

        <!-- LOGO 区域 -->
        <div class="relative w-10 h-10 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(34,211,238,0.3)] group-hover/logo:shadow-[0_0_40px_rgba(34,211,238,0.6)] transition-all duration-500 border border-cyan-500/20 group-hover/logo:border-cyan-400/50 bg-gradient-to-br from-cyan-900/20 to-purple-900/20">
          <img src="https://cdn.yunbaoymgf.chat/logo.png" alt="Logo" class="w-full h-full object-cover" />
          <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-white/30 to-transparent -translate-x-full group-hover/logo:translate-x-full transition-transform duration-700"></div>
          <!-- 霓虹边框 -->
          <div class="absolute inset-0 rounded-xl border border-cyan-400/20 group-hover/logo:border-cyan-300/40 transition-colors"></div>
        </div>

        <div class="flex flex-col">
          <h1 class="text-xl font-black text-white tracking-wider italic flex items-center">
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-cyan-400 to-purple-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">YunManGongFang</span>
            <span class="ml-1 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 drop-shadow-[0_0_10px_rgba(168,85,247,0.7)] animate-pulse">AI</span>
          </h1>
          <span class="text-[10px] text-gray-400 font-mono tracking-[0.2em] group-hover/logo:text-cyan-300 transition-colors bg-gradient-to-r from-cyan-500/20 to-purple-500/20 px-2 py-0.5 rounded-full">NEXUS WORKBENCH v2.0</span>
        </div>
      </div>

      <!-- 右侧按钮组 -->
      <div class="flex items-center gap-6 z-10">
        <!-- 模型选择 - 霓虹风格 -->
        <div class="relative group/model">
          <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500/30 to-purple-500/30 rounded-xl blur-sm opacity-0 group-hover/model:opacity-100 transition-opacity duration-500"></div>
          <button class="relative flex items-center gap-3 px-5 py-3 rounded-xl bg-gradient-to-br from-[#111118] to-[#0a0a12] border border-cyan-500/20 hover:border-cyan-400/40 transition-all min-w-[180px] justify-between shadow-[0_0_20px_rgba(0,0,0,0.5)] group-hover/model:shadow-[0_0_30px_rgba(34,211,238,0.2)]">
            <div class="flex items-center gap-3">
              <div class="relative">
                <Box :size="16" class="text-cyan-400" />
                <div class="absolute -inset-1 bg-cyan-500/20 blur-md rounded-full"></div>
              </div>
              <div class="flex flex-col items-start">
                <span class="text-[9px] text-cyan-300/80 font-bold uppercase tracking-wider">MODEL ENGINE</span>
                <span class="text-sm text-white font-mono font-bold">V1.5-REAL_PRO</span>
              </div>
            </div>
            <ChevronDown :size="16" class="text-cyan-300/60 group-hover/model:text-cyan-300 transition-colors group-hover/model:translate-y-0.5 transition-transform" />
          </button>
          <div class="absolute -bottom-1 left-2 right-2 h-[2px] bg-gradient-to-r from-cyan-500/0 via-cyan-400 to-cyan-500/0 blur-[4px] opacity-0 group-hover/model:opacity-100 transition-all duration-500"></div>
        </div>

        <div class="w-[1px] h-8 bg-gradient-to-b from-transparent via-cyan-500/30 to-transparent"></div>

        <!-- 批量处理按钮组 -->
        <div class="flex bg-gradient-to-br from-[#0f0f15] to-[#05050a] rounded-xl border border-cyan-500/20 p-1.5 gap-1 shadow-[0_0_20px_rgba(0,0,0,0.3)]">
<!-- 0. 风格角色档案库 (新增 - 青蓝渐变) -->
          <button
            @click="showNewModal = true"
            class="relative px-5 py-2.5 rounded-lg text-base font-bold transition-all flex items-center gap-2 group overflow-hidden text-cyan-200 hover:text-white hover:bg-gradient-to-r from-sky-900/30 to-blue-900/30"
          >
            <div class="relative z-10 flex items-center gap-2">
              <Users :size="20" class="text-sky-400 group-hover:scale-110 transition-transform" />
              <span>风格角色档案库</span>
            </div>
            <!-- 流光背景 -->
            <div class="absolute inset-0 bg-gradient-to-r from-sky-500/0 via-sky-500/10 to-sky-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-sky-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>

          <div class="w-[1px] bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent my-1"></div>

          <!-- 1. 批量改文 -->
          <button
            @click="isBatchRewriting ? stopBatchRewrite() : batchInferScripts()"
            class="relative px-5 py-2.5 rounded-lg text-base font-bold transition-all flex items-center gap-2 group overflow-hidden"
            :class="[
              isBatchRewriting
                ? 'text-cyan-200 cursor-wait bg-cyan-900/20'
                : 'text-cyan-200 hover:text-white hover:bg-gradient-to-r from-cyan-900/30 to-purple-900/30'
            ]"
          >
            <div class="relative z-10 flex items-center gap-2">
              <Sparkles :size="20" class="text-cyan-400 transition-transform" :class="isBatchRewriting ? 'animate-spin' : 'group-hover:animate-pulse group-hover:scale-110'"/>
              <span v-if="!isBatchRewriting">批量改文</span>
              <span v-else class="font-mono text-cyan-300">处理中 ({{ batchRewriteProgress.current }}/{{ batchRewriteProgress.total }})</span>
            </div>
            <div v-if="isBatchRewriting" class="absolute inset-0 bg-cyan-500/20 transition-all duration-300 ease-linear origin-left" :style="{ width: `${(batchRewriteProgress.current / batchRewriteProgress.total) * 100}%` }"></div>
            <div v-else class="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>

          <div class="w-[1px] bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent my-1"></div>

          <!-- 2. 批量推理提示词 -->
          <button
            @click="isBatchOptimizing ? stopBatchOptimize() : batchInferPrompts()"
            class="relative px-5 py-2.5 rounded-lg text-base font-bold transition-all flex items-center gap-2 group overflow-hidden"
            :class="[
              isBatchOptimizing
                ? 'text-purple-200 cursor-wait bg-purple-900/20'
                : 'text-purple-200 hover:text-white hover:bg-gradient-to-r from-purple-900/30 to-pink-900/30'
            ]"
          >
            <div class="relative z-10 flex items-center gap-2">
              <Wand2 :size="20" class="text-purple-400 transition-transform" :class="isBatchOptimizing ? 'animate-spin' : 'group-hover:rotate-12'"/>
              <span v-if="!isBatchOptimizing">批量推理提示词</span>
              <span v-else class="font-mono text-purple-300">处理中 ({{ batchOptimizeProgress.current }}/{{ batchOptimizeProgress.total }})</span>
            </div>
            <div v-if="isBatchOptimizing" class="absolute inset-0 bg-purple-500/20 transition-all duration-300 ease-linear origin-left" :style="{ width: `${(batchOptimizeProgress.current / batchOptimizeProgress.total) * 100}%` }"></div>
            <div v-else class="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/10 to-purple-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-purple-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>

          <div class="w-[1px] bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent my-1"></div>

          <!-- 3. 批量提取角色 (已修改，点击触发弹窗) -->
          <button
            @click="showOldModal= true"
            class="relative px-5 py-2.5 rounded-lg text-base font-bold text-pink-200 hover:text-white hover:bg-gradient-to-r from-pink-900/30 to-rose-900/30 transition-all flex items-center gap-2 group overflow-hidden"
          >
            <div class="relative z-10 flex items-center gap-2">
              <Users :size="20" class="text-pink-400 group-hover:scale-110 transition-transform" />
              <span>批量提取角色</span>
            </div>
            <!-- 流光背景 -->
            <div class="absolute inset-0 bg-gradient-to-r from-pink-500/0 via-pink-500/10 to-pink-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-pink-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>

          <!-- 批量视频生成 -->
          <button
            @click="isBatchGenerating ? stopBatchGenerate() : batchGenerateVideos()"
            class="relative px-6 py-3 rounded-xl text-base font-bold transition-all duration-300 group overflow-hidden flex items-center gap-2"
            :class="[
              isBatchGenerating
                ? 'bg-purple-900/40 text-purple-300 cursor-wait border border-purple-500/20'
                : 'text-purple-200 hover:text-white hover:bg-gradient-to-r from-purple-900/40 to-indigo-900/40'
            ]"
          >
            <div class="relative z-10 flex items-center gap-3">
              <Video :size="30" class="transition-transform duration-300" :class="isBatchGenerating ? 'animate-pulse text-purple-400' : 'text-purple-400 group-hover:text-purple-300 group-hover:scale-110 group-hover:-rotate-6'"/>
              <span v-if="!isBatchGenerating">批量视频生成</span>
              <span v-else class="font-mono text-purple-300 text-xl font-bold">生成中 ({{ batchGenerateProgress.current }}/{{ batchGenerateProgress.total }})</span>
            </div>
            <div v-if="!isBatchGenerating" class="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-400/20 to-purple-500/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out"></div>
            <div v-if="!isBatchGenerating" class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-purple-400 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-[0.5px]"></div>
            <div v-if="!isBatchGenerating" class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 shadow-[0_0_20px_rgba(168,85,247,0.15)_inset]"></div>
          </button>
        </div>

        <!-- 导出按钮 -->
        <button class="relative p-3 rounded-xl border border-cyan-500/20 hover:border-cyan-400/40 bg-gradient-to-br from-[#111118] to-[#0a0a12] text-cyan-300 hover:text-white hover:bg-gradient-to-br hover:from-[#1a1a2a] hover:to-[#0f0f1a] transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.3)] group/export" title="导出工程">
          <Download :size="20" class="group-hover/export:translate-y-[-2px] transition-transform" />
          <div class="absolute -inset-1 bg-gradient-to-r from-cyan-500/0 to-cyan-500/20 rounded-xl blur-sm opacity-0 group-hover/export:opacity-100 transition-opacity duration-500"></div>
        </button>

      </div>
    </header>

    <!-- ================= 主体内容区 ================= -->
    <div class="flex-1 flex overflow-hidden relative z-10">
      <!-- ... (左侧分镜列表和右侧预览保持不变) ... -->
       <!-- ================= 左侧：创作输入区 ================= -->
      <div class="w-1/2 h-full flex flex-col border-r border-white/5 bg-gradient-to-b from-[#0f0f15]/90 via-[#0a0a10]/80 to-[#0f0f15]/90 backdrop-blur-xl relative z-10 transition-all duration-300">
        <!-- 工具栏 -->
        <div class="h-14 px-6 border-b border-white/5 flex items-center justify-between shrink-0 bg-gradient-to-r from-[#111118]/90 to-[#0a0a12]/90 relative">
         <div class="flex items-center gap-4 select-none">
          <!-- 图标容器 -->
          <div class="relative flex items-center justify-center group/icon">
            <div class="absolute -inset-3 bg-cyan-500/20 blur-md rounded-full group-hover/icon:bg-cyan-400/30 transition-colors duration-500"></div>
            <List :size="36" class="relative z-10 text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] group-hover/icon:scale-110 transition-transform duration-300" />
          </div>

          <!-- 标题 -->
          <span class="text-3xl font-black bg-gradient-to-r from-cyan-200 via-purple-200 to-cyan-200 bg-[length:200%_auto] animate-gradient-flow bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(34,211,238,0.25)] tracking-wider">
            二创动态漫：{{ projectName || '未命名' }} ({{ clips.length }})
          </span>
        </div>

          <div class="flex items-center gap-3">
            <span class="text-[18px] font-bold text-gray-500 font-mono bg-[#05050a] px-2 py-1 rounded-lg border border-white/5">TOTAL: {{ clips.length }} SCENES</span>
            <button @click="appendClip" class="relative p-2.5 rounded-xl bg-gradient-to-br from-cyan-900/30 to-cyan-700/20 border border-cyan-500/20 hover:border-cyan-400/40 text-cyan-300 hover:text-white transition-all duration-300 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)] group/add" title="在底部添加分镜">
              <Plus :size="18" class="group-hover/add:rotate-90 transition-transform duration-300"/>
              <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 opacity-0 group-hover/add:opacity-100 transition-opacity duration-500"></div>
            </button>
          </div>

          <!-- 工具栏发光底边 -->
          <div class="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent"></div>
        </div>

        <!-- 分镜卡片列表 -->
        <div class="flex-1 overflow-y-auto custom-scroll p-6 space-y-5">
          <div
            v-for="(clip, index) in clips"
            :key="clip.id"
            @click="selectClip(index)"
            :class="[
              'relative rounded-2xl border-2 transition-all duration-500 p-5 flex flex-col gap-5 group cursor-pointer transform hover:scale-[1.005]',
              activeClipIndex === index
                ? 'bg-gradient-to-br from-cyan-900/20 via-[#111118]/90 to-purple-900/20 border-cyan-500/40 shadow-[0_0_30px_rgba(34,211,238,0.15)]'
                : 'bg-gradient-to-br from-[#0a0a10] via-[#0f0f15] to-[#0a0a10] border-white/10 hover:border-cyan-500/30 hover:shadow-[0_0_20px_rgba(34,211,238,0.1)]'
            ]"
          >
            <!-- 选中高亮条 -->
            <div v-if="activeClipIndex === index" class="absolute left-0 top-4 bottom-4 w-1.5 rounded-r-full bg-gradient-to-b from-cyan-400 via-cyan-300 to-cyan-400 shadow-[0_0_15px_#22d3ee]"></div>

            <!-- 卡片霓虹边框效果 -->
            <div v-if="activeClipIndex === index" class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-cyan-500/20 rounded-2xl blur-sm opacity-70 -z-10"></div>

            <!-- 卡片头部 -->
            <div class="flex justify-between items-center border-b border-white/5 pb-3">
              <div class="flex items-center gap-3">
                <span class="text-2xl font-black font-mono bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">
                  {{ String(index + 1).padStart(2, '0') }}
                </span>
                <span class="text-[10px] px-2 py-1 rounded-lg bg-gradient-to-r from-cyan-900/30 to-purple-900/30 text-cyan-300 border border-cyan-500/20">{{ clip.duration.toFixed(1) }}s</span>
              </div>

              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button @click.stop="addClip(index, 0)" class="relative p-2 rounded-lg bg-gradient-to-br from-[#0a0a10] to-[#05050a] border border-cyan-500/20 hover:border-cyan-400/40 text-cyan-300 hover:text-white transition-all hover:shadow-[0_0_10px_rgba(34,211,238,0.2)] group/up">
                  <ArrowUp :size="24" class="group-hover/up:-translate-y-0.5 transition-transform"/>
                </button>
                <button @click.stop="addClip(index, 1)" class="relative p-2 rounded-lg bg-gradient-to-br from-[#0a0a10] to-[#05050a] border border-cyan-500/20 hover:border-cyan-400/40 text-cyan-300 hover:text-white transition-all hover:shadow-[0_0_10px_rgba(34,211,238,0.2)] group/down">
                  <ArrowDown :size="24" class="group-hover/down:translate-y-0.5 transition-transform"/>
                </button>
                <div class="w-[1px] h-4 bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent mx-1"></div>
                <button @click.stop="deleteClip(index)" class="relative p-2 rounded-lg bg-gradient-to-br from-[#0a0a10] to-[#05050a] border border-red-500/20 hover:border-red-400/40 text-red-400 hover:text-red-300 transition-all hover:shadow-[0_0_10px_rgba(239,68,68,0.2)] group/delete">
                  <Trash2 :size="24" class="group-hover/delete:scale-110 transition-transform"/>
                </button>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="space-y-5">
             <!-- 脚本输入 -->
              <div>
                <div class="flex justify-between items-center mb-2 px-1">
                  <div class="flex items-center gap-3">
                    <label class="text-[20px] text-cyan-300/80 font-bold uppercase tracking-wider flex items-center gap-1">
                      <div class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></div>
                      艺术总监：文案分镜师
                    </label>

                    <!-- 切换原文/润色按钮 -->
                    <button
                      v-if="clip.polishedScript"
                      @click="clip.showOriginal = !clip.showOriginal"
                      class="relative group overflow-hidden px-3 py-1.5 rounded-lg bg-gradient-to-br from-[#0a0a12] to-[#05050a] border border-cyan-500/30 hover:border-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.15)] hover:shadow-[0_0_25px_rgba(34,211,238,0.4)] transition-all duration-300 flex items-center gap-2 cursor-pointer active:scale-95"
                    >
                      <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent z-0"></div>
                      <RefreshCw :size="14" class="relative z-10 text-cyan-400 group-hover:text-cyan-200 group-hover:rotate-180 transition-all duration-500 ease-out drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]" />
                      <span class="relative z-10 text-[15px] font-bold tracking-widest uppercase bg-gradient-to-r from-cyan-300 via-white to-cyan-300 bg-[length:200%_auto] animate-gradient-flow bg-clip-text text-transparent drop-shadow-[0_0_2px_rgba(34,211,238,0.5)]">
                        {{ clip.showOriginal ? '查看润色文案' : '查看原文案' }}
                      </span>
                    </button>
                  </div>

                  <button
                    @click.stop="rewriteScript(index)"
                    :disabled="clip.isRewriting"
                    class="relative text-base font-bold flex items-center gap-1.5 transition-all disabled:opacity-50 group/rewrite px-2 py-1 rounded-lg"
                    :class="clip.isRewriting ? 'text-cyan-400' : 'text-cyan-300 hover:text-white'"
                  >
                    <Sparkles :size="20" :class="{'animate-spin': clip.isRewriting, 'group-hover/rewrite:scale-110': !clip.isRewriting}" class="transition-transform"/>
                    {{ clip.isRewriting ? '润色中...' : 'AI 润色文案' }}
                    <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-cyan-500/0 rounded-lg opacity-0 group-hover/rewrite:opacity-100 transition-opacity"></div>
                  </button>
                </div>

                <!-- 原文输入框 -->
                <textarea
                  v-if="clip.showOriginal || !clip.polishedScript"
                  v-model="clip.script"
                  class="w-full h-24 rounded-2xl p-4 resize-none focus:outline-none custom-scroll transition-all duration-500 ease-out text-lg font-bold tracking-widest leading-relaxed text-white placeholder-gray-600 drop-shadow-[0_0_2px_rgba(34,211,238,0.5)] bg-[#020205] border-2 border-cyan-500/40 shadow-[0_0_15px_rgba(34,211,238,0.15),inset_0_0_20px_rgba(34,211,238,0.05)] focus:border-cyan-400 focus:bg-black focus:shadow-[0_0_40px_rgba(34,211,238,0.4),inset_0_0_10px_rgba(34,211,238,0.1)] focus:drop-shadow-[0_0_5px_rgba(34,211,238,1)] caret-cyan-400 selection:bg-cyan-500/30 selection:text-white"
                  :class="clip.isRewriting ? 'border-cyan-400 shadow-[0_0_30px_rgba(34,211,238,0.5)] animate-pulse' : ''"
                  placeholder="请输入您的爆款分镜文案"
                ></textarea>

                <!-- 润色后文案输入框 -->
                <textarea
                  v-else
                  v-model="clip.polishedScript"
                  class="w-full h-24 rounded-2xl p-4 resize-none focus:outline-none custom-scroll transition-all duration-500 ease-out text-lg font-bold tracking-widest leading-relaxed text-emerald-100 placeholder-emerald-600/50 drop-shadow-[0_0_2px_rgba(52,211,153,0.5)] bg-[#020502] border-2 border-emerald-500/40 shadow-[0_0_15px_rgba(52,211,153,0.15),inset_0_0_20px_rgba(52,211,153,0.05)] focus:border-emerald-400 focus:bg-black focus:shadow-[0_0_40px_rgba(52,211,153,0.4),inset_0_0_10px_rgba(52,211,153,0.1)] focus:drop-shadow-[0_0_5px_rgba(52,211,153,1)] caret-emerald-400 selection:bg-emerald-500/30 selection:text-white"
                  placeholder="AI生成结果..."
                ></textarea>
              </div>


              <!-- AI提示词输入 -->
              <div>
                <div class="flex justify-between items-center mb-2 px-1">
                  <label class="text-[20px] text-purple-300/80 font-bold uppercase tracking-wider flex items-center gap-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" style="animation-delay: 0.2s"></div>
                    创意总监：文案推理师
                  </label>
                  <button
                    @click.stop="optimizePrompt(index)"
                    :disabled="clip.isOptimizing"
                    class="relative text-base font-bold flex items-center gap-1.5 transition-all disabled:opacity-50 group/optimize px-2 py-1 rounded-lg"
                    :class="clip.isOptimizing ? 'text-purple-400' : 'text-purple-300 hover:text-white'"
                  >
                    <Wand2 :size="20" :class="{'animate-spin': clip.isOptimizing, 'group-hover/optimize:rotate-12': !clip.isOptimizing}" class="transition-transform"/>
                    {{ clip.isOptimizing ? 'Optimizing...' : 'AI 推理提示词' }}
                    <div class="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/10 to-purple-500/0 rounded-lg opacity-0 group-hover/optimize:opacity-100 transition-opacity"></div>
                  </button>
                </div>
               <textarea
    v-model="clip.prompt"
    class="custom-resize-area w-full h-40 min-h-[6rem] rounded-2xl p-4 pb-8 resize-y focus:outline-none custom-scroll transition-all duration-500 ease-out font-bold text-sm tracking-widest leading-relaxed text-white placeholder-gray-600 drop-shadow-[0_0_2px_rgba(168,85,247,0.5)] bg-[#020205] border-2 border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.15),inset_0_0_20px_rgba(168,85,247,0.05)] focus:border-purple-400 focus:bg-black focus:shadow-[0_0_40px_rgba(168,85,247,0.4),inset_0_0_10px_rgba(168,85,247,0.1)] focus:drop-shadow-[0_0_5px_rgba(168,85,247,1)] caret-purple-400 selection:bg-purple-500/30 selection:text-white"
    :class="clip.isOptimizing ? 'border-purple-400 shadow-[0_0_30px_rgba(168,85,247,0.5)] animate-pulse' : ''"
    placeholder="请输入您的爆款推理描述词"
  ></textarea>
              </div>
            </div>

            <!-- 双槽位媒体区域 -->
            <div class="grid grid-cols-2 gap-4 h-28">
              <!-- 左侧：原视频 -->
              <div class="relative w-full h-full rounded-xl overflow-hidden border border-cyan-500/20 bg-gradient-to-br from-[#0a0a10] to-[#05050a] group/media hover:border-cyan-400/40 transition-all duration-300 hover:shadow-[0_0_15px_rgba(34,211,238,0.1)]">
                <div v-if="clip.originalThumb" class="w-full h-full relative">
                  <video
                    :src="clip.originalThumb"
                    class="w-full h-full object-cover opacity-80 group-hover/media:opacity-100 transition-opacity"
                    muted loop
                    onmouseover="this.play()"
                    onmouseout="this.pause()"
                  ></video>
                  <div class="absolute top-3 left-3 z-20 group/tag cursor-default select-none">
                    <div class="relative flex items-center gap-2 px-3 py-1.5 bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-lg overflow-hidden shadow-[0_0_15px_rgba(34,211,238,0.2)]">
                      <div class="absolute top-0 left-0 w-[2px] h-full bg-cyan-400/50 blur-[2px] animate-scan-fast"></div>
                      <div class="relative flex items-center justify-center w-2 h-2">
                        <div class="absolute inset-0 bg-cyan-400 rounded-full animate-ping opacity-75"></div>
                        <div class="relative w-1.5 h-1.5 bg-cyan-300 rounded-full shadow-[0_0_5px_#22d3ee]"></div>
                      </div>
                      <div class="flex flex-col leading-none">
                        <span class="text-[18px] text-cyan-500/80 font-mono font-bold tracking-widest scale-75 origin-left">SOURCE_RAW</span>
                        <span class="text-[18px] font-bold  text-cyan-100 tracking-wider drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]">
                          分镜原视频
                        </span>
                      </div>
                      <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-400 opacity-50"></div>
                      <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-400 opacity-50"></div>
                    </div>
                  </div>
                  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover/media:opacity-100 transition-opacity flex items-end justify-center pb-3 gap-2">
                    <button class="p-1.5 rounded-lg bg-gradient-to-r from-cyan-900/80 to-cyan-700/60 border border-cyan-500/30 hover:bg-cyan-700/80 text-white hover:scale-110 transition-transform"><Eye :size="18"/></button>
                    <button class="p-1.5 rounded-lg bg-gradient-to-r from-red-900/80 to-red-700/60 border border-red-500/30 hover:bg-red-700/80 text-white hover:scale-110 transition-transform"><Trash2 :size="18"/></button>
                  </div>
                </div>
                <div v-else class="w-full h-full flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-white/5 transition-all border-2 border-dashed border-cyan-500/20 hover:border-cyan-400/40 group/upload">
                  <div class="relative">
                    <Plus :size="30" class="text-cyan-500/60 group-hover/upload:text-cyan-400 transition-colors" />
                    <div class="absolute -inset-3 bg-cyan-500/10 rounded-full blur-sm opacity-0 group-hover/upload:opacity-100 transition-opacity"></div>
                  </div>
                  <span class="text-[20px] text-cyan-500/60 group-hover/upload:text-cyan-300 font-bold transition-colors">上传分镜视频</span>
                </div>
              </div>

              <!-- 右侧：生成视频 -->
              <div class="relative w-full h-full rounded-xl overflow-hidden border border-purple-500/20 bg-gradient-to-br from-[#0a0a10] to-[#05050a] group/media hover:border-purple-400/40 transition-all duration-300 hover:shadow-[0_0_15px_rgba(168,85,247,0.1)]">
                <div v-if="clip.isGenerating" class="absolute inset-0 z-20 bg-gradient-to-br from-purple-900/20 to-purple-700/10 flex flex-col items-center justify-center">
                  <div class="relative w-10 h-10 mb-2">
                    <div class="absolute inset-0 rounded-full border-2 border-t-purple-400 border-r-transparent border-b-purple-500 border-l-transparent animate-spin"></div>
                    <Sparkles :size="16" class="absolute inset-0 m-auto text-purple-400"/>
                  </div>
                <span class="text-2xl font-bold text-purple-400 font-mono animate-pulse mb-2">
                  RENDERING... {{ activeClip.progress }}%
                </span>
                <div class="w-48 h-1.5 bg-gray-800 rounded-full overflow-hidden relative">
                  <div
                    class="h-full bg-gradient-to-r from-purple-500 to-cyan-400 transition-all duration-300 ease-out"
                    :style="{ width: `${activeClip.progress}%` }"
                  ></div>
                </div>

                </div>

              <div v-else-if="clip.generatedThumb" class="w-full h-full relative group/preview">
                  <img
                    :src="clip.coverUrl || clip.generatedThumb"
                    class="w-full h-full object-cover"
                    @error="$event.target.src = 'https://via.placeholder.com/300x200?text=No+Cover'"
                  />
                  <div class="absolute top-3 left-3 z-20 group/tag cursor-default select-none">
                    <div class="relative flex items-center gap-2 px-3 py-1.5 bg-black/60 backdrop-blur-xl border border-purple-500/40 rounded-lg overflow-hidden shadow-[0_0_20px_rgba(168,85,247,0.25)]">
                      <div class="flex flex-col leading-none">
                        <span class="text-[18px] text-purple-400 font-mono font-bold tracking-widest scale-90 origin-left mb-0.5">AI_RENDERED</span>
                        <span class="text-[18px] font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-100 via-white to-purple-200 tracking-wider">动态视频生成</span>
                      </div>
                    </div>
                  </div>

                  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover/preview:opacity-100 transition-opacity flex items-end justify-center pb-3 gap-2">
                    <button class="p-1.5 rounded-lg bg-gradient-to-r from-purple-900/80 to-purple-700/60 border border-purple-500/30 hover:bg-purple-700/80 text-white hover:scale-110 transition-transform"><Play :size="18"/></button>
                    <button @click.stop="generateVideo(index)" class="p-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-purple-500 border border-purple-400/50 hover:from-purple-500 hover:to-purple-400 text-white hover:scale-110 transition-transform" title="重新生成"><RefreshCw :size="18"/></button>
                  </div>
                </div>

                <div v-else class="w-full h-full flex flex-row items-center justify-center gap-0">
                  <button @click.stop="generateVideo(index)" class="flex-1 h-full flex flex-col items-center justify-center gap-2 hover:bg-gradient-to-br hover:from-purple-900/20 hover:to-purple-700/10 transition-all duration-300 border-r border-white/5 group/generate">
                    <div class="relative">
                      <Sparkles :size="24" class="text-purple-400 group-hover/generate:scale-110 transition-transform" />
                      <div class="absolute -inset-3 bg-purple-500/20 rounded-full blur-sm opacity-0 group-hover/generate:opacity-100 transition-opacity"></div>
                    </div>
                    <span class="text-[18px] text-purple-400 font-bold group-hover/generate:text-purple-300 transition-colors">AI 生成</span>
                    <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-purple-400/50 to-transparent opacity-0 group-hover/generate:opacity-100 transition-opacity"></div>
                  </button>

                  <button class="flex-1 h-full flex flex-col items-center justify-center gap-2 hover:bg-gradient-to-br hover:from-cyan-900/20 hover:to-cyan-700/10 transition-all duration-300 group/upload2">
                    <Upload :size="24" class="text-cyan-500/60 group-hover/upload2:text-cyan-300 transition-colors" />
                    <span class="text-[18px] text-cyan-500/60 font-bold group-hover/upload2:text-cyan-300">上传动态视频</span>
                    <div class="absolute -bottom-0.5 left-4 right-4 h-[1px] bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent opacity-0 group-hover/upload2:opacity-100 transition-opacity"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 添加新分镜按钮 -->
          <button @click="appendClip" class="relative w-full py-4 rounded-2xl border-2 border-dashed border-cyan-500/20 text-cyan-400/60 hover:text-cyan-300 hover:border-cyan-400/40 hover:bg-gradient-to-br hover:from-cyan-900/10 hover:to-purple-900/10 transition-all duration-500 text-xs font-bold uppercase tracking-widest flex items-center justify-center gap-3 group/addnew overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-cyan-500/0 -translate-x-full group-hover/addnew:translate-x-full transition-transform duration-700"></div>
            <Plus :size="30" class="group-hover/addnew:rotate-90 transition-transform duration-500" />
            <span>添加新场景</span>
            <div class="absolute -bottom-0.5 left-1/4 right-1/4 h-[1px] bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent opacity-0 group-hover/addnew:opacity-100 transition-opacity"></div>
          </button>

          <div class="h-10"></div>
        </div>
      </div>

      <!-- ================= 右侧：生成与历史 ================= -->
      <div class="flex-1 flex flex-col h-full bg-gradient-to-b from-[#0a0a10]/90 via-[#05050a]/80 to-[#0a0a10]/90 backdrop-blur-xl relative z-10" v-if="activeClip">
        <!-- 上半部分：预览 -->
        <div class="h-[55%] border-b border-white/5 flex flex-col bg-gradient-to-b from-[#0f0f15] to-[#0a0a10]">
          <div class="h-14 px-6 flex items-center justify-between border-b border-white/5 bg-gradient-to-r from-[#111118]/50 to-[#0a0a12]/50">
           <h2 class="text-xl font-black flex items-center gap-4 group/title cursor-default select-none">
              <!-- 图标 -->
              <div class="relative flex items-center justify-center">
                <div class="absolute -inset-3 bg-gradient-to-r from-cyan-500/40 via-purple-500/40 to-cyan-500/40 rounded-full blur-md animate-spin-slow opacity-70"></div>
                <div class="relative z-10 p-1.5 rounded-lg bg-black/50 border border-cyan-500/30 backdrop-blur-sm shadow-[0_0_15px_rgba(34,211,238,0.3)] group-hover/title:scale-110 transition-transform duration-300">
                  <Clapperboard :size="20" class="text-cyan-300 drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]" />
                  <div class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full border border-black animate-pulse shadow-[0_0_8px_#ef4444]"></div>
                </div>
              </div>
              <!-- 标题 -->
              <span class="text-3xl font-black bg-gradient-to-r from-cyan-200 via-purple-200 to-cyan-200 bg-[length:200%_auto] animate-gradient-flow bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(34,211,238,0.25)] tracking-wider">
                YunManGongFangAI：视频总监分镜预览 {{ String(activeClipIndex + 1).padStart(2, '0') }}
              </span>
            </h2>
          </div>

          <div class="flex-1 p-8 flex items-center justify-center gap-8 relative overflow-hidden">
            <!-- 大预览区 (原视频) -->
            <div class="flex-1 aspect-video max-h-full bg-gradient-to-br from-[#05050a] to-black rounded-2xl border-2 border-cyan-500/20 overflow-hidden relative group hover:border-cyan-400/40 hover:shadow-[0_0_30px_rgba(34,211,238,0.2)] transition-all duration-300">
              <div class="absolute top-4 left-4 px-3 py-1 bg-gradient-to-r from-cyan-900/80 to-cyan-700/60 backdrop-blur-sm rounded-lg text-[15px] font-bold text-cyan-200 border border-cyan-500/30 z-10">ORIGINAL</div>
              <video
                v-if="activeClip.originalThumb"
                :src="activeClip.originalThumb"
                class="w-full h-full object-contain opacity-80 group-hover:opacity-100 transition-all"
                controls autoplay loop muted
              ></video>
              <div v-else class="w-full h-full flex flex-col items-center justify-center select-none group/no-ref">
                <div class="flex flex-col items-center gap-3">
                  <span class="text-2xl font-black tracking-widest bg-gradient-to-r from-gray-600 via-cyan-300 to-gray-600 bg-[length:200%_auto] animate-gradient-flow bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(34,211,238,0.2)]">
                    无参考视频
                  </span>
                  <span class="text-[10px] font-mono font-bold tracking-[0.5em] uppercase text-cyan-500/30 group-hover/no-ref:text-cyan-500/50 transition-colors duration-500">
                    NO_REFERENCE_SOURCE
                  </span>
                </div>
              </div>
              <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/0 via-cyan-500/20 to-cyan-500/0 rounded-2xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"></div>
            </div>

            <!-- 箭头 -->
            <div class="flex flex-col items-center gap-2">
              <div class="relative">
                <ArrowRight :size="28" class="text-cyan-400/60" />
                <div class="absolute -inset-4 bg-cyan-500/10 blur-md rounded-full"></div>
              </div>
              <div class="w-0.5 h-12 bg-gradient-to-b from-cyan-500/30 to-transparent"></div>
            </div>

       <!-- 大预览区 (生成) -->
            <div class="flex-1 aspect-video max-h-full bg-gradient-to-br from-[#05050a] to-black rounded-2xl border-2 border-purple-500/20 overflow-hidden relative group shadow-2xl hover:border-purple-400/40 hover:shadow-[0_0_40px_rgba(168,85,247,0.3)] transition-all duration-300">
              <div class="absolute top-4 left-4 px-3 py-1 bg-gradient-to-r from-purple-900/80 to-purple-700/60 backdrop-blur-sm rounded-lg text-[15px] font-bold text-purple-200 border border-purple-500/30 z-10">GENERATED</div>

              <!-- 加载动画 (进度条) -->
              <div v-if="activeClip.isGenerating" class="absolute inset-0 z-20 bg-gradient-to-br from-purple-900/30 to-black/90 flex flex-col items-center justify-center">
                <div class="relative w-16 h-16 mb-4">
                  <div class="absolute inset-0 rounded-full border-2 border-t-purple-400 border-r-purple-500 border-b-purple-300 border-l-purple-600 animate-spin"></div>
                  <Sparkles :size="24" class="absolute inset-0 m-auto text-purple-400 animate-pulse"/>
                </div>
                <span class="text-2xl font-bold text-purple-400 font-mono animate-pulse">
                  RENDERING... {{ activeClip.progress }}%
                </span>
                <div class="mt-4 w-48 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent rounded-full overflow-hidden">
                  <div class="h-full bg-gradient-to-r from-purple-400 to-cyan-400 animate-progress"></div>
                </div>
              </div>

             <div v-else-if="activeClip.generatedThumb" class="w-full h-full relative bg-black rounded-lg overflow-hidden">
                <video
                  v-if="activeClip.generatedThumb.endsWith('.mp4')"
                  :key="activeClip.generatedThumb"
                  :src="activeClip.generatedThumb"
                  :poster="activeClip.coverUrl"
                  class="w-full h-full object-contain"
                  controls
                  preload="auto"
                  playsinline
                ></video>
                <img
                  v-else
                  :src="activeClip.generatedThumb"
                  class="w-full h-full object-cover"
                />
              </div>
              <div v-else class="flex flex-col items-center justify-center mt-[80px] select-none group/waiting">
                <div class="flex flex-col items-center gap-3">
                  <span class="text-2xl font-black tracking-widest bg-gradient-to-r from-gray-600 via-purple-300 to-gray-600 bg-[length:200%_auto] animate-gradient-flow bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                    等待动态视频生成
                  </span>
                  <span class="text-[10px] font-mono font-bold tracking-[0.5em] uppercase text-purple-500/30 group-hover/waiting:text-purple-500/50 transition-colors duration-500">
                    SYSTEM_STANDBY_MODE
                  </span>
                </div>
              </div>
              <div class="absolute -inset-0.5 bg-gradient-to-r from-purple-500/0 via-purple-500/20 to-purple-500/0 rounded-2xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"></div>
            </div>
          </div>
        </div>

        <!-- 下半部分：历史 -->
        <div class="flex-1 bg-gradient-to-b from-[#0a0a10] to-[#05050a] flex flex-col min-h-0 border-t border-white/5">
          <div class="h-12 px-6 flex items-center justify-between border-b border-white/5 bg-gradient-to-r from-[#111118]/50 to-[#0a0a12]/50">
            <span class="text-2xl font-bold text-cyan-300 flex items-center gap-3">
              <div class="relative">
                <History :size="30" class="text-cyan-400" />
                <div class="absolute -inset-2 bg-cyan-500/10 blur-sm rounded-full "></div>
              </div>
              历史版本 (History)
            </span>
            <span class="text-[18px] font-bold text-cyan-300/60 bg-gradient-to-r from-cyan-900/20 to-cyan-700/10 px-3 py-1 rounded-lg border border-cyan-500/20">共 {{ activeClip.history.length }} 个版本</span>
          </div>

          <div class="flex-1 p-8 overflow-y-auto custom-scroll">
            <div v-if="activeClip.history && activeClip.history.length > 0" class="grid grid-cols-4 gap-6">
              <div
                v-for="(hist, idx) in activeClip.history"
                :key="idx"
                @click="applyHistory(hist)"
                class="group relative aspect-video bg-gradient-to-br from-[#0f0f15] to-[#0a0a10] rounded-xl border border-white/5 hover:border-cyan-500/50 overflow-hidden cursor-pointer transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(34,211,238,0.2)] duration-300"
              >
                <video
                  v-if="hist.url.endsWith('.mp4')"
                  :src="hist.url + '#t=0.1'"
                  class="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-300"
                  preload="metadata"
                  muted
                ></video>
                <img
                  v-else
                  :src="hist.url"
                  class="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-300"
                />

                <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                  <div class="absolute bottom-0 left-0 w-full p-3 pt-6">
                    <p class="text-[10px] text-cyan-300 font-mono">{{ hist.time }}</p>
                  </div>
                </div>
                <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/0 via-cyan-500/20 to-cyan-500/0 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10"></div>
                   <div v-if="activeClip.generatedThumb === hist.url" class="absolute inset-0 border-2 border-cyan-400/80 z-10 pointer-events-none rounded-xl box-border">
                    <div class="absolute top-0 right-0 bg-gradient-to-br from-cyan-600 to-cyan-500 text-black text-[9px] font-bold px-2 py-1 rounded-bl-lg shadow-[0_0_10px_rgba(34,211,238,0.5)]">USED</div>
                 </div>
                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div class="p-2 rounded-full bg-gradient-to-r from-cyan-600/80 to-cyan-500/80 backdrop-blur-sm">
                    <Play :size="16" class="text-white" fill="currentColor" />
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="h-full flex flex-col items-center justify-center text-gray-700 opacity-50">
              <div class="relative mb-4">
                <Dices :size="48" class="text-cyan-500/20" />
                <div class="absolute -inset-6 bg-cyan-500/10 blur-lg rounded-full"></div>
              </div>
              <p class="text-sm text-cyan-300/40">暂无历史记录，点击生成开始抽卡</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="flex-1 flex items-center justify-center bg-gradient-to-br from-[#0a0a10] to-[#05050a] backdrop-blur-xl">
        <div class="text-center">
          <div class="relative mb-6">
            <LayoutGrid :size="64" class="text-cyan-500/20 mx-auto" />
            <div class="absolute -inset-8 bg-cyan-500/10 blur-xl rounded-full"></div>
          </div>
          <p class="text-cyan-300/60 font-bold text-lg">请选择左侧分镜</p>
          <p class="text-cyan-500/40 text-sm mt-2">选择分镜以查看详情和预览</p>
        </div>
      </div>
    </div>
<!-- 🔥 统一媒体预览全屏弹窗 (支持图片和视频) -->
<div
  v-if="showPreviewModal"
  class="fixed inset-0 z-[200] bg-black/95 backdrop-blur-xl flex items-center justify-center p-10 animate-fade-in"
  @click="closeImagePreview"
>
  <!-- 关闭按钮 -->
  <button class="absolute top-8 right-8 p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors z-50 group">
    <X :size="32" class="group-hover:scale-110 transition-transform" />
  </button>

  <!-- 内容容器 -->
  <div class="relative max-w-[90%] max-h-[90%] flex flex-col items-center" @click.stop>

    <!-- 情况A: 视频预览 -->
    <div v-if="previewType === 'video'" class="relative rounded-lg overflow-hidden border border-white/10 shadow-[0_0_50px_rgba(249,115,22,0.3)]">
      <video
        :src="previewImageUrl"
        class="max-w-full max-h-[80vh] object-contain"
        controls
        autoplay
      ></video>
      <div class="absolute top-4 left-4 px-3 py-1 bg-black/60 backdrop-blur-md rounded border border-white/10 text-white text-xs font-mono">
        YunManGongFangAI
      </div>
    </div>

    <!-- 情况B: 图片预览 -->
    <img
      v-else
      :src="previewImageUrl"
      class="max-w-full max-h-[90vh] object-contain rounded-lg shadow-[0_0_50px_rgba(34,211,238,0.3)] border border-white/10"
    />
  </div>
</div>
    <!-- ================= 角色管理流光模态框 (新增) ================= -->
    <div v-if="showOldModal" class="absolute inset-0 z-[100] flex items-center justify-center">
      <!-- 1. 背景遮罩 (毛玻璃 + 暗化) -->
      <div @click="showOldModal = false" class="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity duration-300"></div>

      <!-- 2. 主体窗口容器 -->
      <div class="relative w-[90%] h-[85%] max-w-[1400px] group/modal animate-scale-in">

        <!-- 🔥🔥🔥 核心特效：流光旋转边框 🔥🔥🔥 -->
        <!-- 原理：一个比内容稍大的盒子，背景是旋转的渐变，被内容遮住中间，只露出边缘 -->

        <div class="absolute -inset-[1px] rounded-2xl bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 animate-gradient-xy opacity-100"></div>

        <!-- 3. 窗口内容 -->
        <div class="relative w-full h-full bg-[#0a0a0f] rounded-2xl overflow-hidden flex flex-col border border-white/10 shadow-[0_0_50px_rgba(236,72,153,0.3)]">

          <!-- 顶部扫描线装饰 -->
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-pink-500 to-transparent opacity-50"></div>

          <!-- Header -->
          <div class="h-16 shrink-0 border-b border-white/10 bg-gradient-to-r from-[#111118] to-[#0a0a0f] flex items-center justify-between px-6 relative overflow-hidden">
            <!-- 标题区 -->
            <div class="flex items-center gap-4 z-10">
              <div class="p-2 bg-pink-500/10 rounded-lg border border-pink-500/20">
                <Users :size="24" class="text-pink-400" />
              </div>
              <div>
                <h2 class="text-4xl font-black text-white italic tracking-wider">
                  <span class="bg-clip-text text-transparent bg-gradient-to-r from-pink-300 via-purple-300 to-cyan-300">CHARACTER MATRIX</span>
                </h2>
                <span class="text-[18px] font-bold text-gray-400 tracking-[0.3em]">提取人物角色描述词和生成角色ID</span>
              </div>
            </div>

            <!-- 关闭按钮 -->
            <button @click="showOldModal = false" class="group/close p-2 hover:bg-white/5 rounded-full transition-colors z-10">
              <X :size="24" class="text-gray-400 group-hover/close:text-white group-hover/close:rotate-90 transition-transform duration-300" />
            </button>

            <!-- 顶部背景装饰 -->
            <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
          </div>

          <!-- Toolbar -->
          <div class="h-12 border-b border-white/5 bg-[#0f0f15]/50 flex items-center justify-between px-6 backdrop-blur-md z-10">
           <!-- 外层容器保持 flex 不变 -->
            <div class="flex items-center gap-3 text-2xl font-black tracking-wider">

              <!-- 1. 新增：炫酷能量图标 (SVG) -->
              <svg class="w-8 h-8 icon-flow" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="url(#paint0_linear)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="paint0_linear" x1="3" y1="2" x2="21" y2="22" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#FF00CC"/>
                    <stop offset="1" stop-color="#3333FF"/>
                  </linearGradient>
                </defs>
              </svg>

              <!-- 2. 原有标签：只增加了一个类名 explosive-text -->
              <span class="explosive-text">
                {{ projectName || '未命名' }}的作品角色库
              </span>

            </div>
            <div class="flex items-center gap-3 flex-wrap">

            <!-- 1. 提取角色描述词 (赛博紫 - 神秘数据感) -->
            <button
                @click="extractCharacters"
                :disabled="isExtractingCharacters"
                class="group relative px-4 py-2 rounded-lg text-white text-xs font-black overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.6)] border border-white/20 disabled:opacity-50 disabled:cursor-wait"
            >
                <!-- 流光背景 -->
                <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-purple-500 to-violet-600 bg-[length:200%_auto] animate-shine"></div>
                <!-- 内容 -->
                <div class="relative flex font-bold items-center gap-2 z-10">
                    <ScanText v-if="!isExtractingCharacters" :size="20" class="animate-pulse"/>
                    <Sparkles v-else :size="20" class="animate-spin text-yellow-300"/>
                    <span class="relative flex font-bold items-center gap-2 z-10" >
                        {{ isExtractingCharacters ? '正在提取...' : '批量提取角色' }}
                    </span>
                </div>
            </button>

<!-- 2. 批量生成角色图片按钮 (高亮美化版) -->
<button
  @click="isBatchGeneratingImages ? stopBatchGenerateImages() : batchGenerateImages()"
  class="relative px-5 py-2.5 rounded-lg text-xs font-black transition-all duration-300 flex items-center gap-2 group overflow-hidden border shadow-lg"
  :class="[
    isBatchGeneratingImages
      ? 'bg-[#1a0510] border-pink-500/30 text-pink-300 cursor-wait'
      : 'bg-gradient-to-r from-pink-600 via-fuchsia-600 to-pink-600 bg-[length:200%_auto] border-pink-400/30 text-white hover:animate-shine hover:shadow-[0_0_25px_rgba(236,72,153,0.6)] hover:border-pink-300/50 hover:scale-105'
  ]"
>
  <!-- 进度条背景层 (仅在运行时显示) -->
  <div
    v-if="isBatchGeneratingImages"
    class="absolute inset-0 bg-gradient-to-r from-pink-600 to-fuchsia-600 transition-all duration-300 ease-linear origin-left z-0 opacity-80"
    :style="{ width: `${(batchImageProgress.current / batchImageProgress.total) * 100}%` }"
  ></div>

  <!-- 内容层 -->
  <div class="relative z-10 flex items-center gap-2">
    <!-- 图标 -->
    <Sparkles
      :size="16"
      class="transition-transform duration-500"
      :class="[
        isBatchGeneratingImages
          ? 'animate-spin text-white'
          : 'text-yellow-200 group-hover:rotate-12 group-hover:scale-110'
      ]"
    />

    <!-- 文字 -->
    <span v-if="!isBatchGeneratingImages" class="drop-shadow-md">批量生成图片</span>
    <span v-else class="font-mono text-white drop-shadow-md">
      生成中 ({{ batchImageProgress.current }}/{{ batchImageProgress.total }})
    </span>
  </div>

  <!-- 仅在非生成状态显示的流光高光 -->
  <div v-if="!isBatchGeneratingImages" class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>
</button>

<!-- 3. 生成角色视频 (已恢复熔岩橙流光样式) -->
<button
  @click="isBatchGeneratingCharVideos ? stopBatchCharVideos() : batchGenerateCharacterVideos()"
  class="group relative px-4 py-2 rounded-lg text-xs font-black overflow-hidden transition-all border shadow-lg"
  :class="[
    isBatchGeneratingCharVideos
      ? 'bg-[#1a0a05] border-orange-500/30 text-orange-300 cursor-wait'
      : 'text-white border-white/20 hover:scale-105 hover:shadow-[0_0_20px_rgba(249,115,22,0.6)]'
  ]"
>
  <!-- 🔥 1. 恢复：正常状态下的橙色流光背景 -->
  <div
    v-if="!isBatchGeneratingCharVideos"
    class="absolute inset-0 bg-gradient-to-r from-orange-600 via-red-500 to-orange-600 bg-[length:200%_auto] animate-shine animation-delay-1000"
  ></div>

  <!-- 2. 加载时的进度条背景 -->
  <div
    v-if="isBatchGeneratingCharVideos"
    class="absolute inset-0 bg-gradient-to-r from-orange-900 to-red-900 transition-all duration-300 ease-linear origin-left z-0 opacity-80"
    :style="{ width: `${(batchCharVideoProgress.current / batchCharVideoProgress.total) * 100}%` }"
  ></div>

  <!-- 3. 按钮内容 -->
  <div class="relative flex items-center gap-2 z-10">
    <Clapperboard
      :size="14"
      :class="isBatchGeneratingCharVideos ? 'animate-spin' : 'group-hover:animate-bounce'"
    />
    <span v-if="!isBatchGeneratingCharVideos">批量生成视频</span>
    <span v-else class="font-mono">
      生成中 ({{ batchCharVideoProgress.current }}/{{ batchCharVideoProgress.total }})
    </span>
  </div>
</button>

  <!-- 4. 生成角色ID (极光青 - 精准连接感) -->
  <button
    @click="batchMatchCharacterIds"
    class="group relative px-4 py-2 rounded-lg text-white text-xs font-black overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(6,182,212,0.6)] border border-white/20"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-cyan-600 via-sky-500 to-cyan-600 bg-[length:200%_auto] animate-shine animation-delay-1500"></div>
    <div class="relative flex items-center gap-2 z-10">
      <Fingerprint :size="14"/>
      <!-- 根据状态显示文字 -->
      <span>{{ isMatchingIds ? '匹配中...' : '生成角色ID' }}</span>
    </div>
  </button>

  <!-- 5. 新增角色 (翡翠绿 - 成功生命感) -->
  <button
    @click="addNewCharacter"
    class="group relative px-4 py-2 rounded-lg text-white text-xs font-black overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(16,185,129,0.6)] border border-white/20"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-emerald-600 via-green-500 to-emerald-600 bg-[length:200%_auto] animate-shine"></div>
    <div class="relative flex items-center gap-2 z-10">
      <PlusCircle :size="14" class="group-hover:rotate-90 transition-transform"/>
      <span>新增角色</span>
    </div>
  </button>

  <!-- 6. 清除全部 (警示红 - 危险毁灭感) -->
  <button
    @click="clearAllCharacters"
    class="group relative px-4 py-2 rounded-lg text-white text-xs font-black overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_20px_rgba(225,29,72,0.6)] border border-white/20"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-rose-600 via-red-600 to-rose-600 bg-[length:200%_auto] animate-shine"></div>
    <div class="relative flex items-center gap-2 z-10">
      <Trash2 :size="14" class="group-hover:shake"/>
      <span>清除全部</span>
    </div>
  </button>

</div>
          </div>
<!-- 🔥 1. 添加隐藏的文件上传控件 (放在 table 外面即可) -->
<input
  type="file"
  ref="fileInputRef"
  accept="image/*"
  class="hidden"
  @change="handleFileUpload"
/>
          <!-- 🔥 新增：视频上传隐藏控件 -->
<input
  type="file"
  ref="videoInputRef"
  accept="video/*"
  class="hidden"
  @change="handleVideoUpload"
/>
          <!-- Table Content (Scrollable) -->
          <div class="flex-1 overflow-y-auto custom-scroll relative bg-[#05050a]">
             <!-- 背景网格 -->
            <div class="absolute inset-0 z-0 opacity-20 pointer-events-none"
                 style="background-image: linear-gradient(#1f2937 1px, transparent 1px), linear-gradient(90deg, #1f2937 1px, transparent 1px); background-size: 40px 40px;">
            </div>

            <table class="w-full text-left border-collapse relative z-10">
              <thead class="sticky top-0 z-20 bg-[#0f0f15] shadow-lg text-xs uppercase font-mono text-gray-500 tracking-wider">
                <tr>
                  <th class="p-4 border-b border-white/10 w-16 text-center">
                    <button @click="toggleAll" class="text-pink-500 hover:text-pink-400 transition-colors">
                      <CheckSquare v-if="isAllChecked" :size="20"/>
                      <Square v-else :size="20"/>
                    </button>
                  </th>
<th class="p-4 border-b text-xl font-bold text-white border-white/10 w-32">标签名</th>
<th class="p-4 border-b text-xl text-white border-white/10">人物特征 / 内容</th>
<th class="p-4 border-b text-xl text-white border-white/10 w-32 text-center">图像</th>
<th class="p-4 border-b text-xl text-white border-white/10 w-32 text-center">视频</th>
<th class="p-4 border-b text-xl text-white border-white/10 w-24 text-center">Name</th>
<th class="p-4 border-b text-xl text-white border-white/10 w-48 text-center">操作</th>
                </tr>
              </thead>
              <tbody class="text-sm">
                <!-- 修复了这里的 tr 标签语法错误 -->
                <tr
                  v-for="(char, index) in characterList"
                  :key="char.id"
                  class="group border-b border-white/5 hover:bg-white/[0.02] transition-colors relative"
                >

                  <!-- Checkbox -->
                  <td class="p-4 text-center">
                     <button @click="char.checked = !char.checked" :class="char.checked ? 'text-pink-500' : 'text-gray-600'">
                      <CheckSquare v-if="char.checked" :size="18"/>
                      <Square v-else :size="18"/>
                    </button>
                  </td>
                  <!-- Label (已修改为输入框) -->
                  <td class="p-4">
                    <input
                      v-model="char.label"
                      class="w-full bg-transparent border-b border-transparent focus:border-pink-500 text-white  font-bold  outline-none py-1 transition-colors focus:bg-white/5 px-1"
                      placeholder="输入标签"
                    />
                  </td>

                  <!-- Description (已修改为文本域) -->
                  <td class="p-4">
                    <textarea
                      v-model="char.description"
                      class="w-full h-24 bg-transparent border border-transparent focus:border-white/20 rounded p-2 text-xs text-gray-300 resize-none outline-none custom-scroll focus:bg-white/5 transition-colors leading-relaxed"
                      placeholder="输入人物特征描述..."
                    ></textarea>
                  </td>

                  <!-- Image -->
                 <!-- 🔥 2. 修改图像列 -->
<!-- 🔥 图像列：包含上传/预览/删除/替换逻辑 -->
<!-- 🔥 图像列：包含上传/预览/删除/替换逻辑 -->
<td class="p-4">
  <!-- 状态 A: 没有图片 -> 显示上传按钮 -->
  <div
    v-if="!char.image"
    @click="triggerUpload(char)"
    class="w-20 h-20 mx-auto rounded-lg border-2 border-dashed border-white/20 hover:border-pink-500/50 hover:bg-white/5 flex flex-col items-center justify-center gap-1 cursor-pointer transition-all group/upload-btn"
  >
    <Upload :size="20" class="text-gray-500 group-hover/upload-btn:text-pink-400 transition-colors" />
    <span class="text-[10px] text-gray-500 group-hover/upload-btn:text-pink-300 font-bold">上传</span>
  </div>

  <!-- 状态 B: 有图片 -> 显示图片 + 悬停操作栏 (点击容器本身 = 替换图片) -->
  <div
    v-else
    @click="triggerUpload(char)"
    class="w-20 h-20 mx-auto rounded-lg border border-white/10 overflow-hidden relative group/img bg-black cursor-pointer"
  >
    <!-- 图片本体 -->
    <img :src="char.image" class="w-full h-full object-cover" />

    <!-- 悬停遮罩 (操作栏) -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-[2px] opacity-0 group-hover/img:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center gap-2">

      <!-- 按钮组：预览和删除 (必须加 .stop 防止触发外层的替换上传) -->
      <div class="flex items-center gap-3">
        <!-- 预览按钮 -->
        <button
          @click.stop="openImagePreview(char.image)"
          class="p-1.5 rounded-full bg-white/10 hover:bg-cyan-500/80 text-white transition-all hover:scale-110"
          title="预览大图"
        >
          <Eye :size="16" />
        </button>

        <!-- 删除按钮 -->
        <button
          @click.stop="removeCharacterImage(char)"
          class="p-1.5 rounded-full bg-white/10 hover:bg-red-500/80 text-white transition-all hover:scale-110"
          title="删除图片"
        >
          <Trash2 :size="16" />
        </button>
      </div>

      <!-- 底部文字提示，告知用户点击空白处可替换 -->
      <span class="text-[9px] text-gray-400 font-bold tracking-wider group-hover/img:text-white transition-colors">
        点击替换
      </span>

    </div>
  </div>
</td>

              <!-- Video / 视频列 (已统一交互格式：预览/替换/删除) -->
<td class="p-4">
  <!-- 状态 A: 无视频 -> 显示上传虚线框 -->
  <div
    v-if="!char.video"
    @click="triggerVideoUpload(char)"
    class="w-24 h-20 mx-auto rounded-lg border-2 border-dashed border-white/20 hover:border-orange-500/50 hover:bg-white/5 flex flex-col items-center justify-center gap-1 cursor-pointer transition-all group/vid-upload"
  >
    <Video :size="20" class="text-gray-500 group-hover/vid-upload:text-orange-400 transition-colors" />
    <span class="text-[10px] text-gray-500 group-hover/vid-upload:text-orange-300 font-bold">上传视频</span>
  </div>

  <!-- 状态 B: 有视频 -> 显示缩略预览 + 悬停操作栏 -->
  <div
    v-else
    class="w-24 h-20 mx-auto rounded-lg border border-white/10 overflow-hidden relative group/vid bg-black cursor-pointer"
  >
    <!-- 视频本体 (小窗静音循环播放) -->
    <video
      :src="char.video"
      class="w-full h-full object-cover opacity-80 group-hover/vid:opacity-100 transition-opacity"
      muted
      loop
      onmouseover="this.play()"
      onmouseout="this.pause()"
    ></video>

    <!-- 悬停操作遮罩 (统一风格) -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-[2px] opacity-0 group-hover/vid:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2">

      <!-- 1. 预览按钮 (新加：Eye图标) -->
      <button
        @click.stop="openVideoPreview(char.video)"
        class="p-1.5 rounded-full bg-white/10 hover:bg-cyan-500/80 text-white transition-all hover:scale-110 border border-white/5"
        title="全屏预览"
      >
        <Eye :size="14" />
      </button>

      <!-- 2. 替换按钮 (新加：Upload图标) -->
      <button
        @click.stop="triggerVideoUpload(char)"
        class="p-1.5 rounded-full bg-white/10 hover:bg-orange-500/80 text-white transition-all hover:scale-110 border border-white/5"
        title="替换视频"
      >
        <Upload :size="14" />
      </button>

      <!-- 3. 删除按钮 (保持：Trash2图标) -->
      <button
        @click.stop="removeCharacterVideo(char)"
        class="p-1.5 rounded-full bg-white/10 hover:bg-red-500/80 text-white transition-all hover:scale-110 border border-white/5"
        title="删除视频"
      >
        <Trash2 :size="14" />
      </button>
    </div>
  </div>
</td>

                  <!-- Type -->
                 <!-- 原来的 Type 列位置，现在改成 Name 列 -->
<!-- Name 列 (已改为可点击链接) -->
<td class="p-4 text-center">
  <!-- 如果有名字 -->
  <div v-if="char.name" class="flex flex-col items-center justify-center">

    <!-- 1. 名字显示 (如果是链接则跳转) -->
    <a
      v-if="char.link"
      :href="char.link"
      target="_blank"
      class="font-mono text-cyan-300 font-bold text-sm bg-cyan-900/20 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20 hover:text-white hover:border-cyan-400 transition-all cursor-pointer flex items-center gap-1 group/link"
      title="点击跳转到 Sora 角色主页"
    >
      {{ char.name.startsWith('@') ? char.name : '@' + char.name }}
      <ExternalLink :size="10" class="opacity-50 group-hover/link:opacity-100"/>
    </a>

    <!-- 2. 如果没链接只显示名字 -->
    <span
      v-else
      class="font-mono text-cyan-300 font-bold text-sm bg-cyan-900/20 px-2 py-1 rounded border border-cyan-500/30 select-all"
    >
      {{ char.name.startsWith('@') ? char.name : '@' + char.name }}
    </span>

  </div>

  <!-- 如果没有名字 -->
  <div v-else class="flex flex-col items-center gap-1 opacity-30">
    <span class="text-[10px] text-gray-500">Waiting...</span>
    <div class="h-0.5 w-4 bg-gray-600 rounded-full"></div>
  </div>
</td>
<!-- Actions -->
                  <td class="p-4">
                    <div class="flex flex-col gap-2 items-center justify-center">

                       <!-- 1. 保存到角色库 -->
                       <button    @click="saveToLibrary(char)"    class="w-full py-1.5 rounded border border-white/10 bg-white/5 hover:bg-white/10 text-white text-xs transition-colors">
                         保存到角色库
                       </button>

                       <!-- 2. 生成图片按钮 -->
                       <button
                          @click="generateSingleCharacterImage(char)"
                          :disabled="char.isGenerating"
                          class="w-full py-1.5 rounded text-white text-xs font-bold shadow-lg transition-all flex items-center justify-center gap-1 group/btn"
                          :class="[
                            char.isGenerating
                              ? 'bg-pink-900/50 cursor-wait border border-pink-500/20'
                              : 'bg-gradient-to-r from-pink-600 to-rose-600 shadow-pink-900/20 hover:scale-105'
                          ]"
                        >
                          <template v-if="char.isGenerating">
                            <Sparkles :size="12" class="animate-spin text-pink-300" />
                            <span class="text-pink-200">生成中...</span>
                          </template>
                          <template v-else>
                            <Sparkles :size="12" class="group-hover/btn:rotate-12 transition-transform"/>
                            <span>生成图片</span>
                          </template>
                       </button>

                       <!-- 🔥 3. 新增：生成视频按钮 (橙色系) -->
                       <button
                          @click="generateSingleCharacterVideo(char)"
                          :disabled="char.isGeneratingVideo"
                          class="w-full py-1.5 rounded text-white text-xs font-bold shadow-lg transition-all flex items-center justify-center gap-1 group/btn-vid"
                          :class="[
                            char.isGeneratingVideo
                              ? 'bg-orange-900/50 cursor-wait border border-orange-500/20'
                              : 'bg-gradient-to-r from-orange-500 to-red-500 shadow-orange-900/20 hover:scale-105'
                          ]"
                        >
                          <template v-if="char.isGeneratingVideo">
                            <Clapperboard :size="12" class="animate-spin text-orange-200" />
                            <span class="text-orange-100">渲染中...</span>
                          </template>
                          <template v-else>
                            <Clapperboard :size="12" class="group-hover/btn-vid:scale-110 transition-transform"/>
                            <span>生成视频</span>
                          </template>
                       </button>

                       <!-- 4. 编辑/删除 -->
                    <!-- 编辑/删除 按钮组 -->
<div class="flex gap-2 w-full">
  <button class="flex-1 py-1.5 rounded border border-white/10 hover:border-white/30 text-gray-400 hover:text-white transition-colors text-xs flex items-center justify-center">
    编辑
  </button>

  <!-- 🔥 修改这里：绑定删除事件 -->
  <button
    @click="deleteCharacter(index)"
    class="flex-1 py-1.5 rounded bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-400 transition-colors text-xs flex items-center justify-center"
  >
    删除
  </button>
</div>
                    </div>
                  </td>

                  <!-- Row Hover Glow -->
                  <div class="absolute inset-0 border-y border-transparent group-hover:border-pink-500/20 pointer-events-none transition-colors"></div>
                  <div class="absolute left-0 top-0 bottom-0 w-[2px] bg-pink-500 opacity-0 group-hover:opacity-100 transition-opacity shadow-[0_0_10px_#ec4899]"></div>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';

import {
  LayoutGrid, Settings, Download, List, Plus, Trash2, Wand2, ArrowLeft, Trash, CheckSquare, Square, X,
  Upload, Eye, ArrowRight, Video, RefreshCw, Play, History, ArrowUp, ArrowDown, Sparkles, Dices, ChevronDown, Box, Users, Clapperboard, Image as ImageIcon,
  ScanText, PlusCircle, Fingerprint, // 🔥 新增 ScanText
  ExternalLink
} from 'lucide-vue-next';
import CharacterLibraryModal from "./CharacterLibraryModal.vue";

// 1. Props (接收父组件数据)
const props = defineProps<{
  projectId?: string | number;
  projectName?: string;
  // ✅ 修改后：允许 数组 OR 任意类型 (对象)，消除 Vue Warn
  initialClips?: any[] | any;
}>();
const isExtractingCharacters = ref(false);
const emit = defineEmits(['back']); // 声明返回事件

// 2. 接口定义
// 在 <script setup> 顶部附近
interface HistoryItem {
  id: number;
  url: string;
  coverUrl?: string; // ✅ 新增：必须加上这个字段
  time: string;
}

// 修改 Clip 接口，增加 polishedScript 和 showOriginal 字段
interface Clip {
  id: number;
  index: number;
  duration: number;
  script: string;
  polishedScript: string | null; // [新增] 存储润色后的文案
  showOriginal: boolean;         // [新增] 控制显示原文还是润色文案
  prompt: string;
  originalPath: string;
  originalThumb: string | null;
  generatedThumb: string | null;
  coverUrl: string | null;       // ✅ 新增：这是封面图链接
  isGenerating: boolean;
  isRewriting: boolean;
  isOptimizing: boolean;
  history: HistoryItem[];
  progress: number;

}
// 3. 角色数据接口
interface CharacterData {
  id: number;
  checked: boolean;
  label: string;
  description: string;
  image: string | null;
  video: string | null;
  type: string;
  // 状态锁
  isGenerating?: boolean;
  isGeneratingVideo?: boolean;
  isInferring?: boolean;
  // 🔥 新增字段
  name?: string;
  link?: string;
  taskId?: string;

}

// 🔥 关键修复：在 watch 之前先定义 characterList
const characterList = ref<CharacterData[]>([]);

// 🕒 防抖函数 (核心)：防止用户每打一个字都发请求
// 只有当用户停止操作 delay 毫秒后，才会执行 fn
const debounce = (fn: Function, delay: number) => {
  let timeoutId: any;
  return (...args: any[]) => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
};


// ============================================================
// 🛠️ 1. 数据映射层 (核心：解决前后端字段不一致问题)
// ============================================================

// 🔄 [Map 1] 前端 -> 后端 (保存时)
// 作用：将前端复杂的对象转为后端存储的精简 JSON，剔除临时 UI 状态
const mapCharToBackend = (char: any) => {
  return {
    id: char.id,
    label: char.label || '',
    description: char.description || '',
    // 注意：前端叫 image/video，后端存为 image_url/video_url 以符合通用 API 规范
    image_url: char.image || null,
    video_url: char.video || null,
    name: char.name || '',
    link: char.link || '',
    task_id: char.taskId || '',
    checked: char.checked ?? true      // 默认选中
  };
};

// 🔄 [Map 2] 后端 -> 前端 (加载时)
// 作用：从 DAT 读取数据恢复到 UI，必须重置加载锁
const mapBackendToChar = (data: any) => {
  return {
   id: String(data.id || Date.now() + Math.random()),  // ✅ 转换为字符串
    label: data.label || '未命名',
    description: data.description || '',
    // 映射回前端字段
    image: data.image_url || null,
    video: data.video_url || null,
    name: data.name || '',
    link: data.link || '',
    taskId: data.task_id || '',
    checked: data.checked ?? true,

    // ⚡️ 关键：强制重置所有 UI 锁，防止软件打开时按钮卡死
    isGenerating: false,
    isGeneratingVideo: false,
    isInferring: false
  };
};

// ============================================================
// 💾 2. 角色库存储与加载逻辑 (DAT Real-time Save/Load)
// ============================================================

// 💾 保存角色库到后端 (核心保存函数)
const saveCharactersToBackend = async () => {
  if (!props.projectName) return;

  try {
    // 1. 格式转换
    const charsToSave = characterList.value.map(mapCharToBackend);

    // 2. 发送请求
    const response = await fetch('http://127.0.0.1:8000/api/character/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: props.projectName,
        characters: charsToSave
      })
    });

    const res = await response.json();
    if (res.status === 'success') {
      // 可以在这里更新 lastSaveTime 用于 UI 显示
      console.log(`✅ 角色库已自动保存 (${charsToSave.length} 个角色)`);
    } else {
      console.error('❌ 保存角色库失败:', res.msg);
    }
  } catch (e) {
    console.error('❌ 网络错误，保存角色库中断:', e);
  }
};

// 🕒 防抖保存 (避免打字时频繁写入磁盘)
const debouncedCharSave = debounce(saveCharactersToBackend, 1500);

// 📂 加载角色库 (软件启动时调用)
const loadCharactersFromBackend = async () => {
  if (!props.projectName) return;

  try {
    console.log(`📂 正在加载项目 [${props.projectName}] 的角色库...`);
    const response = await fetch(`http://127.0.0.1:8000/api/character/load?project_name=${encodeURIComponent(props.projectName)}`);
    const res = await response.json();

    if (res.status === 'success') {
      const loadedData = res.data;
      if (loadedData && Array.isArray(loadedData) && loadedData.length > 0) {
        characterList.value = loadedData.map(mapBackendToChar);
        console.log(`✅ 成功恢复 ${characterList.value.length} 个角色数据`);
      } else {
        console.log('🆕 未找到角色存档，初始化为空列表');
        characterList.value = [];
      }
    } else {
      console.warn('⚠️ 后端返回非成功状态:', res.msg);
    }
  } catch (e) {
    console.error('❌ 加载角色库异常 (可能是后端未启动或文件损坏):', e);
  }
};


// ============================================================
// 🧬 3. 批量提取角色逻辑 (提取后自动触发保存)
// ============================================================

const extractCharacters = async () => {
  // 1. 获取所有分镜的文案
  const allScripts = clips.value
    .map((c, i) => c.script ? `分镜${i+1}：${c.script}` : '')
    .filter(s => s.trim() !== '')
    .join('\n');

  if (!allScripts) {
    alert("当前没有任何分镜文案可供提取！");
    return;
  }

  isExtractingCharacters.value = true;

  try {
    // 2. 调用后端接口
    const response = await fetch('http://127.0.0.1:8000/extract_characters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: allScripts })
    });

    const resData = await response.json();

    if (resData.status === 'success') {
      if (!resData.data || resData.data.length === 0) {
        alert("未能提取到角色，请检查文案是否包含人物描述。");
      } else {
        console.log("提取原始数据:", resData.data);

        // 3. 数据映射：兼容后端返回的不同字段名
        const newCharacters = resData.data.map((item: any) => ({
          id: String(Date.now() + Math.random()),  // ✅ 转换为字符串
          // 兼容 label/role/name/tag 等多种可能
          label: item.label || item.role || item.name || item.tag || '未命名角色',
          description: item.description || item.content || '',
          image: null,
          video: null,
          name: '',
          link: '',
          taskId: '',
          checked: true,

          // 状态锁初始化
          isGenerating: false,
          isGeneratingVideo: false,
          isInferring: false
        }));

        // 4. 更新列表 (此处为覆盖，如果想保留旧的可以用 [...characterList.value, ...newCharacters])
        characterList.value = newCharacters;

        // 🔥 5. 核心：提取完立即保存，确保刷新后还在！
        await saveCharactersToBackend();

        alert(`提取成功！共找到 ${newCharacters.length} 个角色。`);
      }
    } else {
      alert("提取失败: " + resData.msg);
    }
  } catch (error) {
    console.error("提取角色异常:", error);
    alert("网络请求错误，请检查后端服务是否启动。");
  } finally {
    isExtractingCharacters.value = false;
  }
};

// ============================================================
// 🔄 4. 生命周期与监听 (确保自动运行)
// ============================================================

onMounted(async () => {
  // 初始化原有逻辑...
  initParticles();

  // 1. 加载分镜数据 (原有的)
  const hasSavedClips = await loadFromBackend();
  if (!hasSavedClips && props.initialClips) {
    transformData(props.initialClips);
    saveToBackend();
  }

  // 2. 🔥 加载角色库数据 (新增的核心逻辑)
  // 这行代码确保软件打开时，上次提取的角色会显示出来
  await loadCharactersFromBackend();
});

// 🔥 监听: 角色列表变化 -> 自动保存 (DAT)
// 只要 label, image, video, name 等任何字段变了，或者新增了角色，都会触发保存
watch(
  characterList,
  () => {
    debouncedCharSave();
  },
  { deep: true }
);
// --- 放在 <script setup> 内部 ---


// 保存状态指示器 (用于在UI上显示 "已保存" 或 "保存中...")
const saveStatus = ref<'saved' | 'saving' | 'error'>('saved');
const lastSaveTime = ref('');



// 🔄 数据转换工具：前端格式 -> 后端保存格式
// 主要是为了对齐字段名，前端用 polishedScript，后端存 polished_script 更规范
const mapClipToBackend = (clip: Clip) => {
  return {
    index: clip.index,
    // 文案相关
    script_original: clip.script,
    script_polished: clip.polishedScript,
    prompt: clip.prompt,

    // 视频相关
    video_original: clip.originalPath,     // 本地绝对路径
    video_url: clip.originalThumb,         // 前端预览链接
    video_generated: clip.generatedThumb,  // 生成后的视频链接
    cover_url: clip.coverUrl,              // 封面

    // 历史记录 (完整保存)
    history: clip.history,

    // 状态 (可选，如果你想保存上次是显示原文还是润色文)
    show_original: clip.showOriginal
  };
};

// 🔄 核心修复：重新计算所有分镜的 index
const reindexClips = () => {
  if (!clips.value) return;
  clips.value.forEach((clip, i) => {
    clip.index = i; // 强制将 index 设为当前数组下标
  });
};

// 🔄 数据转换工具：后端加载格式 -> 前端格式 (终极修复版)
const mapBackendToClip = (savedClip: any): Clip => {

  // 1. 智能提取视频本地路径 (兼容 存档字段 和 拆帧字段)
  const rawPath = savedClip.video_original || savedClip.path || '';

  // 2. 智能计算视频预览 URL
  // 如果后端存了 URL 就用存的；没存(比如刚拆帧完)就根据路径算一个
  let finalVideoUrl = savedClip.video_url || '';

  if (!finalVideoUrl && rawPath) {
     try {
        let relativePath = "";
        // 假设路径包含 "Videos"，进行切割
        if (rawPath.includes("Videos")) {
            relativePath = rawPath.split("Videos")[1];
        } else {
            // 兜底：只取文件名
            relativePath = "/" + rawPath.split(/[\\/]/).pop();
        }
        // 统一转为正斜杠
        relativePath = relativePath.replace(/\\/g, "/");

        // 拼接流媒体地址 (端口按你实际的来，通常是8000)
        finalVideoUrl = `http://127.0.0.1:8000/video_storage${relativePath}`;
     } catch (e) {
        console.error("视频路径自动解析失败:", rawPath);
     }
  }

  // 3. 智能计算时长 (兼容 duration 和 start/end)
  let finalDuration = savedClip.duration;
  if (!finalDuration && savedClip.end !== undefined && savedClip.start !== undefined) {
      finalDuration = savedClip.end - savedClip.start;
  }
  if (!finalDuration) finalDuration = 3; // 默认3秒

  // 4. 返回标准 Clip 对象
  return {
    id: Date.now() + Math.random(), // 临时ID
    index: savedClip.index,
    duration: finalDuration,

    // 🔥🔥🔥 核心修复点：同时读取 script_original (存档) 和 subtitle_text (拆帧)
    // 只有这样，第一次加载才会有字！
    script: (savedClip.script_original || savedClip.subtitle_text || '').trim().replace(/\s+/g, '，'),

    polishedScript: savedClip.script_polished || null,
    prompt: savedClip.prompt || '',
    showOriginal: savedClip.show_original ?? true,

    // 🔥 核心修复点：把算好的路径存进去
    originalPath: rawPath,
    originalThumb: finalVideoUrl,

    generatedThumb: savedClip.video_generated || null,
    coverUrl: savedClip.cover_url || null,

    history: savedClip.history || [],

    // 状态重置
    isGenerating: false,
    isRewriting: false,
    isOptimizing: false,
    progress: 0
  };
};


// 💾 核心：保存数据到后端
const saveToBackend = async () => {
  if (!props.projectName) return;

  saveStatus.value = 'saving';

  try {
    // 1. 转换数据格式
    const clipsToSave = clips.value.map(mapClipToBackend);

    // 2. 发送请求
    const response = await fetch('http://127.0.0.1:8000/api/project/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: props.projectName,
        clips: clipsToSave
      })
    });

    const res = await response.json();

    if (res.status === 'success') {
      saveStatus.value = 'saved';
      lastSaveTime.value = new Date().toLocaleTimeString();
      console.log('✅ 项目自动保存成功');
    } else {
      console.error('保存失败:', res.msg);
      saveStatus.value = 'error';
    }
  } catch (e) {
    console.error('网络错误，保存失败', e);
    saveStatus.value = 'error';
  }
};

// 创建一个防抖版本的保存函数 (延迟 1.5 秒执行)
const debouncedAutoSave = debounce(saveToBackend, 1500);

// 📂 核心：从后端加载数据
const loadFromBackend = async () => {
  if (!props.projectName) return;

  try {
    const response = await fetch(`http://127.0.0.1:8000/api/project/load?project_name=${encodeURIComponent(props.projectName)}`);
    const res = await response.json();

    if (res.status === 'success' && res.data && res.data.length > 0) {
      console.log('📂 发现本地存档，正在恢复...');
      clips.value = res.data.map(mapBackendToClip);

      // 🔥🔥🔥 关键修复：加载进来的数据，强行按顺序重置 index
      // 这样即便 json 里全是 0，加载后也会变成 0, 1, 2, 3...
      reindexClips();

      return true;
    }
    return false;
  } catch (e) {
    console.error('加载存档失败:', e);
    return false;
  }
};

// 1. 定义 ref 变量，名字要和模板里的 ref="libraryModalRef" 一样
const libraryModalRef = ref(null);
const clips = ref<Clip[]>([]);
const activeClipIndex = ref(0);
const activeClip = computed(() => clips.value[activeClipIndex.value] || null);
const showPreviewModal = ref(false);
const previewImageUrl = ref('');

// 2. 处理从“角色库弹窗”保存回来的数据
const handleSaveCharacters = (updatedList: any[]) => {
  // 当你在新弹窗里编辑并保存后，更新父组件的列表
  characterList.value = updatedList;
  console.log('角色库数据已更新:', updatedList);
};

// 3. ✨ 核心功能：点击表格里的“保存到角色库”
const saveToLibrary = (char: any) => {
  // A. 校验
  if (!char.description && !char.image) {
    alert("该角色信息为空（无描述或图片），无法保存到档案库！");
    return;
  }

  // B. 打开新弹窗
  showNewModal.value = true;

  // C. 等待弹窗渲染后，调用子组件的方法注入数据
  // nextTick 确保 v-if="showNewModal" 渲染完毕
  setTimeout(() => {
    if (libraryModalRef.value) {
      // 构造数据格式 (映射字段)
      const transferData = {
        tag: char.label || '默认标签',
        name: char.name || `提取角色_${char.id}`,
        desc: char.description || '',
        image: char.image || '',
        video: char.video || ''  // 👈 🔥 必须加上这行！把视频地址传过去
      };

      // 调用子组件暴露的 addCharacterFromGen 方法
      // @ts-ignore
      libraryModalRef.value.addCharacterFromGen(transferData);
    }
  }, 100);
};


// 🔥 3. 新增上传逻辑
const fileInputRef = ref<HTMLInputElement | null>(null);
const targetCharForUpload = ref<any>(null); // 用于记录当前正在给哪个角色传图片

// 🔥 3.1 新增：视频上传逻辑
const videoInputRef = ref<HTMLInputElement | null>(null);
const targetCharForVideoUpload = ref<any>(null);

// A. 触发视频选择框
const triggerVideoUpload = (char: any) => {
  targetCharForVideoUpload.value = char;
  videoInputRef.value?.click();
};

// B. 处理视频文件选中
// B. 处理视频文件选中 (已修复：使用正确的目标对象和 Blob 预览)
const handleVideoUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;

  // 1. 检查是否有文件，以及是否已指定当前要操作的角色对象
  if (input.files && input.files[0] && targetCharForVideoUpload.value) {
    const file = input.files[0];

    // 2. 创建本地 Blob 预览链接 (视频建议用 Blob，速度快，不占内存)
    const previewUrl = URL.createObjectURL(file);

    // 3. 赋值给当前操作角色的 video 字段
    // (之前的代码错误地赋值给了 image 字段，且用了错误的 targetCharForUpload 变量)
    targetCharForVideoUpload.value.video = previewUrl;
  }

  // 4. 清空 input，防止选中同一个视频时不触发 change 事件
  if (input) input.value = '';
};

// C. 删除视频
const removeCharacterVideo = (char: any) => {
  if (confirm("确定要移除这个视频吗？")) {
    char.video = null;
  }
};

// 1. 修复：添加全选相关的计算属性和方法 (消除 isAllChecked 警告)
// ==========================================
const isAllChecked = computed(() => {
  if (characterList.value.length === 0) return false;
  return characterList.value.every(c => c.checked);
});

const toggleAll = () => {
  const newValue = !isAllChecked.value;
  characterList.value.forEach(c => c.checked = newValue);
};

// ==========================================
// 2. 修复：角色视频生成逻辑 (修正参数以解决 422 错误)
// ==========================================
const generateSingleCharacterVideo = async (char: any, silent = false) => {
  // 1. 校验前置条件
  if (!char.image) {
    return alert("请先生成或上传角色图片，才能生成动态视频！");
  }
  if (!char.description) {
    return alert("角色缺少特征描述/内容，无法生成！");
  }

  // 仅在非静默模式下弹窗确认
  if (!silent) {
      if (!confirm(`确定要为角色【${char.label}】生成Sora动态视频吗？...`)) return;
  }

  char.isGeneratingVideo = true;

  try {
    // 2. 🔥 关键修复：确保 character_id 是字符串类型
    const characterId = String(char.id);  // ✅ 强制转换为字符串

    const response = await fetch('http://127.0.0.1:8000/generate_character_video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        character_id: characterId,             // ✅ 修复：确保是字符串
        label: char.label,
        description: char.description,
        image_url: char.image
      })
    });

    // 🔥 关键修改：处理 422 错误，避免显示 undefined
    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error Detail:", errorData);

      let errMsg = "请求失败";
      if (errorData.detail && Array.isArray(errorData.detail)) {
         // FastAPI 422 格式提取
         errMsg = errorData.detail.map((e: any) => `${e.loc.join('.')} - ${e.msg}`).join('\n');
      } else if (errorData.msg) {
         errMsg = errorData.msg;
      }

      alert(`提交任务失败 (Code ${response.status}):\n${errMsg}`);
      char.isGeneratingVideo = false;
      return;
    }

    const res = await response.json();

    if (res.status === 'success' && res.job_id) {
      const jobId = res.job_id;
      console.log(`🚀 视频任务提交成功，Job ID: ${jobId}，开始轮询...`);

      // 3. 开始轮询状态 (每 3 秒一次)
      const pollInterval = setInterval(async () => {
        try {
          // 调用后端查询接口
          const statusRes = await fetch(`http://127.0.0.1:8000/api/character_task_status/${jobId}`);
          const statusData = await statusRes.json();

          console.log(`查询进度 [${char.label}]: ${statusData.status} - ${statusData.msg}`);

          // --- 情况 A: 成功 ---
          if (statusData.status === 'success' || statusData.status === 'completed') {
            clearInterval(pollInterval);
            char.video = statusData.video_url;

            // 🔥🔥🔥 关键：保存任务ID，供"生成角色ID"功能使用
            char.taskId = statusData.external_id;

            char.isGeneratingVideo = false;
            if (!silent) alert(`🎉 角色【${char.label}】动态视频生成成功！`);
            resolve(); // 🔥 需要定义 resolve
          }
          // --- 情况 B: 失败 ---
          else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            char.isGeneratingVideo = false;
            alert(`❌ 生成失败: ${statusData.msg}`);
          }
          // --- 情况 C: 进行中 (pending / processing) ---
          else {
            // 继续等待
          }

        } catch (err) {
          console.error("轮询网络请求出错", err);
        }
      }, 3000);

    } else {
      // 逻辑错误（如 task id 没返回）
      alert(`提交失败: ${res.msg || '未知错误'}`);
      char.isGeneratingVideo = false;
    }

  } catch (e) {
    console.error("提交任务异常:", e);
    alert("网络请求失败，请检查后端服务");
    char.isGeneratingVideo = false;
  }
};


// A. 触发文件选择框
const triggerUpload = (char: any) => {
  targetCharForUpload.value = char; // 记住当前点击的是哪一行
  fileInputRef.value?.click();      // 模拟点击 input
};

// B. 处理文件选中
const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0] && targetCharForUpload.value) {
    const file = input.files[0];

    // ✅ 必须使用 FileReader 转为 Base64
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        // 赋值给当前角色，这样发给后端的才是 data:image... 开头的长字符串
        targetCharForUpload.value.image = e.target.result;
      }
    };
    reader.readAsDataURL(file); // 开始转换
  }

  if (input) input.value = '';
};

// 2. 删除图片逻辑
const removeCharacterImage = (char: any) => {
  if (confirm("确定要移除这张图片吗？")) {
    char.image = null; // 清空图片，UI会自动切回“上传”按钮
  }
};
const previewType = ref<'image' | 'video'>('image');
// 3. 预览图片逻辑
const openImagePreview = (url: string) => {
  previewImageUrl.value = url;
  previewType.value = 'image'; // 标记为图片
  showPreviewModal.value = true;
};
// 2. 新增函数：打开视频预览
const openVideoPreview = (url: string) => {
  previewImageUrl.value = url; // 复用同一个 URL 变量
  previewType.value = 'video'; // 标记为视频
  showPreviewModal.value = true;
};

// 3. 关闭函数 (保持不变，只是重置时也可以重置类型)
const closeImagePreview = () => {
  showPreviewModal.value = false;
  previewImageUrl.value = '';
  previewType.value = 'image'; // 默认重置回图片
};


// ================= 5. 角色图片生成逻辑 (升级版) =================

// 1. 新增：批量生成专用状态变量
const isBatchGeneratingImages = ref(false);
const batchImageProgress = ref({ current: 0, total: 0 });
let batchImageController: AbortController | null = null; // 用于停止任务

// A. 单个生成函数 (保持不变，但增加 signal 支持以便取消)
const generateSingleCharacterImage = async (char: any, signal?: AbortSignal) => {
  if (!char.description) return alert("该角色没有特征描述，无法生成！");

  char.isGenerating = true;

  try {
    const response = await fetch('http://127.0.0.1:8000/generate_character_image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: char.description,
        ratio: "9:16" //
      }),
      signal: signal // 传递取消信号
    });

    const res = await response.json();

    if (res.status === 'success') {
      char.image = res.image_url;
    } else {
      console.error(`生成失败 ID ${char.id}: ${res.msg}`);
    }
  } catch (e: any) {
    if (e.name !== 'AbortError') {
      console.error(e);
    }
  } finally {
    char.isGenerating = false;
  }
};

// B. 停止批量生成
const stopBatchGenerateImages = () => {
  if (batchImageController) {
    batchImageController.abort(); // 发送取消信号
    batchImageController = null;
  }
  isBatchGeneratingImages.value = false;
};

// C. 批量生成函数 (逻辑全面升级)
// C. 批量生成函数 (逻辑修复：跳过已有图片的角色)
const batchGenerateImages = async () => {
  // 1. 筛选目标
  // 条件：已被勾选 + 有描述词 + 【关键】当前没有图片 (!c.image)
  const targetChars = characterList.value.filter(c =>
    c.checked &&
    c.description &&
    !c.image // <--- 新增条件：只生成还没图的角色
  );

  // 2. 各种情况的提示优化
  if (targetChars.length === 0) {
    // 检查一下是不是因为都已有图了
    const checkedCount = characterList.value.filter(c => c.checked).length;
    if (checkedCount > 0) {
       return alert(`已勾选 ${checkedCount} 个角色，但它们要么已有图片，要么缺少描述词。\n批量生成会自动跳过已有图片的角色。`);
    } else {
       return alert("请先勾选需要生成的角色！");
    }
  }

  // 3. 确认弹窗
  if (!confirm(`即将为 ${targetChars.length} 个“无图”角色生成图片，确定继续吗？`)) return;

  // 4. 初始化状态
  isBatchGeneratingImages.value = true;
  batchImageProgress.value = { current: 0, total: targetChars.length };
  batchImageController = new AbortController();

  // 5. 定义单个任务的处理逻辑
  const worker = async (char: any) => {
    if (batchImageController?.signal.aborted) return;

    // 双重检查：防止在等待过程中用户手动上传了图片
    if (!char.image) {
        await generateSingleCharacterImage(char, batchImageController?.signal);
    }

    if (!batchImageController?.signal.aborted) {
      batchImageProgress.value.current++;
    }
  };

  try {
    // 2并发执行
    await asyncPool(2, targetChars, worker);

    if (!batchImageController?.signal.aborted) {
      alert(`批量任务完成！共生成 ${targetChars.length} 张图片。`);
    }
  } catch (err) {
    console.error("批量任务异常中止", err);
  } finally {
    isBatchGeneratingImages.value = false;
    batchImageController = null;
  }
};

// ================= [修正] 批量处理状态 (分离) =================

// 1. 批量改文专用状态
const isBatchRewriting = ref(false);
const batchRewriteProgress = ref({ current: 0, total: 0 });
let batchRewriteController: AbortController | null = null;

// 2. 批量推理提示词专用状态
const isBatchOptimizing = ref(false);
const batchOptimizeProgress = ref({ current: 0, total: 0 });
let batchOptimizeController: AbortController | null = null;

// ================= 3. 角色提取弹窗状态 =================
// 🔵 控制新窗口（全屏炫酷版）
const showNewModal = ref(false);

// 🔴 控制旧窗口（原来的流光边框版）
const showOldModal = ref(false);

// 打开弹窗
const openCharacterModal = () => {
  showCharacterModal.value = true;
};

// 关闭弹窗
const closeCharacterModal = () => {
  showCharacterModal.value = false;
};

// ================= 4. 模拟角色数据 (Mock Data) =================
// 1. 修改接口：增加新的状态锁 (isInferring, isGeneratingVideo)
interface CharacterData {
  id: number;
  checked: boolean;
  label: string;
  description: string;
  image: string | null;
  video: string | null;
  type: string;
  // 状态锁
  isGenerating?: boolean;      // 图片生成中
  isGeneratingVideo?: boolean; // 🔥 新增：视频生成中
  isInferring?: boolean;       // 🔥 新增：推理描述词中
}




// 3. 🔥🔥🔥 核心：数据转换 (配合后端静态挂载) 🔥🔥🔥
const transformData = (data: any) => {
    let rawList = [];
    if (data && Array.isArray(data.clips)) {
        rawList = data.clips;
    } else if (Array.isArray(data)) {
        rawList = data;
    }

    if (!rawList || rawList.length === 0) return;

    clips.value = rawList.map((item: any) => {
        let relativePath = "";
        try {
            if(item.path.includes("Videos")) {
                relativePath = item.path.split("Videos")[1];
            } else {
                relativePath = "/" + item.path.split("\\").pop();
            }
            relativePath = relativePath.replace(/\\/g, "/");
        } catch(e) {
            console.error("路径解析错误", e);
        }

        const streamUrl = `http://127.0.0.1:8000/video_storage${relativePath}`;
        return {
            id: Date.now() + Math.random(),
            index: i,
            duration: (item.end - item.start),
            script: (item.subtitle_text || '').trim().replace(/\s+/g, '，'),
            polishedScript: null,
            showOriginal: true,
            prompt: '',
            originalPath: item.path,
            originalThumb: streamUrl,
            generatedThumb: null,
            coverUrl: null, // ✅ 初始化为空
            isGenerating: false,
            isRewriting: false,
            isOptimizing: false,
            history: [],
           // ✅ 必须显式初始化为 0
            progress: 0
        };
    });

    if (clips.value.length > 0) activeClipIndex.value = 0;
};

// ================= 增强粒子特效逻辑 =================
const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number;

const initParticles = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    const particles: Particle[] = [];
    const particleCount = 120; // 增加粒子数量
    const connectionDistance = 180;
    const mouseDistance = 250;

    let mouse = { x: -1000, y: -1000 };

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    window.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    class Particle {
        x: number;
        y: number;
        vx: number;
        vy: number;
        size: number;
        color: string;
        alpha: number;
        pulseSpeed: number;

        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.8; // 增加速度
            this.vy = (Math.random() - 0.5) * 0.8;
            this.size = Math.random() * 2.5 + 0.5;
            this.alpha = Math.random() * 0.4 + 0.3;
            this.pulseSpeed = Math.random() * 0.02 + 0.01;

            // 霓虹色粒子
            const colors = [
                'rgba(34, 211, 238, ', // cyan
                'rgba(168, 85, 247, ', // purple
                'rgba(236, 72, 153, ', // pink
                'rgba(139, 92, 246, '  // violet
            ];
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // 边界反弹
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            // 脉冲效果
            this.alpha = 0.3 + Math.sin(Date.now() * this.pulseSpeed) * 0.2;

            // 鼠标互动
            const dx = mouse.x - this.x;
            const dy = mouse.y - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < mouseDistance) {
                const forceDirectionX = dx / distance;
                const forceDirectionY = dy / distance;
                const force = (mouseDistance - distance) / mouseDistance;
                // 增加互动强度
                this.vx -= forceDirectionX * force * 0.1;
                this.vy -= forceDirectionY * force * 0.1;
            }
        }

        draw() {
            if (!ctx) return;

            // 粒子发光效果
            ctx.beginPath();
            const gradient = ctx.createRadialGradient(
                this.x, this.y, 0,
                this.x, this.y, this.size * 3
            );
            gradient.addColorStop(0, this.color + '0.8)');
            gradient.addColorStop(1, this.color + '0)');

            ctx.fillStyle = gradient;
            ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
            ctx.fill();

            // 粒子核心
            ctx.beginPath();
            ctx.fillStyle = this.color + this.alpha + ')';
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();

            // 粒子内光
            ctx.beginPath();
            ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.arc(this.x, this.y, this.size * 0.3, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // 初始化粒子
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    const animate = () => {
        // 创建渐变背景
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, 'rgba(10, 10, 15, 0.1)');
        gradient.addColorStop(1, 'rgba(5, 5, 10, 0.1)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            // 粒子连线
            for (let j = i; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < connectionDistance) {
                    ctx.beginPath();
                    const opacity = 1 - distance / connectionDistance;
                    ctx.strokeStyle = `rgba(100, 116, 139, ${opacity * 0.15})`;
                    ctx.lineWidth = 1.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }

            // 鼠标连线高亮
            const dx = mouse.x - particles[i].x;
            const dy = mouse.y - particles[i].y;
            const distMouse = Math.sqrt(dx * dx + dy * dy);
            if (distMouse < connectionDistance * 1.5) {
                ctx.beginPath();
                const opacity = 1 - distMouse / (connectionDistance * 1.5);
                ctx.strokeStyle = particles[i].color + opacity * 0.4 + ')';
                ctx.lineWidth = 2;
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.stroke();
            }
        }

        // 鼠标光晕
        ctx.beginPath();
        const mouseGradient = ctx.createRadialGradient(
            mouse.x, mouse.y, 0,
            mouse.x, mouse.y, 100
        );
        mouseGradient.addColorStop(0, 'rgba(34, 211, 238, 0.3)');
        mouseGradient.addColorStop(1, 'rgba(34, 211, 238, 0)');
        ctx.fillStyle = mouseGradient;
        ctx.arc(mouse.x, mouse.y, 100, 0, Math.PI * 2);
        ctx.fill();

        animationFrameId = requestAnimationFrame(animate);
    };

    animate();
};

// 4. 生命周期
// 在 onMounted 中修改逻辑
onMounted(async () => {
  // 1. 初始化粒子特效 (原有的)
  initParticles();

  // 2. 🔥 尝试加载云端/本地存档
  const hasSavedData = await loadFromBackend();

  // 3. 如果没有存档 (第一次打开)，则使用传入的 props 初始化
  if (!hasSavedData && props.initialClips) {
    console.log('🆕 无存档，使用初始拆帧数据');
    transformData(props.initialClips); // 使用你原有的 transformData 处理 initialClips
    // 初始化后立刻保存一次，建立档案
    saveToBackend();
  }
});

// 🔥 监听器：一旦 clips 发生变化 (改字、生成视频、删分镜)，自动保存
watch(
  clips,
  (newVal) => {
    // 调用防抖保存，避免频繁请求
    debouncedAutoSave();
  },
  { deep: true } // 深度监听：监听数组内部对象的属性变化
);

onUnmounted(() => {
    cancelAnimationFrame(animationFrameId); // 清理动画
});

watch(() => props.initialClips, (newVal) => {
    if (newVal) transformData(newVal);
}, { deep: true });

// 5. 交互逻辑
const selectClip = (index: number) => { activeClipIndex.value = index; };

const addClip = (index: number, offset: number) => {
  const newClip: Clip = {
    id: Date.now() + Math.random(), // 确保 ID 唯一
    index: 0, // 暂时写0，马上会被 reindex 修正
    duration: 3,
    script: '',
    polishedScript: null,
    showOriginal: true,
    prompt: '',
    originalPath: '',
    originalThumb: null,
    generatedThumb: null,
    coverUrl: null,
    isGenerating: false,
    isRewriting: false,
    isOptimizing: false,
    history: [],
    progress: 0
  };

  const targetIndex = index + offset;
  // 插入数组
  clips.value.splice(targetIndex, 0, newClip);

  // 🔥🔥🔥 关键修复：插入后立即重排索引
  reindexClips();

  activeClipIndex.value = targetIndex;
};

const appendClip = () => { addClip(clips.value.length, 0); };

const deleteClip = (index: number) => {
  if(confirm('确定要删除这个分镜吗？')) {
    clips.value.splice(index, 1);

    // 🔥🔥🔥 关键修复：删除后立即重排索引
    reindexClips();

    // 修正当前选中项，防止越界
    if (activeClipIndex.value >= clips.value.length) {
      activeClipIndex.value = Math.max(0, clips.value.length - 1);
    }
  }
};

// 引入需要的变量（如果还没引入）
// import { ref } from 'vue';

// ================= 批量视频生成状态 =================
const isBatchGenerating = ref(false);
const batchGenerateProgress = ref({ current: 0, total: 0 });
let batchGenerateController: AbortController | null = null;

// ==========================================================
// 🔥 核心封装：生成单个分镜视频 (返回 Promise 用于批量控制)
// ==========================================================
// ==========================================================
// 🔥 核心封装：生成单个分镜视频 (支持双端取消)
// ==========================================================
const processClipVideo = (clip: Clip, signal?: AbortSignal): Promise<void> => {
  return new Promise(async (resolve, reject) => {
    if (!clip.prompt || !clip.prompt.trim()) return resolve();
    if (signal?.aborted) return reject(new DOMException('Aborted', 'AbortError'));

    clip.isGenerating = true;
    clip.progress = 0;

    // 用于存储本次任务的 Job ID，以便取消时使用
    let currentJobId: string | null = null;

    // 🔥 定义清理函数
    const cleanup = () => {
      clip.isGenerating = false;
      // 如果已经拿到了 JobID，发送请求告诉后端取消任务
      if (currentJobId) {
        // 使用 fetch 发送取消请求 (不等待结果，fire-and-forget)
        fetch(`http://127.0.0.1:8000/api/cancel_task/${currentJobId}`, {
             method: 'POST',
             keepalive: true // 确保组件卸载也能发出请求
        }).catch(err => console.warn('Cancel request failed', err));
      }
    };

    // 🔥 监听前端取消信号
    const onAbort = () => {
       cleanup();
       reject(new DOMException('Aborted', 'AbortError'));
    };
    signal?.addEventListener('abort', onAbort);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/generate_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: clip.prompt,
          project_id: props.projectId ? String(props.projectId) : 'temp_workspace',
          clip_index: clip.index,
          api_key: "sk-your-api-key"
        }),
        signal: signal
      });

      const data = await res.json();
      if (signal?.aborted) return; // 请求回来时可能已经取消了

      if (data.status === 'success' && data.job_id) {
        currentJobId = data.job_id; // 🔥 保存 Job ID

        // 开始轮询
        const pollInterval = setInterval(async () => {
          if (signal?.aborted) {
             clearInterval(pollInterval);
             signal.removeEventListener('abort', onAbort);
             cleanup(); // 触发取消逻辑
             return;
          }

          try {
            const statusRes = await fetch(`http://127.0.0.1:8000/api/task_status/${currentJobId}`);
            const statusData = await statusRes.json();

            // 如果后端显示已取消（可能由其他端取消），前端也同步停止
            if (statusData.status === 'cancelled') {
                clearInterval(pollInterval);
                clip.isGenerating = false;
                resolve();
                return;
            }

            if (statusData.progress !== undefined) {
               clip.progress = statusData.progress;
            }

            if (statusData.status === 'success') {
              clearInterval(pollInterval);
              signal?.removeEventListener('abort', onAbort);
              clip.progress = 100;

              setTimeout(() => {
                  clip.isGenerating = false;
                  clip.generatedThumb = statusData.video_url;
                  if (statusData.cover_url) clip.coverUrl = statusData.cover_url;

                  // 添加到历史记录
                  clip.history.unshift({
                    id: Date.now(),
                    url: statusData.video_url,
                    coverUrl: statusData.cover_url,
                    time: new Date().toLocaleTimeString()
                  });
                  resolve();
              }, 500);

            } else if (statusData.status === 'failed' || statusData.status === 'error') {
              clearInterval(pollInterval);
              signal?.removeEventListener('abort', onAbort);
              clip.isGenerating = false;
              console.error(`Clip ${clip.index} failed: ${statusData.msg}`);
              resolve();
            }
          } catch (err) {
            // 轮询网络错误忽略，继续下一次
          }
        }, 3000);

      } else {
        signal?.removeEventListener('abort', onAbort);
        cleanup();
        alert(`启动失败: ${data.msg}`);
        resolve();
      }

    } catch (error: any) {
      signal?.removeEventListener('abort', onAbort);
      cleanup();
      if (error.name !== 'AbortError') {
          console.error("API Error:", error);
      }
      resolve();
    }
  });
};

// ================= 交互功能：单个生成按钮 =================
// ✅ 修复：这里只保留这一个 generateVideo 函数
const generateVideo = (index: number) => {
  const clip = clips.value[index];
  if (!clip.prompt) {
    return alert("请先输入提示词！");
  }
  // 单个调用不需要 await
  processClipVideo(clip);
};

// ================= 交互功能：批量视频生成 =================
const stopBatchGenerate = () => {
  if (batchGenerateController) {
    batchGenerateController.abort();
    batchGenerateController = null;
  }
  isBatchGenerating.value = false;
};

const batchGenerateVideos = async () => {
  const targetClips = clips.value.filter(c => c.prompt && c.prompt.trim() !== '' && !c.isGenerating);

  if (targetClips.length === 0) {
    return alert("没有检测到可生成的任务（需要有提示词且未在生成中）！");
  }

  if(!confirm(`即将批量生成 ${targetClips.length} 个视频，这可能需要较长时间，是否继续？`)) {
      return;
  }

  isBatchGenerating.value = true;
  batchGenerateProgress.value = { current: 0, total: targetClips.length };
  batchGenerateController = new AbortController();

  const worker = async (clip: Clip) => {
    if (batchGenerateController?.signal.aborted) return;
    await processClipVideo(clip);
    if (!batchGenerateController?.signal.aborted) {
      batchGenerateProgress.value.current++;
    }
  };

  try {
    // 2并发
    await asyncPool(2, targetClips, worker);

    if (!batchGenerateController?.signal.aborted) {
        alert("批量视频生成完成！");
    }
  } finally {
    isBatchGenerating.value = false;
    batchGenerateController = null;
  }
};


// 单个润色文案逻辑
const rewriteScript = async (index: number) => {
    const clip = clips.value[index];
    if (!clip.script) return alert("请先输入文案");

    clip.isRewriting = true;

    try {
        const response = await fetch('http://127.0.0.1:8000/rewrite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: clip.script })
        });
        const data = await response.json();
        if (data.success) {
            clip.polishedScript = data.data;
            clip.showOriginal = false;
        } else {
            alert("润色失败，请重试");
        }
    } catch (error) {
        console.error("API Error:", error);
        alert("连接服务器失败，请确保 ai_server.py 已运行");
    } finally {
        clip.isRewriting = false;
    }
};

// 单个推理提示词逻辑
const optimizePrompt = async (index: number) => {
    const clip = clips.value[index];
    if (!clip.originalPath) return alert("该分镜没有关联的原视频，无法进行推理！");

    clip.isOptimizing = true;
    try {
        const response = await fetch('http://127.0.0.1:8000/analyze_prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_path: clip.originalPath,
                subtitle_text: clip.script
            })
        });
        const data = await response.json();
        if (data.success) {
            clip.prompt = data.data;
        } else {
            alert(`推理失败: ${data.msg}`);
        }
    } catch (error) {
        console.error("API Error:", error);
        alert("连接服务器失败，请确保后端服务已启动且网络正常。");
    } finally {
        clip.isOptimizing = false;
    }
};

// ✅ 新代码 (替换为这个)
const applyHistory = (hist: HistoryItem) => {
  if (activeClip.value) {
    // 1. 恢复视频地址
    activeClip.value.generatedThumb = hist.url;

    // 2. 恢复封面图 (如果有的话，没有则设为 null)
    // 这行代码是解决“没有封面/黑屏”的关键
    activeClip.value.coverUrl = hist.coverUrl || null;

    // 3. 重置一下状态，防止 UI 卡在生成中
    activeClip.value.isGenerating = false;
    activeClip.value.progress = 100;
  }
};

// ================= [修正] 批量处理逻辑 (增量并发) =================

// 并发控制工具函数
async function asyncPool(poolLimit: number, array: any[], iteratorFn: (item: any) => Promise<any>) {
  const ret: Promise<any>[] = [];
  const executing: Promise<any>[] = [];
  for (const item of array) {
    const p = Promise.resolve().then(() => iteratorFn(item));
    ret.push(p);
    if (poolLimit <= array.length) {
      const e: Promise<any> = p.then(() => executing.splice(executing.indexOf(e), 1));
      executing.push(e);
      if (executing.length >= poolLimit) {
        await Promise.race(executing);
      }
    }
  }
  return Promise.all(ret);
}

// ----------------- 1. 批量改文逻辑 -----------------
const stopBatchRewrite = () => {
  if (batchRewriteController) {
    batchRewriteController.abort();
    batchRewriteController = null;
  }
  isBatchRewriting.value = false;
};

const batchInferScripts = async () => {
  // 筛选：有原文 且 无润色文案
  const targetClips = clips.value.filter(c => c.script && !c.polishedScript);
  if (targetClips.length === 0) return alert("没有检测到需要润色的文案（原文为空或已润色）！");

  isBatchRewriting.value = true;
  batchRewriteProgress.value = { current: 0, total: targetClips.length };
  batchRewriteController = new AbortController();

  const worker = async (clip: Clip) => {
    if (batchRewriteController?.signal.aborted) return;
    clip.isRewriting = true;
    try {
      const response = await fetch('http://127.0.0.1:8000/rewrite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: clip.script }),
        signal: batchRewriteController?.signal
      });
      const data = await response.json();
      if (data.success) {
        clip.polishedScript = data.data;
        clip.showOriginal = false;
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') console.error(`Script error clip ${clip.index}`, err);
    } finally {
      clip.isRewriting = false;
      if (!batchRewriteController?.signal.aborted) {
        batchRewriteProgress.value.current++;
      }
    }
  };

  try {
    await asyncPool(5, targetClips, worker); // 5并发
  } finally {
    isBatchRewriting.value = false;
    batchRewriteController = null;
  }
};

// ----------------- 2. 批量推理提示词逻辑 -----------------
const stopBatchOptimize = () => {
  if (batchOptimizeController) {
    batchOptimizeController.abort();
    batchOptimizeController = null;
  }
  isBatchOptimizing.value = false;
};

const batchInferPrompts = async () => {
  // 筛选：有视频 且 有文案 且 无提示词
  const targetClips = clips.value.filter(c => c.originalPath && c.script && !c.prompt);
  if (targetClips.length === 0) return alert("没有检测到需要推理的分镜（需含视频、文案且未推理）！");

  isBatchOptimizing.value = true;
  batchOptimizeProgress.value = { current: 0, total: targetClips.length };
  batchOptimizeController = new AbortController();

  const worker = async (clip: Clip) => {
    if (batchOptimizeController?.signal.aborted) return;
    clip.isOptimizing = true;
    try {
      const response = await fetch('http://127.0.0.1:8000/analyze_prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            video_path: clip.originalPath,
            subtitle_text: clip.script
        }),
        signal: batchOptimizeController?.signal
      });
      const data = await response.json();
      if (data.success) {
        clip.prompt = data.data;
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') console.error(`Prompt error clip ${clip.index}`, err);
    } finally {
      clip.isOptimizing = false;
      if (!batchOptimizeController?.signal.aborted) {
        batchOptimizeProgress.value.current++;
      }
    }
  };

  try {
    await asyncPool(3, targetClips, worker); // 3并发
  } finally {
    isBatchOptimizing.value = false;
    batchOptimizeController = null;
  }
};
// ================= 6. 批量生成角色视频逻辑 (新增) =================

// 状态变量
const isBatchGeneratingCharVideos = ref(false);
const batchCharVideoProgress = ref({ current: 0, total: 0 });
let batchCharVideoController: AbortController | null = null;

// 停止批量生成
const stopBatchCharVideos = () => {
  if (batchCharVideoController) {
    batchCharVideoController.abort();
    batchCharVideoController = null;
  }
  isBatchGeneratingCharVideos.value = false;
};

// 🔥 核心函数：批量生成角色视频
const batchGenerateCharacterVideos = async () => {
  // 1. 统计勾选总数
  const checkedChars = characterList.value.filter(c => c.checked);

  if (checkedChars.length === 0) {
    return alert("请先勾选需要生成视频的角色！");
  }

  // 2. 核心筛选：必须有 Image 且有 Description，且当前没在生成
  // (也可以加 !c.video 跳过已有视频的，这里暂不加，允许覆盖)
  const targetChars = checkedChars.filter(c =>
    c.image &&           // 🔥 必须有图片
    c.description &&     // 必须有描述
    !c.isGeneratingVideo // 未在生成中
  );

  // 3. 计算被跳过的数量 (无图角色)
  const skippedCount = checkedChars.length - targetChars.length;

  // 4. 校验与提示
  if (targetChars.length === 0) {
    return alert(`已勾选 ${checkedChars.length} 个角色，但它们全部缺少图片或描述！\n\n请先上传或生成图片。`);
  }

  let confirmMsg = `即将为 ${targetChars.length} 个角色生成动态视频。`;
  if (skippedCount > 0) {
    confirmMsg += `\n(已自动跳过 ${skippedCount} 个没有图片的角色)`;
  }
  confirmMsg += `\n\n视频生成耗时较长，确定开始吗？`;

  if (!confirm(confirmMsg)) return;

  // 5. 初始化状态
  isBatchGeneratingCharVideos.value = true;
  batchCharVideoProgress.value = { current: 0, total: targetChars.length };
  batchCharVideoController = new AbortController();

  // 6. 定义单个任务 Worker (封装成 Promise 以便 asyncPool 等待)
  const worker = async (char: any) => {
    if (batchCharVideoController?.signal.aborted) return;

    // 复用 generateSingleCharacterVideo，但要改造一下让它支持 Promise 返回
    // 由于 generateSingleCharacterVideo 原函数里有 alert 且是异步轮询，
    // 这里我们简单包装一下调用，或者为了批量体验，建议改造 generateSingleCharacterVideo 让其支持 silent 模式
    // 这里演示直接调用的逻辑，实际为了并发控制完美，generateSingleCharacterVideo 最好返回 Promise

    // 这里我们手动实现一个不带 alert 的精简版生成逻辑，或者直接调用原函数
    // 为了代码复用，我们直接调用原函数，注意原函数是 async 的
    await generateSingleCharacterVideo(char);

    // 注意：目前的 generateSingleCharacterVideo 内部有轮询，
    // 如果想要 asyncPool 真正等待视频生成完再进行下一个，
    // generateSingleCharacterVideo 需要返回一个 Promise 并在轮询结束 resolve。
    // 如果原函数只是提交任务就返回，那么这里就会瞬间提交所有任务。
    // 假设原函数是“提交即返回”，建议把并发数设为 1，或者接受瞬间提交。

    if (!batchCharVideoController?.signal.aborted) {
      batchCharVideoProgress.value.current++;
    }
  };

  try {
    // 🔥 并发执行：建议设置为 1 或 2，避免同时提交太多长任务给后端
    await asyncPool(1, targetChars, worker);

    if (!batchCharVideoController?.signal.aborted) {
      alert(`批量任务提交完成！\n后台正在生成 ${targetChars.length} 个视频，请留意状态变化。`);
    }
  } catch (err) {
    console.error("批量视频任务异常", err);
  } finally {
    isBatchGeneratingCharVideos.value = false;
    batchCharVideoController = null;
  }
};




// ================= 7. 生成角色ID 逻辑 (并发版 + 智能跳过) =================

const isMatchingIds = ref(false);

const batchMatchCharacterIds = async () => {
  // 1. 获取勾选的角色
  const checkedChars = characterList.value.filter(c => c.checked);

  if (checkedChars.length === 0) {
    return alert("请先勾选需要匹配 ID 的角色！");
  }

  // 2. 核心筛选：
  // (1) 必须有 taskId
  // (2) 必须没有 name，或者 name 不是以 @ 开头的
  const targetChars = checkedChars.filter(c =>
    c.taskId &&
    (!c.name || !c.name.startsWith('@'))
  );

  // 3. 统计被跳过的情况
  const skippedCount = checkedChars.length - targetChars.length;

  if (targetChars.length === 0) {
    // 细分提示
    const alreadyDoneCount = checkedChars.filter(c => c.name && c.name.startsWith('@')).length;
    if (alreadyDoneCount === checkedChars.length) {
      return alert("所选角色都已经拥有角色ID了，无需重复匹配。");
    } else {
      return alert(`已勾选 ${checkedChars.length} 个角色，但无可匹配项。\n\n原因可能是：\n1. 角色已有ID (自动跳过)\n2. 缺少生成任务ID (请先生成视频，且不要刷新页面)`);
    }
  }

  // 4. 确认弹窗
  let confirmMsg = `即将并发匹配 ${targetChars.length} 个角色ID`;
  if (skippedCount > 0) {
    confirmMsg += `\n(已智能跳过 ${skippedCount} 个无需匹配的角色)`;
  }
  confirmMsg += `\n\n确定开始吗？`;

  if (!confirm(confirmMsg)) return;

  isMatchingIds.value = true;

  // 5. 定义单个匹配任务 Worker
  const worker = async (char: any) => {
    try {
      console.log(`🚀 发起匹配请求: ${char.label}`);

      const response = await fetch('http://127.0.0.1:8000/match_character_id', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: char.taskId
        })
      });

      if (!response.ok) {
         console.warn(`❌ 网络请求失败 [${char.label}]: ${response.status}`);
         return;
      }

      const res = await response.json();

       if (res.status === 'success' && res.username) {
        // 赋值名字
        char.name = '@' + res.username;

        // 🔥🔥 核心修改：保存链接到 char 对象 (如果没有 permalink，可以根据 username 拼一个)
        char.link = res.permalink || `https://sora.chatgpt.com/profile/${res.username}`;

        console.log(`✅ 匹配成功: ${char.label} -> ${char.name}`);
      } else {
        console.warn(`⚠️ 匹配未找到 [${char.label}]: ${res.msg}`);
      }
    } catch (err) {
      console.error(`❌ 请求异常 [${char.label}]:`, err);
    }
  };

  try {
    // 🔥🔥 核心修改：使用 asyncPool 实现并发
    // 第一个参数 3 表示同时处理 3 个请求 (建议 3-5，不要太大以免被封)
    await asyncPool(3, targetChars, worker);

    alert("批量匹配流程结束！");

  } catch (e) {
    console.error("并发调度异常", e);
    alert("匹配过程发生错误，请检查控制台");
  } finally {
    isMatchingIds.value = false;
  }
};


// ================= 8. 手动新增角色逻辑 =================

const addNewCharacter = () => {
  // 创建一个空的“手动添加”角色对象
  const newChar: CharacterData = {
    id: Date.now(), // 使用时间戳作为唯一ID
    checked: true,  // 默认勾选，方便后续操作
    label: '',      // 留空让用户填
    description: '',// 留空让用户填
    image: null,
    video: null,
    type: '手动添加',
    // 同时也初始化状态字段，防止报错
    isGenerating: false,
    isGeneratingVideo: false,
    isInferring: false,
    // 初始化匹配ID相关字段
    name: '',
    taskId: ''
  };

  // 添加到列表末尾
  characterList.value.push(newChar);

  // 可选：添加后自动滚动到底部（提升体验）
  setTimeout(() => {
    const tableContainer = document.querySelector('.overflow-y-auto.custom-scroll.relative.bg-\\[\\#05050a\\]');
    if (tableContainer) {
      tableContainer.scrollTop = tableContainer.scrollHeight;
    }
  }, 100);
};

// ================= 9. 删除/清空逻辑 =================

// 1. 删除单个角色
const deleteCharacter = (index: number) => {
  // 防误触提示
  if (!confirm("确定要删除这个角色吗？\n(相关的图片和视频记录也会被移除)")) {
    return;
  }
  // 从数组中移除
  characterList.value.splice(index, 1);
};

// 2. 清空所有角色
const clearAllCharacters = () => {
  if (characterList.value.length === 0) {
    return alert("当前没有角色可清除。");
  }

  // 二次确认，防止误操作毁灭世界
  const confirmed = confirm(
    "⚠️ 高危操作警告 ⚠️\n\n确定要【清空所有】角色数据吗？\n此操作将丢失所有已提取的描述、生成的图片和视频链接，且无法撤销！"
  );

  if (confirmed) {
    characterList.value = [];
  }
};





</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: rgba(10, 10, 15, 0.5); border-radius: 3px; }
.custom-scroll::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, rgba(34, 211, 238, 0.5), rgba(168, 85, 247, 0.5));
  border-radius: 3px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, rgba(34, 211, 238, 0.8), rgba(168, 85, 247, 0.8));
}
/* 文字流光炸裂效果 */
.explosive-text {
  /* 核心：高饱和度渐变色 (红紫-蓝-青-红紫循环) */
  background: linear-gradient(
    110deg,
    #ff0080,
    #7928ca,
    #00dfd8,
    #ff0080
  );

  /* 放大背景以实现流动 */
  background-size: 200% auto;

  /* 裁剪背景到文字 */
  -webkit-background-clip: text;
  background-clip: text;

  /* 文字透明 */
  color: transparent;

  /* 动画：流动 */
  animation: stream-shine 2.5s linear infinite;

  /* 炸裂关键：利用滤镜实现发光，比 text-shadow 更强劲，不会被裁剪遮挡 */
  filter: drop-shadow(0 0 6px rgba(121, 40, 202, 0.6));

  /* 字体加粗与倾斜，增加速度感 */
  font-weight: 900;
  font-style: italic;
}

/* 图标动画效果 */
.icon-flow {
  /* 让图标也有辉光 */
  filter: drop-shadow(0 0 8px rgba(255, 0, 204, 0.6));
  /* 图标轻微跳动，增加炸裂感 */
  animation: icon-pulse 2s ease-in-out infinite;
}

/* 文字流动动画 */
@keyframes stream-shine {
  to {
    background-position: 200% center;
  }
}

/* 图标跳动动画 */
@keyframes icon-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.15) rotate(5deg);
    opacity: 1;
    filter: drop-shadow(0 0 12px rgba(51, 51, 255, 0.9));
  }
}
@keyframes scan {
  0% { top: 0; opacity: 0; }
  100% { top: 100%; opacity: 0; }
}
.animate-scan { animation: scan 2s linear infinite; }

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-shimmer { animation: shimmer 1.5s infinite; }

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-bounce-slow { animation: bounce-slow 2s infinite; }

@keyframes progress {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-progress {
  animation: progress 1.5s ease-in-out infinite;
}

/* 霓虹文字效果 */
.neon-text {
  text-shadow: 0 0 5px rgba(34, 211, 238, 0.8),
               0 0 10px rgba(34, 211, 238, 0.6),
               0 0 15px rgba(34, 211, 238, 0.4);
}

/* 按钮悬停效果 */
.btn-glow:hover {
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.5),
              inset 0 0 20px rgba(34, 211, 238, 0.1);
}

/* 卡片悬停效果 */
.card-hover {
  transition: all 0.3s ease;
}
.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

/* 脉冲动画 */
@keyframes pulse-glow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}

/* ---------------- 模态框流光特效 (新增) ---------------- */

/* 弹窗进入动画 */
@keyframes scale-in {
  0% { opacity: 0; transform: scale(0.95) translateY(20px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-scale-in {
  animation: scale-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

/* 渐变流光背景动画 */
@keyframes gradient-xy {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient-xy {
  background-size: 200% 200%;
  animation: gradient-xy 6s ease infinite;
}

/* 旋转边框特效 */
@keyframes spin-slow-border {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-spin-slow-border {
  /* 使用 conic-gradient 创建旋转的彩色光环 */
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(236, 72, 153, 0.8) 90deg,
    transparent 180deg,
    rgba(34, 211, 238, 0.8) 270deg,
    transparent 360deg
  );
  width: 150%;
  height: 150%;
  position: absolute;
  top: -25%;
  left: -25%;
  z-index: -1;
  animation: spin-slow-border 4s linear infinite;
}
/* =========================================
   🔥🔥🔥 新增：隐藏 Textarea 默认白色拖拽图标
   ========================================= */

/* 针对带有 custom-resize-area 类的文本域 */
.custom-resize-area::-webkit-resizer {
  background-color: transparent; /* 背景变透明 */
  border: none;                  /* 去掉边框 */

  /* 保留点击区域大小，否则鼠标很难抓到右下角 */
  width: 20px;
  height: 20px;
}

/* 隐藏滚动条交接处的背景 */
.custom-resize-area::-webkit-scrollbar-corner {
  background-color: transparent;
}
</style>