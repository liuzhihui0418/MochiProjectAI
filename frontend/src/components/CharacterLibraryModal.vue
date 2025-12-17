<template>
  <!--
    全局容器
  -->
  <div class="fixed inset-0 z-[100] flex items-center justify-center bg-black/10 backdrop-blur-md font-sans animate-fade-in perspective-1000">

    <!-- 关闭触发层 -->
    <div class="absolute inset-0 z-0" @click="$emit('close')"></div>

    <!--
      === 主窗口容器 (完全保留原逻辑) ===
      新增动态类名：当弹窗打开时，主窗口模糊并变暗
    -->
    <div
      class="relative w-full max-w-[1380px] h-[85vh] z-10 flex flex-col group/window select-none transition-all duration-500 ease-out"
      :class="showEditModal ? 'scale-95 opacity-40 blur-[5px] pointer-events-none grayscale-[0.5]' : 'scale-100 opacity-100'"
    >

      <!-- 超级流光边框 (原样保留) -->
      <div class="absolute -inset-2 rounded-2xl bg-gradient-to-r from-transparent via-[#00d1a0] to-transparent bg-[length:250%_100%] animate-border-run blur-xl opacity-70 group-hover/window:opacity-100 transition-opacity duration-500"></div>
      <div class="absolute -inset-[1.5px] rounded-2xl bg-gradient-to-r from-transparent via-[#00ffc3] to-transparent bg-[length:250%_100%] animate-border-run opacity-100 blur-[1px]"></div>

      <!-- 窗口主体 -->
      <div class="flex-1 w-full bg-[#08080c] rounded-2xl overflow-hidden flex flex-col shadow-2xl relative border border-white/5">

        <!-- 内部装饰 -->
        <div class="absolute inset-0 opacity-15 pointer-events-none bg-[linear-gradient(rgba(0,255,160,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,160,0.05)_1px,transparent_1px)] bg-[size:40px_40px]"></div>

        <!-- Header (原样保留) -->
        <header class="relative px-10 py-8 shrink-0 flex items-center justify-between border-b border-white/5 bg-[#08080c]/90 backdrop-blur-xl z-20">
          <div class="flex items-center gap-12">
            <div>
              <h2 class="text-4xl font-black tracking-widest flex items-center gap-4 uppercase italic">
                <div class="w-2 h-10 bg-[#00d1a0] skew-x-[-15deg] shadow-[0_0_20px_#00d1a0] animate-pulse"></div>
                <span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-[#00ffc3] to-white bg-[length:200%_auto] animate-text-flow drop-shadow-[0_0_10px_rgba(0,209,160,0.5)]">
                  风格角色档案库
                </span>
              </h2>
              <p class="text-xl font-bold text-gray-500 tracking-[0.4em] mt-2 pl-6 uppercase opacity-80">
                打造专属于您的风格角色档案库 <span class="text-[#00d1a0] font-bold"></span>
              </p>
            </div>
            <div class="relative flex p-1.5 bg-white/5 rounded-xl border border-white/5 backdrop-blur-md">
              <div class="absolute top-1.5 bottom-1.5 w-[calc(50%-6px)] bg-[#00d1a0] rounded-lg shadow-[0_0_25px_rgba(0,209,160,0.6)] transition-all duration-300 ease-out" :class="currentTab === 'sora' ? 'translate-x-[100%] left-[6px]' : 'left-[6px]'"></div>
              <button @click="currentTab = 'ref'" class="relative z-15 px-100 py-2.5 text-xl font-bold tracking-wider transition-colors duration-300 w-36 text-center" :class="currentTab === 'ref' ? 'text-black' : 'text-gray-400 hover:text-white'">Sora角色库</button>
              <button @click="currentTab = 'sora'" class="relative z-15 px-100 py-2.5 text-xl font-bold tracking-wider transition-colors duration-300 w-36 text-center" :class="currentTab === 'sora' ? 'text-black' : 'text-gray-400 hover:text-white'">Sora风格库</button>
            </div>
          </div>
          <div class="flex items-center gap-6">
            <button @click="addNewCharacter" class="relative px-8 py-3 group overflow-hidden rounded bg-transparent border border-[#00d1a0]/30 hover:border-[#00d1a0] transition-all duration-300 active:scale-95 shadow-[0_0_0_transparent] hover:shadow-[0_0_30px_rgba(0,209,160,0.3)]">
              <div class="absolute inset-0 w-0 bg-[#00d1a0] transition-all duration-300 ease-out group-hover:w-full opacity-10"></div>
              <div class="flex items-center gap-3 relative z-10 text-[#00d1a0] group-hover:text-[#00ffc3] transition-all">
                <Plus :size="20" stroke-width="3" />
                <span class="font-bold tracking-widest text-base group-hover:animate-text-flow bg-gradient-to-r from-[#00d1a0] via-white to-[#00d1a0] bg-[length:200%_auto] bg-clip-text group-hover:text-transparent">新建档案</span>
              </div>
            </button>
            <button @click="$emit('close')" class="group p-3 rounded-full bg-white/5 hover:bg-white/10 hover:text-white transition-all duration-300">
               <X :size="24" class="text-gray-500 group-hover:text-red-400 transition-colors group-hover:rotate-90 duration-500" />
            </button>
          </div>
        </header>

        <!-- 工具栏 (搜索框保留) -->
        <div class="px-10 py-5 flex items-center justify-between bg-[#0e0e14] border-b border-white/5 shadow-inner">
          <div class="flex items-center gap-6 text-xl text-gray-500 font-bold">
             <span class="flex items-center gap-2">
               <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
               系统连接: 稳定
             </span>
             <span class="text-white/10">|</span>
             <span class="flex items-center gap-2">
               角色档案总数据:
               <span class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-t from-[#00d1a0] to-white font-sans drop-shadow-[0_0_5px_rgba(0,209,160,0.8)]">
                 {{ filteredList.length }}条
               </span>
             </span>
          </div>

          <!-- 搜索框 (原样保留) -->
          <div class="relative group w-96">
             <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search :size="18" class="text-gray-600 group-focus-within:text-[#00d1a0] transition-colors" />
             </div>
             <input
               v-model="searchQuery"
               type="text"
               placeholder="输入角色名检索您的角色"
               class="w-full bg-[#15151a] font-bold text-white text-base rounded-lg border border-white/10 pl-11 pr-4 py-2.5 focus:outline-none focus:border-[#00d1a0] focus:shadow-[0_0_30px_rgba(0,209,160,0.2)] transition-all placeholder-gray-600 tracking-wider"
             >
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="flex-1 overflow-y-auto p-10 custom-scroll bg-[#08080c]">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-8">

            <!-- 卡片 Item -->
            <div
              v-for="(char, idx) in filteredList"
              :key="char.id"
              class="group relative aspect-[3/4] bg-[#101014] rounded-xl border border-white/5 cursor-pointer transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_60px_-15px_rgba(0,209,160,0.15)]"
            >
              <div class="absolute inset-0 rounded-xl border border-[#00d1a0]/0 group-hover:border-[#00d1a0]/60 transition-colors duration-500 z-20 box-border"></div>
              <div class="absolute inset-2 overflow-hidden rounded-lg bg-[#050508]">
               <!-- 1. 优先显示图片 -->
  <img
    v-if="char.image"
    :src="char.image"
    class="w-full h-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700 ease-out"
  />

  <!-- 2. 没有图片但有视频 -> 显示视频 (您之前缺了这段) -->
  <video
    v-else-if="char.video"
    :src="char.video"
    class="w-full h-full object-cover opacity-60 group-hover:opacity-100 group-hover:scale-110 transition-all duration-700 ease-out"
    muted loop autoplay playsinline
  ></video>

  <!-- 3. 都没有 -> 显示文字 -->
  <div v-else class="w-full h-full flex items-center justify-center text-gray-700 font-bold text-xs">
    NO MEDIA
  </div>
                <div class="absolute inset-0 bg-gradient-to-b from-transparent via-[#00d1a0]/40 to-transparent h-[15%] w-full -translate-y-full group-hover:animate-scan z-10 pointer-events-none mix-blend-overlay"></div>
                <div class="absolute bottom-0 left-0 right-0 h-2/3 bg-gradient-to-t from-[#08080c] via-[#08080c]/80 to-transparent opacity-90"></div>
              </div>
              <div class="absolute bottom-4 left-4 right-4 z-30">
                <h3 class="text-white font-black text-lg truncate tracking-widest group-hover:text-[#00d1a0] transition-colors duration-300 drop-shadow-md">{{ char.label+char.name }}</h3>
                <p class="text-xs text-gray-500 mt-1 truncate font-bold group-hover:text-gray-300 transition-colors">{{ char.desc }}</p>
                <div class="flex items-center gap-3 mt-0 h-0 opacity-0 group-hover:h-auto group-hover:opacity-100 group-hover:mt-3 transition-all duration-500 overflow-hidden">
                  <!-- EDIT 按钮触发弹窗 -->
                  <button @click.stop="openEditModal(char)" class="flex-1 py-1.5 rounded bg-white/10 hover:bg-[#00d1a0] hover:text-black text-white text-xs font-bold transition-all hover:shadow-[0_0_15px_#00d1a0]">
                    EDIT
                  </button>
                  <button @click.stop="deleteChar(char.id)" class="p-1.5 rounded bg-white/10 hover:bg-red-600 hover:text-white text-white transition-all">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
              <div class="absolute top-0 left-1/2 -translate-x-1/2 w-0 h-[2px] bg-[#00d1a0] shadow-[0_0_15px_#00d1a0] group-hover:w-[60%] transition-all duration-500 delay-100 z-30 rounded-full"></div>
            </div>

            <!-- 添加按钮卡片 -->
            <div
              @click="addNewCharacter"
              class="aspect-[3/4] rounded-xl border-2 border-dashed border-white/10 hover:border-[#00d1a0] hover:bg-[#00d1a0]/5 flex flex-col items-center justify-center gap-4 cursor-pointer group transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,209,160,0.1)]"
            >
              <div class="p-5 rounded-full bg-white/5 group-hover:bg-[#00d1a0] group-hover:text-black transition-all duration-300 group-hover:scale-110 shadow-[0_0_0_rgba(0,209,160,0)] group-hover:shadow-[0_0_40px_rgba(0,209,160,0.8)]">
                <Plus :size="32" stroke-width="3" />
              </div>
              <span class="text-sm text-gray-500 group-hover:text-[#00d1a0] tracking-widest font-black uppercase group-hover:animate-text-flow bg-gradient-to-r from-gray-500 via-white to-gray-500 bg-[length:200%_auto] bg-clip-text group-hover:text-transparent">
                Inject Data
              </span>
            </div>

          </div>

          <!-- 空状态 -->
          <div v-if="filteredList.length === 0" class="h-64 flex flex-col items-center justify-center text-gray-600">
             <SearchX :size="64" class="opacity-30 mb-4 animate-pulse"/>
             <p class="text-lg tracking-[0.5em] font-bold opacity-50">数据丢失 / DATA LOST</p>
          </div>
        </div>
      </div>
    </div>

    <!--
      === 竖向长方形弹窗 (New Edit Modal) ===
      样式：上面短，高度长 w-[500px] h-[80vh]
    -->
     <div v-if="showEditModal" class="fixed inset-0 z-[200] flex items-center justify-center pointer-events-auto font-sans">

    <!-- 遮罩：带一点点噪点和模糊 -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="closeEditModal"></div>

    <!-- 弹窗主体：战术平板风格 -->
    <div class="relative w-[520px] max-h-[90vh] flex flex-col bg-[#050508] rounded-xl overflow-hidden shadow-[0_0_50px_rgba(0,209,160,0.15)] border border-[#00d1a0]/30 animate-slide-up-fade group/modal">

      <!-- 装饰：顶部扫描光效 -->
      <div class="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-[#00d1a0] to-transparent animate-scan-x z-20"></div>

      <!-- ============ HEADER: 紧凑型战术头 ============ -->
      <div class="relative h-16 shrink-0 flex items-center justify-between px-6 border-b border-white/5 bg-[#0a0a0f] z-10">
        <!-- 动态斜纹背景 -->
        <div class="absolute inset-0 opacity-10 bg-[repeating-linear-gradient(45deg,transparent,transparent_5px,#00d1a0_5px,#00d1a0_6px)]"></div>

        <div class="flex items-center gap-3 relative z-10">
          <div class="w-1 h-6 bg-[#00d1a0] shadow-[0_0_10px_#00d1a0]"></div>
<h3 class="relative flex items-end gap-2 text-3xl font-black italic tracking-widest uppercase">

  <!--
     1. 流光文字主体
     原理：背景是青色-白色-青色的渐变，宽度设为200%，通过动画移动背景位置，
     配合 bg-clip-text 让渐变只显示在文字上。
  -->
  <span class="bg-gradient-to-r from-[#00d1a0] via-[#ffffff] to-[#00d1a0] bg-[length:200%_auto] bg-clip-text text-transparent animate-text-flow drop-shadow-[0_0_8px_rgba(0,209,160,0.5)]">
    角色档案编辑
  </span>

  <!-- 2. 装饰性版本号 (保持机械感) -->
  <div class="flex flex-col items-start mb-1">
    <span class="text-[10px] leading-none text-[#00d1a0]/60 font-mono not-italic"></span>
    <span class="text-sm leading-none text-[#00d1a0] font-bold font-mono not-italic text-shadow-neon"></span>
  </div>

  <!-- 3. 底部装饰线条 (增加层次感) -->
  <div class="absolute -bottom-2 left-0 w-full h-[2px] bg-gradient-to-r from-[#00d1a0] to-transparent opacity-50"></div>
</h3>
        </div>

        <button @click="closeEditModal" class="relative z-10 w-8 h-8 flex items-center justify-center rounded bg-white/5 hover:bg-red-500 hover:text-white text-gray-400 transition-all duration-300">
          <X :size="18" />
        </button>
      </div>

      <!-- ============ BODY: 内容编辑区 ============ -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scroll bg-[#08080a] relative">

        <!-- 背景装饰字 -->
        <div class="absolute top-10 right-4 text-[100px] font-black text-white/0 stroke-text pointer-events-none select-none opacity-20">EDIT</div>

        <!-- 1. 基础信息组 (Tag & Name) -->
        <div class="grid grid-cols-12 gap-4">
          <!-- Tag Input -->
          <div class="col-span-4 group/input">
            <label class="block text-[20px] font-black text-[#00d1a0]/70 mb-1.5 tracking-widest uppercase group-focus-within/input:text-[#00d1a0] transition-colors">
  Tag / 标签
</label>
            <div class="relative">
              <input v-model="editForm.label" type="text" class="peer w-full bg-[#101014] text-white font-bold text-xl px-3 py-2.5 outline-none border-b-2 border-white/10 focus:border-[#00d1a0] focus:bg-[#00d1a0]/5 transition-all rounded-t-sm" placeholder="TAG">
              <!-- 角标装饰 -->
              <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/20 peer-focus:border-[#00d1a0] transition-colors"></div>
            </div>
          </div>

          <!-- Name Input -->
          <div class="col-span-8 group/input">
            <label class="block text-[20px]  font-black text-[#00d1a0]/70 mb-1.5 tracking-widest uppercase group-focus-within/input:text-[#00d1a0] transition-colors">Identity / 角色代号</label>
            <div class="relative">
              <input v-model="editForm.name" type="text" class="peer w-full bg-[#101014] text-[#00ffc3] font-bold text-xl px-4 py-2 outline-none border border-white/10 focus:border-[#00d1a0] focus:shadow-[0_0_20px_rgba(0,209,160,0.1)] transition-all rounded-sm placeholder-white/20" placeholder="NAME_ID">
              <!-- 科技感方块 -->
              <div class="absolute inset-y-0 right-0 w-1 bg-white/5 peer-focus:bg-[#00d1a0] transition-colors"></div>
            </div>
          </div>
        </div>

        <!-- 2. 特征描述 (Traits) -->
        <div class="group/area relative">
          <label class="flex justify-between text-[20px] font-black text-[#00d1a0]/70 mb-1.5 tracking-widest uppercase">
            <span>Traits / 特征数据</span>
            <span class="opacity-0 group-focus-within/area:opacity-100 transition-opacity text-[#00d1a0] animate-pulse"></span>
          </label>
          <div class="relative p-[1px] rounded bg-gradient-to-br from-white/10 to-transparent focus-within:from-[#00d1a0] focus-within:to-[#00d1a0]/20 transition-all duration-500">
             <div class="bg-[#101014] rounded h-32 relative overflow-hidden">
               <textarea v-model="editForm.desc" class="w-full h-full bg-transparent p-4 text-xl text-gray-300 font-bold leading-relaxed outline-none resize-none custom-scroll placeholder-gray-700 relative z-10" placeholder="输入角色特征描述..."></textarea>
               <!-- 底部网格装饰 -->
               <div class="absolute bottom-0 inset-x-0 h-8 bg-[linear-gradient(transparent_50%,rgba(0,209,160,0.05)_50%)] bg-[size:100%_4px] pointer-events-none"></div>
             </div>
          </div>
        </div>

        <!-- 3. 视觉数据注入 (图片 & 视频) -->
        <!-- 修改核心：改掉原本的白底/灰底，使用流光霓虹风格 -->
        <div class="pt-2">
          <label class="block text-[20px]0px] font-bold text-gray-500 mb-3 text-xl tracking-widest uppercase text-center">YunManGongFangAI / 视觉数据源</label>

          <div class="grid grid-cols-2 gap-5">

            <!-- ================= A. 图片卡片 ================= -->
            <div class="group/card relative h-40 rounded-lg overflow-hidden transition-all bg-[#0c0c10] border border-[#00d1a0]/30 hover:border-[#00d1a0]/60 hover:shadow-[0_0_20px_rgba(0,209,160,0.15)]">

              <!-- 状态 1: 有图片 -->
              <div v-if="editForm.image" class="w-full h-full relative group/content">
                <img :src="editForm.image" class="w-full h-full object-cover" />

                <!-- 悬停遮罩 -->
                <div class="absolute inset-0 bg-black/60 backdrop-blur-sm opacity-0 group-hover/content:opacity-100 transition-all duration-300 flex items-center justify-center gap-3">
                  <!-- 预览 -->
                  <button @click.stop="openLocalPreview('image', editForm.image)" class="p-2 rounded-full bg-white/10 hover:bg-[#00d1a0] hover:text-black text-white transition-all hover:scale-110" title="预览">
                    <Eye :size="18" />
                  </button>
                  <!-- 替换 -->
                  <button @click.stop="triggerImageUpload" class="p-2 rounded-full bg-white/10 hover:bg-blue-500 hover:text-white text-white transition-all hover:scale-110" title="替换">
                    <Sparkles :size="18" />
                  </button>
                  <!-- 删除 -->
                  <button @click.stop="clearEditImage" class="p-2 rounded-full bg-white/10 hover:bg-red-500 hover:text-white text-white transition-all hover:scale-110" title="删除">
                    <Trash2 :size="18" />
                  </button>
                </div>
              </div>

              <!-- 状态 2: 无图片 (显示上传按钮) -->
              <div
                v-else
                @click="triggerImageUpload"
                class="w-full h-full flex flex-col items-center justify-center cursor-pointer hover:bg-white/5 transition-colors group/empty"
              >
                <!-- 边框流光动画 -->
                <div class="absolute inset-[-50%] bg-[conic-gradient(from_0deg,transparent_0_340deg,#00d1a0_360deg)] animate-spin-slow opacity-0 group-hover/empty:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
                <div class="absolute inset-[1px] bg-[#0c0c10] rounded-lg z-0 pointer-events-none"></div>

                <div class="relative z-10 flex flex-col items-center">
                  <div class="w-10 h-10 mb-2 rounded-full bg-[#00d1a0]/10 flex items-center justify-center text-[#00d1a0] group-hover/empty:scale-110 transition-transform shadow-[0_0_15px_rgba(0,209,160,0.2)]">
                    <Sparkles :size="20" />
                  </div>
                  <span class="text-xs font-bold text-gray-500 group-hover/empty:text-white tracking-widest">UPLOAD IMAGE</span>
                </div>
              </div>
            </div>

            <!-- ================= B. 视频卡片 ================= -->
            <div class="group/card relative h-40 rounded-lg overflow-hidden transition-all bg-[#0c0c10] border border-[#00d1a0]/30 hover:border-[#00ffc3]/60 hover:shadow-[0_0_20px_rgba(0,255,195,0.15)]">

              <!-- 状态 1: 有视频 -->
              <div v-if="editForm.video" class="w-full h-full relative group/content">
                <video
                  :src="editForm.video"
                  class="w-full h-full object-cover"
                  muted loop autoplay playsinline
                ></video>

                <!-- 悬停遮罩 -->
                <div class="absolute inset-0 bg-black/60 backdrop-blur-sm opacity-0 group-hover/content:opacity-100 transition-all duration-300 flex items-center justify-center gap-3">
                  <!-- 预览 -->
                  <button @click.stop="openLocalPreview('video', editForm.video)" class="p-2 rounded-full bg-white/10 hover:bg-[#00ffc3] hover:text-black text-white transition-all hover:scale-110" title="预览">
                    <Play :size="18" class="ml-0.5" />
                  </button>
                  <!-- 替换 -->
                  <button @click.stop="triggerVideoUpload" class="p-2 rounded-full bg-white/10 hover:bg-blue-500 hover:text-white text-white transition-all hover:scale-110" title="替换">
                    <Clapperboard :size="18" />
                  </button>
                  <!-- 删除 -->
                  <button @click.stop="clearEditVideo" class="p-2 rounded-full bg-white/10 hover:bg-red-500 hover:text-white text-white transition-all hover:scale-110" title="删除">
                    <Trash2 :size="18" />
                  </button>
                </div>
              </div>

              <!-- 状态 2: 无视频 (显示上传按钮) -->
              <div
                v-else
                @click="triggerVideoUpload"
                class="w-full h-full flex flex-col items-center justify-center cursor-pointer hover:bg-white/5 transition-colors group/empty"
              >
                <!-- 边框流光动画 (不同色) -->
                <div class="absolute inset-[-50%] bg-[conic-gradient(from_0deg,transparent_0_340deg,#00ffc3_360deg)] animate-spin-reverse-slow opacity-0 group-hover/empty:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
                <div class="absolute inset-[1px] bg-[#0c0c10] rounded-lg z-0 pointer-events-none"></div>

                <div class="relative z-10 flex flex-col items-center">
                   <div class="w-10 h-10 mb-2 rounded-full bg-[#00ffc3]/10 flex items-center justify-center text-[#00ffc3] group-hover/empty:scale-110 transition-transform shadow-[0_0_15px_rgba(0,255,195,0.2)]">
                    <Clapperboard :size="20" />
                  </div>
                  <span class="text-xs font-bold text-gray-500 group-hover/empty:text-white tracking-widest">UPLOAD VIDEO</span>
                </div>
              </div>
            </div>

            <!-- 隐藏的 input (保持不变) -->
            <input type="file" ref="imageInputRef" class="hidden" accept="image/*" @change="handleImageUpload">
            <input type="file" ref="videoInputRef" class="hidden" accept="video/*" @change="handleVideoUpload">

          </div>
        </div>

      </div>

      <!-- ============ FOOTER: 底部按钮 ============ -->
      <div class="p-6 pt-2 bg-[#08080a] border-t border-white/5 relative z-20">
         <button
           @click="saveEdit"
           class="group relative w-full h-12 bg-[#00d1a0] overflow-hidden rounded-sm flex items-center justify-center gap-2 transition-all hover:bg-[#00ffc3] hover:shadow-[0_0_30px_rgba(0,209,160,0.4)] active:scale-[0.98]"
         >
           <!-- 按钮内部的扫描光扫过 -->
           <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full group-hover:animate-scan-x-fast"></div>

           <Save :size="18" class="text-black relative z-10" />
           <span class="text-black font-black tracking-[0.2em] text-lg relative z-10">SAVE CHANGES</span>
         </button>
      </div>
</div>
    </div>

  </div>
  <!-- ============ 新增：编辑页面的全屏预览层 ============ -->
    <div v-if="showLocalPreview" class="fixed inset-0 z-[300] bg-black/95 backdrop-blur-xl flex items-center justify-center animate-fade-in" @click="closeLocalPreview">

      <!-- 关闭按钮 -->
      <button class="absolute top-8 right-8 p-3 bg-white/10 hover:bg-white/20 rounded-full text-white transition-all z-50">
        <X :size="32" />
      </button>

      <!-- 预览内容容器 -->
      <div class="relative max-w-[90vw] max-h-[90vh]" @click.stop>

        <!-- 图片预览 -->
        <img
          v-if="localPreviewType === 'image'"
          :src="localPreviewUrl"
          class="max-w-full max-h-[90vh] object-contain rounded shadow-[0_0_50px_rgba(0,209,160,0.2)] border border-[#00d1a0]/20"
        />

        <!-- 视频预览 -->
        <div v-else class="relative rounded overflow-hidden shadow-[0_0_50px_rgba(0,255,195,0.2)] border border-[#00ffc3]/20">
          <video
            :src="localPreviewUrl"
            class="max-w-full max-h-[90vh] object-contain"
            controls autoplay
          ></video>
          <!-- 视频标签 -->
          <div class="absolute top-4 left-4 px-3 py-1 bg-black/60 backdrop-blur rounded text-[#00ffc3] font-bold
           text-xs border border-[#00ffc3]/30">
            YunManGoongFangAI
          </div>
        </div>

      </div>
    </div>
</template>

<script setup lang="ts">

import { ref, computed, reactive, onMounted, watch } from 'vue';
import {
  X, Plus, Search, Trash2, SearchX, Sparkles, Clapperboard, Save, Eye, Play
} from 'lucide-vue-next';
const props = defineProps<{
  projectName?: string; // 接收父组件传来的项目名
}>();
// ================= 1. 基础数据与加载 =================
const currentTab = ref('sora');
const searchQuery = ref('');

// 核心数据列表
const charList = ref<any[]>([]);

const filteredList = computed(() => {
  return charList.value.filter(item =>
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.label.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// 🔥 加载全局库数据
const loadLibraryData = async () => {
  if (!props.projectName) return; // 没有项目名就不加载

  try {
    // 🔥 URL 加上 project_name 参数
    const res = await fetch(`http://127.0.0.1:8000/api/style_library/load?project_name=${encodeURIComponent(props.projectName)}`);
    const json = await res.json();
    if (json.status === 'success') {
      charList.value = json.data || [];
      console.log(`📂 [${props.projectName}] 档案库加载成功`);
    }
  } catch (e) {
    console.error("加载失败:", e);
  }
};

// 🔥 保存全局库数据 (防抖)
let saveTimer: any = null;
const saveLibraryData = () => {
  if (!props.projectName) return;

  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {
    try {
      const dataToSave = charList.value.map(c => ({
         // ... 字段保持不变 ...
         id: c.id, label: c.label, name: c.name, desc: c.desc,
         image: c.image, video: c.video
      }));

      await fetch('http://127.0.0.1:8000/api/style_library/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: props.projectName, // 🔥 Body 里带上项目名
          characters: dataToSave
        })
      });
      console.log("💾 档案库保存成功");
    } catch (e) {
      console.error("保存失败:", e);
    }
  }, 1000);
};

// 生命周期
onMounted(() => {
  loadLibraryData();
});

// 监听数据变化 -> 触发保存
watch(charList, () => {
  saveLibraryData();
}, { deep: true });


// ================= 2. 编辑弹窗逻辑 =================
const showEditModal = ref(false);
const editForm = reactive({
  id: 0,
  label: '',
  name: '',
  desc: '',
  image: '',
  video: ''
});
const imageInputRef = ref<HTMLInputElement | null>(null);
const videoInputRef = ref<HTMLInputElement | null>(null);

// 添加新角色 (从父组件调用)
const addCharacterFromGen = (data: any) => {
  const newChar = {
    id: Date.now(),
    label: data.tag || '默认标签',
    name: data.name || '未命名角色',
    desc: data.desc || '暂无描述...',
    image: data.image || '',             // 确保这里传入的是 Base64 或 http链接，不是 blob
    video: data.video || ''
  };

  charList.value.unshift(newChar);
  // 触发保存
  saveLibraryData();
  // 打开编辑
  openEditModal(newChar);
};

// 暴露给父组件
defineExpose({
  addCharacterFromGen
});

// 手动点击 "+" 按钮
const addNewCharacter = () => {
  const newChar = {
    id: Date.now(),
    label: 'NEW TAG',
    name: '@new.character',
    desc: '',
    image: '',
    video: ''
  };
  charList.value.unshift(newChar);
  openEditModal(newChar);
};

const deleteChar = (id: number) => {
  if(confirm('警告：确认要从全局数据库中彻底抹除该角色数据吗？')) {
    charList.value = charList.value.filter(c => c.id !== id);
  }
};

const openEditModal = (char: any) => {
  // Deep Clone
  Object.assign(editForm, JSON.parse(JSON.stringify(char)));
  showEditModal.value = true;
};

const saveEdit = () => {
  const index = charList.value.findIndex(c => c.id === editForm.id);
  if (index !== -1) {
    charList.value[index] = { ...editForm };
    closeEditModal();
  }
};

const closeEditModal = () => {
  showEditModal.value = false;
};

// ================= 3. 文件上传 (转 Base64 核心) =================
const triggerImageUpload = () => imageInputRef.value?.click();
const triggerVideoUpload = () => videoInputRef.value?.click();

// 🔥 辅助函数：文件转 Base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
  });
};

const handleImageUpload = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) {
    // ⚠️ 修改：转为 Base64 以便存入 dat 文件
    const base64 = await fileToBase64(file);
    editForm.image = base64;
  }
  // 清空 input 允许重复选择
  if (imageInputRef.value) imageInputRef.value.value = '';
};

