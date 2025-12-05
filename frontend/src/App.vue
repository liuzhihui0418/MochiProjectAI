<template>
  <div class="app-root font-sans text-gray-100 overflow-hidden relative w-full h-screen bg-[#020204]">

    <!-- ================= 0. 静态背景层 ================= -->
    <div class="absolute inset-0 z-0 pointer-events-none">
      <div class="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] rounded-full bg-purple-900/30 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[-20%] right-[-10%] w-[70%] h-[70%] rounded-full bg-blue-900/30 blur-[150px] animate-pulse-slow delay-1000"></div>
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,black,transparent)]"></div>
    </div>

    <!-- ================= 1. Canvas 粒子层 ================= -->
    <canvas ref="bgCanvas" id="bgCanvas" class="absolute inset-0 z-0 pointer-events-none mix-blend-screen"></canvas>

    <!-- ================= 2. 界面层 ================= -->
    <div class="relative z-10 w-full h-full transition-all duration-500">

      <!-- A. 未登录状态 -->
      <Login v-if="!isLoggedIn" @loginSuccess="handleLoginSuccess" />

      <!-- B. 已登录状态 -->
      <div v-else class="flex h-screen w-full animate-fade-in glass-layout">

        <!-- === 左侧侧边栏 === -->
        <aside class="w-88 flex flex-col border-r border-white/10 bg-[#0a0a0a]/80 backdrop-blur-3xl flex-shrink-0 relative overflow-hidden z-20 shadow-[10px_0_40px_rgba(0,0,0,0.6)]">
          <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-transparent via-cyan-500/80 to-transparent shadow-[0_0_15px_#22d3ee]"></div>

          <!-- Logo -->
          <div class="h-36 flex items-center px-8 gap-6 relative z-10 group select-none shrink-0">
            <div class="relative w-20 h-20 flex-shrink-0">
              <div class="absolute inset-0 bg-gradient-to-br from-purple-600 via-fuchsia-600 to-cyan-600 rounded-full blur-[20px] opacity-60 group-hover:opacity-100 animate-pulse transition-all duration-500"></div>
              <div class="absolute -inset-[4px] rounded-full border-[2px] border-transparent border-t-cyan-400 border-r-purple-500 shadow-[0_0_20px_rgba(34,211,238,0.6)] animate-spin-slow"></div>
              <div class="relative w-full h-full rounded-full overflow-hidden border border-white/40 bg-black z-10 group-hover:scale-110 transition-transform duration-500">
                <img src="https://cdn.yunbaoymgf.chat/logo.png" alt="Logo" class="w-full h-full object-cover" />
                <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-white/50 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"></div>
              </div>
            </div>
            <div class="flex flex-col justify-center h-full pt-2">
              <h1 class="text-[26px] font-black italic leading-none tracking-tight text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
                YunMan<br>
                <span class="text-[30px] bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent filter drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]">GongFang.AI</span>
              </h1>
            </div>
          </div>

          <!-- Nav -->
          <nav class="flex-1 px-6 py-6 space-y-3 relative z-10 overflow-y-auto scrollbar-hide">
            <NavItem icon="Home" label="首页" active />
            <NavItem icon="Cloud" label="云端算力" />
            <NavItem icon="MonitorPlay" label="Sora 网页版" />
            <NavItem icon="Box" label="AI 智能体" />
            <div class="h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent my-6"></div>
            <NavItem icon="MessageCircle" label="技术支持" />
            <NavItem icon="Settings" label="系统设置" />
          </nav>

          <!-- User Card -->
          <div class="p-6 relative z-10 flex flex-col gap-4">
            <div class="p-[1px] rounded-2xl bg-gradient-to-r from-purple-500/50 via-cyan-500/50 to-purple-500/50 bg-[length:200%_auto] animate-border-flow">
              <div class="p-4 rounded-2xl bg-[#0F0F13] relative overflow-hidden group cursor-pointer hover:bg-white/5 transition-colors">
                <div class="flex items-center gap-4 relative z-10">
                  <div class="relative">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 p-[2px]">
                      <div class="w-full h-full rounded-[10px] bg-black flex items-center justify-center font-black text-xs text-white">SVIP</div>
                    </div>
                    <div class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-[#22c55e] rounded-full border-2 border-black shadow-[0_0_10px_#22c55e] animate-pulse"></div>
                  </div>
                  <div class="flex flex-col">
                    <span class="text-base font-bold text-white tracking-wide">超级管理员</span>
                    <span class="text-xs text-cyan-400 font-medium">VIP 终身会员</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-4 py-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between group hover:border-white/10 transition-colors">
              <div class="flex flex-col">
                <span class="text-[10px] text-gray-500 font-bold tracking-widest uppercase">LICENSE STATUS</span>
                <span class="font-mono text-xs font-bold text-gray-300 mt-0.5">{{ expiryDate }}</span>
              </div>
              <div class="relative">
                <div class="w-2.5 h-2.5 rounded-full" :class="isExpired ? 'bg-red-500' : 'bg-green-400 shadow-[0_0_8px_#4ade80]'"></div>
                <div v-if="!isExpired" class="absolute inset-0 rounded-full bg-green-400 animate-ping opacity-75"></div>
              </div>
            </div>
          </div>
        </aside>

        <!-- === 右侧主内容区 === -->
        <main class="flex-1 flex flex-col relative overflow-hidden bg-transparent">
          <!-- Header -->
          <header class="h-28 px-12 flex justify-between items-center z-20 relative shrink-0">
            <div class="flex items-center">
               <div class="pl-2 pr-6 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md flex items-center gap-4 group hover:border-purple-500/50 transition-all duration-300">
                 <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-cyan-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                   <Megaphone :size="20" class="text-white" />
                 </div>
                 <span class="text-base font-medium text-gray-200">欢迎回来，开启你的 <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 font-bold">AI 创作之旅</span></span>
               </div>
            </div>
            <div class="flex items-center gap-8">
              <div class="group relative cursor-pointer">
                 <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full blur-lg opacity-20 group-hover:opacity-70 transition-opacity duration-300"></div>
                 <div class="relative px-6 py-3 rounded-full bg-[#121212] border border-white/10 flex items-center gap-4 hover:border-purple-500 transition-colors group-active:scale-95">
                   <span class="text-xl animate-bounce-slow">💎</span>
                   <span class="font-black font-mono text-white text-xl tracking-wider">88,474</span>
                   <button class="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center text-base font-bold hover:bg-cyan-300 hover:scale-110 transition-all shadow-lg">+</button>
                 </div>
              </div>
              <button class="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 hover:text-cyan-400 hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition-all relative active:scale-90">
                <Bell :size="22" />
                <span class="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-[#050505] animate-ping"></span>
                <span class="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-[#050505]"></span>
              </button>
            </div>
          </header>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto p-12 pt-4 scrollbar-hide relative z-10">

            <!-- Banner -->
            <div class="grid grid-cols-12 gap-8 mb-12">
              <div class="col-span-6 h-[380px] rounded-[40px] relative group cursor-pointer perspective-1000">
                <div class="absolute inset-0 rounded-[40px] bg-[#0F0F11] border border-white/10 overflow-hidden transition-all duration-500 group-hover:border-cyan-500/50 group-hover:shadow-[0_0_60px_rgba(34,211,238,0.2)]">
                  <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=1974&auto=format&fit=crop')] bg-cover bg-center transition-transform duration-1000 group-hover:scale-110"></div>
                  <div class="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent opacity-90"></div>
                  <div class="absolute inset-0 bg-gradient-to-r from-black/80 via-transparent to-transparent"></div>
                  <div class="absolute bottom-0 left-0 w-full p-12 flex flex-col items-start z-20">
                    <div class="mb-5 px-4 py-1.5 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-sm font-bold tracking-widest backdrop-blur-md shadow-[0_0_20px_rgba(34,211,238,0.2)]">
                      FEATURED PROJECT
                    </div>
                    <h2 class="text-6xl font-black text-white leading-tight mb-8 drop-shadow-[0_5px_5px_rgba(0,0,0,0.8)]">
                      原创漫剧<br>
                      <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-400 animate-gradient-x">一键生成</span>
                    </h2>
                    <button @click="openCreateModal" class="relative overflow-hidden group/btn px-10 py-4 rounded-xl bg-white text-black font-bold text-lg transition-all duration-300 hover:shadow-[0_0_40px_rgba(255,255,255,0.6)] hover:scale-105 active:scale-95">
                      <div class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-300"></div>
                      <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/80 to-transparent -translate-x-[150%] group-hover/btn:translate-x-[150%] transition-transform duration-700 ease-in-out skew-x-[-20deg]"></div>
                      <span class="relative z-10 flex items-center gap-3 group-hover/btn:text-white transition-colors">
                        立即创作 <ArrowRight :size="22" class="group-hover/btn:translate-x-1 transition-transform"/>
                      </span>
                    </button>
                  </div>
                </div>
              </div>

              <div class="col-span-6 h-[380px] rounded-[40px] relative group cursor-pointer perspective-1000">
                <div class="absolute inset-0 rounded-[40px] bg-[#0F0F11] border border-white/10 overflow-hidden transition-all duration-500 group-hover:border-pink-500/50 group-hover:shadow-[0_0_60px_rgba(236,72,153,0.2)]">
                  <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1614728853913-1e22ba863009?q=80&w=2089&auto=format&fit=crop')] bg-cover bg-center transition-transform duration-1000 group-hover:scale-110"></div>
                  <div class="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-90"></div>
                  <div class="absolute inset-0 p-12 flex flex-col justify-end items-start z-20">
                     <h2 class="text-5xl font-black text-white mb-4 italic drop-shadow-[0_5px_5px_rgba(0,0,0,0.8)]">
                      爆款复刻 <span class="text-pink-500 inline-block animate-pulse">Speed Run</span>
                    </h2>
                    <p class="text-gray-200 text-xl font-medium mb-8 max-w-lg drop-shadow-md">使用最先进的 AI 引擎，将现有视频转化为全新风格的动态漫剧。</p>
                    <button @click="openCreateModal" class="px-8 py-3.5 rounded-xl bg-white/10 border border-white/30 text-white font-bold text-lg backdrop-blur-xl hover:bg-pink-600 hover:border-pink-500 hover:shadow-[0_0_30px_#db2777] transition-all transform hover:-translate-y-1 active:translate-y-0">
                      开始复刻 →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 数据表格 -->
            <div class="relative bg-[#0a0a0a]/90 backdrop-blur-xl rounded-[32px] border border-white/10 overflow-hidden flex flex-col min-h-[500px] shadow-2xl hover:border-white/20 transition-colors duration-500">
              <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500"></div>

              <div class="p-8 flex justify-between items-center z-10">
                <div class="flex gap-4">
                   <button class="text-lg font-bold text-white px-4 py-2 relative group">
                     全部作品
                     <span class="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-[3px] bg-cyan-500 rounded-full shadow-[0_0_10px_#22d3ee]"></span>
                   </button>
                   <button class="text-lg font-bold text-gray-500 px-4 py-2 hover:text-white transition-colors">
                     回收站
                   </button>
                </div>

                <button @click="openCreateModal" class="group relative px-8 py-4 rounded-xl bg-white overflow-hidden active:scale-95 transition-all duration-200">
                  <div class="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] animate-flow-bg"></div>
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 skew-x-[-20deg]"></div>
                  <div class="relative z-10 flex items-center gap-3 text-white font-black text-lg tracking-wide">
                    <Plus :size="24" stroke-width="3" />
                    <span>新建空间</span>
                  </div>
                </button>
              </div>

              <div class="grid grid-cols-12 px-10 py-6 bg-white/[0.05] border-y border-white/10 text-lg font-black text-white uppercase tracking-widest drop-shadow-md">
                <div class="col-span-4 pl-6">&nbsp&nbsp&nbsp&nbsp作品名称</div>
                <div class="col-span-2 text-center">作品类型</div>
                <div class="col-span-2 text-center">作品状态</div>
                <div class="col-span-1 text-center">比例</div>
                <div class="col-span-2 text-center">创建日期</div>
                <div class="col-span-1 text-right pr-2">操作</div>
              </div>

              <div v-if="loading" class="flex-1 flex flex-col items-center justify-center py-20 gap-6">
                <div class="w-16 h-16 border-4 border-purple-500/30 border-t-cyan-500 rounded-full animate-spin shadow-[0_0_30px_rgba(34,211,238,0.3)]"></div>
                <p class="text-gray-400 font-bold text-lg animate-pulse tracking-widest">LOADING DATA...</p>
              </div>

              <div v-else class="flex-1 overflow-y-auto custom-scroll p-2">
                <div v-for="item in projects" :key="item.id"
                     class="grid grid-cols-12 px-8 py-6 items-center rounded-xl hover:bg-white/[0.04] transition-all duration-300 group relative cursor-pointer mb-1 border border-transparent hover:border-white/5">

                  <div class="absolute left-2 top-1/2 -translate-y-1/2 h-8 w-1 bg-gradient-to-b from-cyan-400 to-purple-500 rounded-full opacity-0 group-hover:opacity-100 transition-all shadow-[0_0_15px_#22d3ee]"></div>

                  <div class="col-span-4 flex items-center gap-5 pl-4">
                    <div class="w-14 h-14 rounded-2xl bg-[#151518] border border-white/10 flex items-center justify-center text-3xl shadow-lg group-hover:scale-105 transition-transform group-hover:border-purple-500/30 group-hover:text-purple-400 flex-shrink-0">
                      🎬
                    </div>
                    <div class="overflow-hidden">
                      <h3 class="font-bold text-white text-lg mb-1 truncate group-hover:text-cyan-300 transition-colors">{{ item.name }}</h3>
                      <span class="text-xs text-gray-500 font-mono flex items-center gap-2">
                         <span class="w-1.5 h-1.5 rounded-full bg-gray-600"></span> ID: {{ item.id }}
                      </span>
                    </div>
                  </div>

                  <div class="col-span-2 flex justify-center">
                    <div v-if="item.type === 'original' || item.type === '原创动态漫'" class="px-4 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-sm font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(34,211,238,0.15)]">
                       <span class="text-xs">✨</span> 原创动态漫
                    </div>
                    <div v-else-if="item.type === 'secondary' || item.type === '二创动态漫'" class="px-4 py-1.5 rounded-lg bg-pink-500/10 border border-pink-500/30 text-pink-300 text-sm font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(236,72,153,0.15)]">
                       <span class="text-xs">🔄</span> 二创动态漫
                    </div>
                     <div v-else class="px-4 py-1.5 rounded-lg bg-gray-500/10 border border-gray-500/30 text-gray-300 text-sm font-bold flex items-center gap-2">
                       <span class="text-xs">📁</span> 未知作品
                    </div>
                  </div>

                  <div class="col-span-2 flex justify-center">
                    <span class="px-4 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-bold tracking-wide shadow-[0_0_15px_rgba(74,222,128,0.1)] group-hover:bg-green-500/20 transition-colors">
                      COMPLETED
                    </span>
                  </div>

                  <div class="col-span-1 text-center font-mono text-gray-300 text-base font-bold">{{ item.ratio }}</div>

                  <div class="col-span-2 text-center">
                    <div class="font-mono text-base text-gray-300">{{ item.created_at }}</div>
                  </div>

                  <div class="col-span-1 flex justify-end gap-2 pr-2">
                    <button class="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-cyan-500 hover:text-white hover:border-cyan-400 hover:shadow-[0_0_15px_#22d3ee] transition-all" title="进入空间">
                        <LogIn :size="18"/>
                    </button>
                    <button @click.stop="handleDelete(item.name)" class="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-red-500 hover:text-white hover:border-red-400 hover:shadow-[0_0_15px_#ef4444] transition-all" title="删除项目">
                        <Trash2 :size="18"/>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="h-12"></div>
          </div>
        </main>
      </div>

      <!-- ================= 3. 创建空间弹窗 ================= -->
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeModal"></div>
          <div class="relative w-full max-w-[480px] bg-[#18181b] rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden transform transition-all scale-100">
            <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-cyan-500 via-purple-500 to-cyan-500"></div>

            <div class="flex justify-between items-center p-6 pb-2">
              <h2 class="text-xl font-bold text-white tracking-wide">创建空间</h2>
              <button @click="closeModal" class="text-gray-500 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            <div class="p-8 pt-4 space-y-6">
              <div class="space-y-2">
                <label class="text-sm font-bold text-gray-400 flex justify-between">
                  <span>* 空间名称</span>
                  <span class="text-xs text-gray-600">{{ form.name.length }} / 10</span>
                </label>
                <div class="relative group">
                   <input type="text" v-model="form.name" maxlength="10" placeholder="请输入空间名称"
                          class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" />
                </div>
              </div>

              <div class="space-y-2 relative z-20">
                <label class="text-sm font-bold text-gray-400">项目类型</label>
                <div class="relative">
                  <button @click="showTypeSelect = !showTypeSelect; showRatioSelect = false"
                          class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-left text-white flex justify-between items-center hover:border-white/20 transition-all">
                    <span>{{ form.type }}</span>
                    <svg :class="{'rotate-180': showTypeSelect}" class="w-4 h-4 text-gray-500 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </button>
                  <Transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
                    <div v-if="showTypeSelect" class="absolute top-full left-0 w-full mt-2 bg-[#18181b] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-30">
                      <div v-for="option in typeOptions" :key="option"
                           @click="form.type = option; showTypeSelect = false"
                           class="px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-cyan-400 cursor-pointer transition-colors flex items-center justify-between">
                         {{ option }}
                         <span v-if="form.type === option" class="text-cyan-400">✓</span>
                      </div>
                    </div>
                  </Transition>
                </div>
              </div>

              <div class="space-y-2 relative z-10">
                <label class="text-sm font-bold text-gray-400">视频比例</label>
                <div class="relative">
                  <button @click="showRatioSelect = !showRatioSelect; showTypeSelect = false"
                          class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-left text-white flex justify-between items-center hover:border-white/20 transition-all">
                    <span>{{ form.ratio }}</span>
                    <svg :class="{'rotate-180': showRatioSelect}" class="w-4 h-4 text-gray-500 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </button>
                  <Transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
                    <div v-if="showRatioSelect" class="absolute top-full left-0 w-full mt-2 bg-[#18181b] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-30">
                      <div v-for="option in ratioOptions" :key="option"
                           @click="form.ratio = option; showRatioSelect = false"
                           class="px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-cyan-400 cursor-pointer transition-colors flex items-center justify-between">
                         {{ option }}
                         <span v-if="form.ratio === option" class="text-cyan-400">✓</span>
                      </div>
                    </div>
                  </Transition>
                </div>
              </div>

            </div>

            <div class="p-6 pt-2 flex gap-4">
              <button @click="closeModal" class="flex-1 py-3.5 rounded-xl bg-white/5 text-gray-400 font-bold hover:bg-white/10 hover:text-white transition-colors">
                取消
              </button>
              <button @click="handleCreate" class="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-cyan-400 to-green-400 text-black font-black hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] active:scale-95 transition-all">
                立即创建
              </button>
            </div>

          </div>
        </div>
      </Transition>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, Component, nextTick, onUnmounted } from 'vue';
import Login from './components/Login.vue';
import {
  Home, Cloud, MonitorPlay, Box, MessageCircle, Mail, Settings,
  Megaphone, Bell, Plus, ArrowRight, Trash2, LogIn
} from 'lucide-vue-next';

// === 状态管理 ===
const isLoggedIn = ref(false);
const expiryDate = ref('Loading...');
const isExpired = ref(false);
const projects = ref<Project[]>([]);
const loading = ref(true);
const bgCanvas = ref<HTMLCanvasElement | null>(null);
let animationId: number;

// === 弹窗与表单逻辑 ===
const isModalOpen = ref(false);
const showTypeSelect = ref(false);
const showRatioSelect = ref(false);

const form = ref({
  name: '',
  type: '原创动态漫',
  ratio: '16:9'
});

const typeOptions = ['原创动态漫', '二创动态漫'];
const ratioOptions = ['16:9', '9:16'];

const openCreateModal = () => {
  form.value = { name: '', type: '原创动态漫', ratio: '16:9' };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  showTypeSelect.value = false;
  showRatioSelect.value = false;
};

// === 核心逻辑修改：对接后端 API ===
const handleCreate = async () => {
  if (!form.value.name.trim()) {
    alert("请输入空间名称");
    return;
  }

  try {
    // 构造请求数据，必须与后端 ProjectReq 模型一致
    const payload = {
      name: form.value.name,
      type: form.value.type || '原创动态漫',
      ratio: form.value.ratio || '16:9',
      id: 0, // 后端会重写
      created_at: "" // 后端会重写
    };

    console.log("正在发送创建请求:", payload);

    const response = await fetch('http://127.0.0.1:8000/api/create_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      alert(`创建失败: ${errorData.detail}`);
      return;
    }

    // 成功后关闭弹窗并刷新
    closeModal();
    loading.value = true;

    // 稍微延迟一下确保文件写入完成
    setTimeout(async () => {
        await fetchProjects();
    }, 500);

  } catch (e) {
    console.error("网络错误:", e);
    alert("连接后端失败，请检查黑色控制台窗口是否开启");
  }
};

const fetchProjects = async () => {
  try {
    loading.value = true;
    const res = await fetch('http://127.0.0.1:8000/api/projects');
    if (res.ok) {
      projects.value = await res.json();
    }
  } catch (e) {
    console.error("加载项目失败", e);
  } finally {
    loading.value = false;
  }
};

const handleDelete = async (name: string) => {
  if(!confirm(`确定要永久删除项目 "${name}" 吗？此操作不可撤销。`)) return;
  try {
    // 3. 删除逻辑也对接后端
    const res = await fetch(`http://127.0.0.1:8000/api/delete_project/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      await fetchProjects();
    } else {
      alert("删除失败");
    }
  } catch(e) {
    alert("网络错误");
  }
};

const handleLoginSuccess = async () => {
  isLoggedIn.value = true;
  await nextTick();
  initCanvas();
  await fetchProjects();
  await checkLoginStatus();
};

const checkLoginStatus = async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/status');
    const data = await res.json();
    if (data.activated) {
      isLoggedIn.value = true;
      if (data.info && data.info.expiry_date) {
        expiryDate.value = data.info.expiry_date;
        const today = new Date().toISOString().split('T')[0];
        if (expiryDate.value < today) isExpired.value = true;
      } else {
        expiryDate.value = '永久授权';
      }
      if (projects.value.length === 0) fetchProjects();
      await nextTick();
      if (!animationId) initCanvas();
    }
  } catch (e) {
    console.log("未连接后端或未激活");
  }
};

const initCanvas = () => {
  const canvas = document.getElementById('bgCanvas') as HTMLCanvasElement;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  let width: number, height: number;
  let particles: any[] = [];
  const mouse = { x: null as number | null, y: null as number | null, radius: 250 };

  const onMouseMove = (e: MouseEvent) => { mouse.x = e.clientX; mouse.y = e.clientY; };
  const onMouseOut = () => { mouse.x = null; mouse.y = null; };
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseout', onMouseOut);

  const initSize = () => { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; };
  const properties = { bgColor: 'rgba(5, 5, 5, 1)', particleColor: 'rgba(139, 92, 246, 0.8)', particleRadius: 2, particleCount: window.innerWidth > 1000 ? 120 : 60, particleVelocity: 0.5, lineLength: 150 };

  class Particle {
    x: number; y: number; velocityX: number; velocityY: number; size: number;
    constructor() {
      this.x = Math.random() * width; this.y = Math.random() * height;
      this.velocityX = Math.random() * (properties.particleVelocity * 2) - properties.particleVelocity;
      this.velocityY = Math.random() * (properties.particleVelocity * 2) - properties.particleVelocity;
      this.size = Math.random() * 2 + 1;
    }
    position() {
      if(this.x > width || this.x < 0) this.velocityX *= -1;
      if(this.y > height || this.y < 0) this.velocityY *= -1;
      this.x += this.velocityX; this.y += this.velocityY;
    }
    reDraw() {
      if(!ctx) return;
      ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fillStyle = properties.particleColor; ctx.fill();
    }
  }
  const drawLines = () => {
    if(!ctx) return;
    let x1, y1, x2, y2, length, opacity;
    for (let i in particles) {
      for (let j in particles) {
        x1 = particles[i].x; y1 = particles[i].y; x2 = particles[j].x; y2 = particles[j].y;
        length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        if (length < properties.lineLength) {
          opacity = 1 - length / properties.lineLength;
          ctx.lineWidth = 0.5; ctx.strokeStyle = `rgba(139, 92, 246, ${opacity})`;
          ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
        }
      }
      if (mouse.x != null && mouse.y != null) {
        let mouseDist = Math.sqrt(Math.pow(mouse.x - particles[i].x, 2) + Math.pow(mouse.y - particles[i].y, 2));
        if (mouseDist < mouse.radius) {
          ctx.lineWidth = 1; ctx.strokeStyle = `rgba(59, 130, 246, ${1 - mouseDist/mouse.radius})`;
          ctx.beginPath(); ctx.moveTo(particles[i].x, particles[i].y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
      }
    }
  };
  const loop = () => { ctx!.clearRect(0, 0, width, height); for (let i in particles) { particles[i].position(); particles[i].reDraw(); } drawLines(); animationId = requestAnimationFrame(loop); };
  const initParticles = () => { particles = []; for(let i=0; i<properties.particleCount; i++) { particles.push(new Particle()); } loop(); };
  initSize(); window.addEventListener('resize', initSize); initParticles();
};

onMounted(() => { checkLoginStatus(); initCanvas(); });
onUnmounted(() => { cancelAnimationFrame(animationId); window.removeEventListener('mousemove', () => {}); window.removeEventListener('mouseout', () => {}); });

interface Project {
    id: number;
    name: string;
    ratio: string;
    created_at: string;
    updated_at: string;
    type?: string;
}

const NavItem = (props: { icon: string, label: string, active?: boolean }) => {
  const icons: Record<string, Component> = { Home, Cloud, MonitorPlay, Box, MessageCircle, Mail, Settings };
  return h('button', {
    class: `group relative flex items-center gap-5 px-6 py-4 rounded-2xl w-full text-left transition-all duration-300 overflow-hidden ${
      props.active ? 'bg-gradient-to-r from-purple-600/20 to-cyan-600/20 shadow-[0_5px_20px_rgba(168,85,247,0.15)]' : 'hover:bg-white/5'
    }`
  }, [
    props.active && h('div', { class: 'absolute left-0 top-0 bottom-0 w-[4px] bg-gradient-to-b from-purple-400 to-cyan-400 shadow-[0_0_15px_#a855f7]' }),
    h(icons[props.icon], { size: 24, class: props.active ? 'text-cyan-300 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]' : 'text-gray-400 group-hover:text-gray-200 transition-colors duration-300 group-hover:scale-110' }),
    h('span', { class: `relative z-10 font-bold tracking-wide text-lg ${props.active ? 'text-white text-glow' : 'text-gray-400 group-hover:text-white transition-colors duration-300'}` }, props.label),
    h('div', { class: 'absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-500 pointer-events-none' })
  ]);
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.98) translateY(15px); } to { opacity: 1; transform: scale(1) translateY(0); } }
.animate-fade-in { animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.animate-spin-slow { animation: spin-slow 15s linear infinite; }
@keyframes pulse-slow { 0%, 100% { opacity: 0.3; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.1); } }
.animate-pulse-slow { animation: pulse-slow 6s ease-in-out infinite; }
@keyframes borderFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.animate-border-flow { background-size: 200% 200%; animation: borderFlow 4s ease infinite; }
@keyframes flowBg { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
.animate-flow-bg { animation: flowBg 3s linear infinite; }
@keyframes gradient-x { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.animate-gradient-x { background-size: 200% 200%; animation: gradient-x 4s ease infinite; }
@keyframes bounce-slow { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.animate-bounce-slow { animation: bounce-slow 3s ease-in-out infinite; }
.glass-layout { backdrop-filter: blur(0px); }
.text-glow { text-shadow: 0 0 15px rgba(34, 211, 238, 0.6); }
.perspective-1000 { perspective: 1200px; }
</style>