const handleVideoUpload = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) {
    // ⚠️ 警告：视频转 Base64 会导致 dat 文件非常大。
    // 如果视频很大，建议只存路径，但因为这是 Web 前端，没法直接存绝对路径。
    // 这里为了演示功能使用 Base64，实际生产环境建议用单独的文件上传接口。
    if (file.size > 10 * 1024 * 1024) { // 限制 10MB
       alert("为了保证性能，不仅以直接存储超过 10MB 的视频。\n请使用链接或压缩视频。");
       return;
    }
    const base64 = await fileToBase64(file);
    editForm.video = base64;
  }
  if (videoInputRef.value) videoInputRef.value.value = '';
};

// ================= 4. 预览与清理 =================
const showLocalPreview = ref(false);
const localPreviewType = ref<'image' | 'video'>('image');
const localPreviewUrl = ref('');

const openLocalPreview = (type: 'image' | 'video', url: string) => {
  if (!url) return;
  localPreviewType.value = type;
  localPreviewUrl.value = url;
  showLocalPreview.value = true;
};

const closeLocalPreview = () => {
  showLocalPreview.value = false;
  localPreviewUrl.value = '';
};

const clearEditImage = () => {
  if (confirm('确定要移除当前的角色图片吗？')) editForm.image = '';
};

const clearEditVideo = () => {
  if (confirm('确定要移除当前的角色视频吗？')) editForm.video = '';
};

</script>

<style scoped>
/* 背景网格平移动画 */
@keyframes pan-grid {
  0% { background-position: 0 0; }
  100% { background-position: 30px 30px; }
}
.animate-pan-grid {
  animation: pan-grid 4s linear infinite;
}

/* 反向旋转 (用于关闭按钮光环) */
@keyframes spin-reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}
.animate-spin-reverse {
  animation: spin-reverse 2s linear infinite;
}

/* 底部扫描线 */
@keyframes scan-x {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.group-hover\/header\:animate-scan-x:hover {
  animation: scan-x 1.5s linear infinite;
}
/* 弹窗进场动画 */
@keyframes slide-up-fade {
  0% { opacity: 0; transform: translateY(50px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
.animate-slide-up-fade {
  animation: slide-up-fade 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* 顶部扫描线 */
@keyframes scan-x {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.animate-scan-x {
  animation: scan-x 2s linear infinite;
}

/* 以下保持原有动画逻辑 */
@keyframes text-flow {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
.animate-text-flow {
  animation: text-flow 3s linear infinite;
}

@keyframes border-run {
  0% { background-position: 0% 50%; }
  100% { background-position: 250% 50%; }
}
.animate-border-run {
  animation: border-run 4s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100%); opacity: 0; }
  20% { opacity: 1; }
  100% { transform: translateY(500%); opacity: 0; }
}
.group-hover\:animate-scan:hover {
  animation: scan 1.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.custom-scroll::-webkit-scrollbar {
  width: 4px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: #08080c;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 4px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: #00d1a0;
  box-shadow: 0 0 15px #00d1a0;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
@keyframes fade-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>