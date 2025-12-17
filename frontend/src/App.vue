<template>
  <div class="app-root font-sans text-gray-100 overflow-hidden relative w-full h-screen bg-[#020204]">
    <!-- 🔥 1. 插入全局通知组件 -->
    <GlobalToast />

    <!-- 全局加载遮罩 -->
    <div v-if="pageLoading" class="fixed inset-0 z-[9999] flex items-center justify-center bg-[#020204]">
      <div class="flex flex-col items-center gap-6">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 border-4 border-transparent rounded-full animate-pulse"
               style="background: linear-gradient(#020204, #020204) padding-box, conic-gradient(from 0deg, transparent, #8b5cf6, #3b82f6, #8b5cf6, transparent) border-box;"></div>
          <div class="absolute inset-2 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-600/20 backdrop-blur-sm"></div>
          <div class="absolute w-2 h-2 bg-cyan-400 rounded-full shadow-[0_0_15px_#22d3ee] animate-spin"
               style="animation-duration: 1.5s; left: 50%; top: 0; transform-origin: 50% 100%;"></div>
          <div class="absolute inset-3 border-2 border-transparent rounded-full animate-spin"
               style="border-image: conic-gradient(from 0deg, #06b6d4, #8b5cf6, #06b6d4) 1; animation-duration: 2s;"></div>
        </div>
        <div class="relative">
          <p class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-purple-300 to-cyan-300 font-bold text-lg tracking-widest animate-gradient">
           YunManGongFangAI 页面初始化中请稍后
          </p>
        </div>
      </div>
    </div>

    <!-- 0. 静态背景层 (全局共享) -->
    <div class="absolute inset-0 z-0 pointer-events-none">
      <div class="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] rounded-full bg-purple-900/30 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[-20%] right-[-10%] w-[70%] h-[70%] rounded-full bg-blue-900/30 blur-[150px] animate-pulse-slow delay-1000"></div>
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,black,transparent)]"></div>
    </div>

    <!-- 1. Canvas 粒子层 (全局共享) -->
    <canvas ref="bgCanvas" id="bgCanvas" class="absolute inset-0 z-0 pointer-events-none mix-blend-screen"></canvas>

    <!-- 2. 内容层容器 -->
    <div class="relative z-10 w-full h-full transition-all duration-500">

      <VideoGenerationWorkbench
        v-if="showWorkbench"
        :projectId="currentProject?.id || ''"
        :projectName="currentProject?.name || '未命名作品'"
        :initialClips="currentClips"
        @back="exitWorkbench"
      />

      <!-- B. 否则显示主界面 -->
      <div v-else class="w-full h-full relative">

        <!-- 2.1 界面层内容 -->
        <div class="w-full h-full">

          <!-- A. 未登录状态 -->
          <Login v-if="!isLoggedIn" @loginSuccess="handleLoginSuccess" />

          <!-- B. 已登录状态 -->
          <div v-else class="flex h-screen w-full animate-fade-in glass-layout">

            <!-- === 左侧侧边栏 === -->
            <aside class="w-88 flex flex-col border-r border-white/10 bg-[#0a0a0a]/80 backdrop-blur-3xl flex-shrink-0 relative overflow-hidden z-20 shadow-[10px_0_40px_rgba(0,0,0,0.6)]">
              <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-transparent via-cyan-500/80 to-transparent shadow-[0_0_15px_#22d3ee]"></div>

              <!-- Logo -->
              <div class="h-36 flex items-center px-8 gap-6 relative z-10 group select-none shrink-0">
                <div class="relative w-20 h-20 flex-shrink-0 cursor-pointer">
                  <div class="absolute inset-0 bg-gradient-to-br from-purple-600 via-fuchsia-600 to-cyan-600 rounded-full blur-[20px] opacity-60 group-hover:opacity-100 animate-pulse transition-all duration-500"></div>
                  <div class="absolute -inset-[4px] rounded-full border-[2px] border-transparent border-t-cyan-400 border-r-purple-500 shadow-[0_0_20px_rgba(34,211,238,0.6)] animate-spin-slow"></div>
                  <div class="relative w-full h-full rounded-full overflow-hidden border border-white/40 bg-black z-10 group-hover:scale-110 transition-transform duration-500">
                    <img src="https://cdn.yunbaoymgf.chat/logo.png" alt="Logo" class="w-full h-full object-cover" />
                  </div>
                </div>
                <div class="flex flex-col justify-center h-full pt-2">
                  <h1 class="text-[26px] font-black italic leading-none tracking-tight text-white drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
                    YunMan<br>
                    <span class="text-[30px] bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent filter drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]">GongFang.AI</span>
                  </h1>
                </div>
              </div>

              <!-- Nav (侧边栏导航) -->
              <nav class="flex-1 px-6 py-6 space-y-3 relative z-10 overflow-y-auto scrollbar-hide">
                <!-- 🔥 修改点：添加点击事件，切换 currentView -->
                <NavItem icon="Home" label="首页" @click="switchView('home')" :active="currentView === 'home'" />
                <NavItem icon="Cloud" label="云端算力" />
                <!-- 🔥 修改这里：添加 @click 事件 -->
                <NavItem icon="MonitorPlay" label="Sora 网页版" @click="openSoraWeb" />
                <NavItem icon="Box" label="AI智能体" />

                <!-- 🔥 修改点：添加点击事件，切换 currentView -->
                <NavItem icon="Box" label="YunManBanana" @click="switchView('banana')" :active="currentView === 'banana'" />

                <div class="h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent my-6"></div>
                <NavItem icon="MessageCircle" label="技术支持" />
                <NavItem icon="Settings" label="系统设置" />
              </nav>

              <!-- User Card -->
              <div class="p-6 relative z-10 flex flex-col gap-4">
                <div class="p-[1px] rounded-2xl bg-gradient-to-r from-purple-500/50 via-cyan-500/50 to-purple-500/50 bg-[length:200%_auto] animate-border-flow">
                  <div class="p-4 rounded-2xl bg-[#0F0F13] active:scale-[0.98] relative overflow-hidden group cursor-pointer transition-colors">
                    <div class="flex items-center gap-4 relative z-10">
                      <div class="relative">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 p-[2px]">
                          <div class="w-full h-full rounded-[10px] bg-black flex items-center justify-center font-black text-xs text-white">SVIP</div>
                        </div>
                        <div class="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full border-2 border-black" :class="isExpired ? 'bg-red-500' : 'bg-green-400 shadow-[0_0_10px_#22c55e]'"></div>
                      </div>
                      <div class="flex flex-col flex-1 min-w-0">
                        <span class="text-base font-bold text-white tracking-wide">超级管理员</span>
                        <span class="text-xs text-gray-400 font-mono mt-0.5 flex items-center gap-1 mb-2">
                          <span v-if="!isExpired" class="text-green-400">●</span>
                          {{ expiryDate }}
                        </span>
                        <div class="flex items-center justify-between gap-2 bg-white/10 px-3 py-1.5 rounded-lg border border-white/5 group/id hover:border-cyan-500/30 transition-all cursor-pointer" @click.stop="copyMachineId">
                          <span class="text-xs text-white font-mono truncate" title="设备ID">{{ machineId }}</span>
                          <button class="text-gray-400 hover:text-cyan-400 transition-colors p-1 flex-shrink-0" title="复制设备ID"><Copy :size="14" /></button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </aside>

            <!-- === 右侧主内容区 (使用 v-if 切换) === -->
            <main class="flex-1 flex flex-col relative overflow-hidden bg-transparent">

              <!-- 🔥 情况 1: 显示 YunManBanana 组件 -->
              <YunManBanana v-if="currentView === 'banana'" />

              <!-- 🔥 情况 2: 显示 首页内容 (用 template 包裹) -->
              <template v-else-if="currentView === 'home'">
                <!-- Header -->
                <header class="h-28 px-12 flex justify-between items-center z-20 relative shrink-0">
                  <div class="flex items-center">
                     <div class="pl-2 pr-6 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md flex items-center gap-4 group hover:border-purple-500/50 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all duration-300 cursor-default">
                       <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-cyan-600 flex items-center justify-center shadow-lg group-hover:rotate-12 transition-transform duration-500">
                         <Megaphone :size="20" class="text-white" />
                       </div>
                       <span class="text-base font-medium text-gray-200">欢迎回来，开启你的 <span class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 font-bold animate-pulse">AI 创作之旅</span></span>
                     </div>
                  </div>

                  <!-- 右侧功能区 -->
                  <div class="flex items-center gap-6">
                    <div class="flex items-center gap-4 mr-4">
                      <div class="relative group cursor-pointer">
                        <button class="btn-social-flow green-flow"><MessageCircle :size="18" /> 微信助手</button>
                        <div class="absolute top-full right-0 mt-4 w-40 p-3 bg-[#18181b]/95 border border-green-500/30 rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform translate-y-4 group-hover:translate-y-0 z-50 shadow-[0_10px_30px_rgba(0,0,0,0.5)] backdrop-blur-md">
                          <img src="https://cdn.yunbaoymgf.chat/weixin.png" class="w-full rounded-lg mb-2 shadow-inner" alt="微信">
                        </div>
                      </div>
                      <div class="relative group cursor-pointer">
                        <button class="btn-social-flow blue-flow"><Link :size="18" /> 变现链路</button>
                        <div class="absolute top-full right-0 mt-4 w-40 p-3 bg-[#18181b]/95 border border-blue-500/30 rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform translate-y-4 group-hover:translate-y-0 z-50 shadow-[0_10px_30px_rgba(0,0,0,0.5)] backdrop-blur-md">
                          <img src="https://cdn.yunbaoymgf.chat/qq.png" class="w-full rounded-lg mb-2 shadow-inner" alt="QQ">
                        </div>
                      </div>
                    </div>
                    <button class="w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 hover:text-cyan-400 transition-all relative active:scale-90">
                      <Bell :size="22" /><span class="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-[#050505] animate-ping"></span><span class="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-[#050505]"></span>
                    </button>
                  </div>
                </header>

                <!-- Content -->
                <div class="flex-1 overflow-y-auto p-12 pt-4 scrollbar-hide relative z-10">
                  <!-- Banner -->
                  <div class="grid grid-cols-12 gap-8 mb-12">
                    <div class="col-span-6 h-[380px] rounded-[40px] relative group cursor-pointer perspective-1000">
                      <div class="absolute inset-0 rounded-[40px] bg-[#0F0F11] border border-white/10 overflow-hidden transition-all duration-500 group-hover:border-cyan-500/50 group-hover:shadow-[0_0_60px_rgba(34,211,238,0.3)]">
                        <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?q=80&w=1974&auto=format&fit=crop')] bg-cover bg-center transition-transform duration-1000 group-hover:scale-110"></div>
                        <div class="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent opacity-90"></div>
                        <div class="absolute bottom-0 left-0 w-full p-12 flex flex-col items-start z-20">
                          <div class="mb-5 px-4 py-1.5 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-sm font-bold tracking-widest backdrop-blur-md">FEATURED PROJECT</div>
                          <h2 class="text-5xl font-black text-white mb-4 italic">原创动态漫 <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-white to-purple-400 animate-gradient-x">Speed Run</span></h2>
                          <p class="text-gray-200 text-xl font-medium mb-8 max-w-lg">用颠覆性AI技术为视频注入原创灵魂，一键生成独一无二的电影级动态漫！</p>
                          <button @click="openCreateModal('原创动态漫')" class="btn-quantum group/btn">
                            <div class="btn-quantum-content"><span>开始原创</span><ArrowRight :size="20" class="group-hover/btn:translate-x-1 transition-transform duration-300"/></div>
                            <div class="btn-quantum-flow"></div><div class="btn-quantum-glow"></div>
                          </button>
                        </div>
                      </div>
                    </div>

                    <div class="col-span-6 h-[380px] rounded-[40px] relative group cursor-pointer perspective-1000">
                      <div class="absolute inset-0 rounded-[40px] bg-[#0F0F11] border border-white/10 overflow-hidden transition-all duration-500 group-hover:border-pink-500/50 group-hover:shadow-[0_0_60px_rgba(236,72,153,0.3)]">
                        <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1614728853913-1e22ba863009?q=80&w=2089&auto=format&fit=crop')] bg-cover bg-center transition-transform duration-1000 group-hover:scale-110"></div>
                        <div class="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent opacity-90"></div>
                        <div class="absolute inset-0 p-12 flex flex-col justify-end items-start z-20">
                          <div class="mb-5 px-4 py-1.5 rounded-full bg-pink-500/20 border border-pink-500/40 text-pink-300 text-sm font-bold tracking-widest backdrop-blur-md">FEATURED PROJECT</div>
                           <h2 class="text-5xl font-black text-white mb-4 italic">二创动态漫 <span class="text-pink-500 inline-block animate-pulse">Speed Run </span></h2>
                          <p class="text-gray-200 text-xl font-medium mb-8 max-w-lg">一键精准复刻高赞视频，瞬间产出国漫级动态漫，助你快速量产流量！</p>
                          <button @click="openCreateModal('二创动态漫')" class="btn-quantum pink-theme group/btn">
                            <div class="btn-quantum-content"><span>开始二创</span><ArrowRight :size="20" class="group-hover/btn:translate-x-1 transition-transform duration-300"/></div>
                            <div class="btn-quantum-flow"></div><div class="btn-quantum-glow"></div>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 数据表格 -->
                  <div class="relative bg-[#0a0a0a]/90 backdrop-blur-xl rounded-[32px] border border-white/10 overflow-hidden flex flex-col min-h-[500px] shadow-2xl hover:border-white/20 transition-colors duration-500 group/table">
                    <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 animate-gradient-x"></div>

                    <div class="p-8 flex justify-between items-center z-10 gap-4">
                      <div class="flex gap-4 shrink-0">
                         <button class="text-lg font-bold text-white px-4 py-2 relative group hover:text-cyan-300 transition-colors">
                           全部作品
                           <span class="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-[3px] bg-cyan-500 rounded-full shadow-[0_0_10px_#22d3ee] group-hover:w-full transition-all duration-300"></span>
                         </button>
                         <button class="text-lg font-bold text-gray-500 px-4 py-2 hover:text-white transition-colors relative group">
                           回收站
                           <span class="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-[3px] bg-gray-500 rounded-full group-hover:w-1/2 transition-all duration-300"></span>
                         </button>
                      </div>

                      <div class="flex items-center gap-3 flex-1 justify-end">
                        <div class="relative group w-48 transition-all focus-within:w-64">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500 group-focus-within:text-cyan-400 transition-colors"><Search :size="16" /></div>
                          <input v-model="filterForm.keyword" type="text" placeholder="搜索名称或ID..." class="w-full bg-[#0a0a0a] border border-white/30 text-white text-base font-medium rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-cyan-500 focus:bg-[#111] hover:bg-[#111] transition-all placeholder-gray-500" />
                        </div>
                        <div class="relative group">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500"><ListFilter :size="16" /></div>
                          <select v-model="filterForm.type" class="appearance-none bg-[#0a0a0a] border border-white/30 text-white text-base font-medium rounded-xl pl-10 pr-8 py-2.5 focus:outline-none focus:border-cyan-500 focus:bg-[#111] hover:bg-[#111] transition-all cursor-pointer w-40">
                            <option value="">所有类型</option><option value="原创动态漫">原创动态漫</option><option value="二创动态漫">二创动态漫</option>
                          </select>
                        </div>
                        <div class="relative group">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500"><Filter :size="16" /></div>
                          <select v-model="filterForm.status" class="appearance-none bg-[#0a0a0a] border border-white/30 text-white text-base font-medium rounded-xl pl-10 pr-8 py-2.5 focus:outline-none focus:border-cyan-500 focus:bg-[#111] hover:bg-[#111] transition-all cursor-pointer w-40">
                            <option value="">所有状态</option><option value="已完成">已完成</option><option value="进行中">进行中</option>
                          </select>
                        </div>
                        <div class="relative group">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500 group-focus-within:text-cyan-400 transition-colors"><Calendar :size="16" /></div>
                          <input v-model="filterForm.date" type="date" class="bg-[#0a0a0a] border border-white/30 text-white text-base font-medium rounded-xl pl-10 pr-4 py-2.5 focus:outline-none focus:border-cyan-500 focus:bg-[#111] hover:bg-[#111] transition-all cursor-pointer placeholder-gray-500 [color-scheme:dark] w-44" />
                        </div>
                      </div>
                    </div>

                    <div class="grid grid-cols-12 px-10 py-6 bg-white/[0.05] border-y border-white/10 text-lg font-black text-white uppercase tracking-widest drop-shadow-md">
                      <div class="col-span-4 pl-6">&nbsp&nbsp&nbsp&nbsp作品名称</div><div class="col-span-2 text-center">作品类型</div><div class="col-span-2 text-center">作品状态</div><div class="col-span-1 text-center">比例</div><div class="col-span-2 text-center">创建日期</div><div class="col-span-1 text-right pr-2">操作</div>
                    </div>

                    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center py-20 gap-6">
                      <div class="w-16 h-16 border-4 border-purple-500/30 border-t-cyan-500 rounded-full animate-spin shadow-[0_0_30px_rgba(34,211,238,0.3)]"></div>
                      <p class="text-gray-400 font-bold text-lg animate-pulse tracking-widest">LOADING DATA...</p>
                    </div>

                    <div v-else class="flex-1 overflow-y-auto custom-scroll p-2 flex flex-col">
                      <div class="flex-1">
                        <div v-for="item in paginatedProjects" :key="item.id" class="grid grid-cols-12 px-8 py-6 items-center rounded-xl hover:bg-white/[0.04] transition-all duration-300 group relative cursor-pointer mb-1 border border-transparent hover:border-white/5 hover:shadow-[0_0_20px_rgba(255,255,255,0.05)]">
                          <div class="absolute left-2 top-1/2 -translate-y-1/2 h-8 w-1 bg-gradient-to-b from-cyan-400 to-purple-500 rounded-full opacity-0 group-hover:opacity-100 group-hover:h-12 transition-all duration-300 shadow-[0_0_15px_#22d3ee]"></div>
                          <div class="col-span-4 flex items-center gap-5 pl-4">
                            <div class="w-14 h-14 rounded-2xl bg-[#151518] border border-white/10 flex items-center justify-center text-3xl shadow-lg group-hover:scale-110 transition-transform duration-300 group-hover:border-purple-500/50 group-hover:text-purple-400 flex-shrink-0">🎬</div>
                            <div class="overflow-hidden">
                              <h3 class="font-bold text-white text-lg mb-1 truncate group-hover:text-cyan-300 transition-colors">{{ item.name }}</h3>
                              <span class="text-xs text-gray-500 font-mono flex items-center gap-2 group-hover:text-gray-400"><span class="w-1.5 h-1.5 rounded-full bg-gray-600 group-hover:bg-cyan-400 group-hover:shadow-[0_0_5px_#22d3ee]"></span> ID: {{ item.id }}</span>
                            </div>
                          </div>
                          <div class="col-span-2 flex justify-center">
                            <div v-if="item.type === '原创动态漫'" class="px-4 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-sm font-bold flex items-center gap-2"><span class="text-xs">✨</span> 原创动态漫</div>
                            <div v-else-if="item.type === '二创动态漫'" class="px-4 py-1.5 rounded-lg bg-pink-500/10 border border-pink-500/30 text-pink-300 text-sm font-bold flex items-center gap-2"><span class="text-xs">🔄</span> 二创动态漫</div>
                             <div v-else class="px-4 py-1.5 rounded-lg bg-gray-500/10 border border-gray-500/30 text-gray-300 text-sm font-bold flex items-center gap-2"><span class="text-xs">📁</span> 未知作品</div>
                          </div>
                          <div class="col-span-2 flex justify-center"><span class="px-4 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-bold tracking-wide">COMPLETED</span></div>
                          <div class="col-span-1 text-center font-mono text-gray-300 text-base font-bold">{{ item.ratio }}</div>
                          <div class="col-span-2 text-center"><div class="font-mono text-base text-gray-300">{{ item.created_at }}</div></div>
                          <div class="col-span-1 flex justify-end gap-2 pr-2">
                            <button @click.stop="handleEnterProject(item)" class="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-cyan-500 hover:text-white transition-all transform hover:-translate-y-1"><LogIn :size="18"/></button>
                            <button @click.stop="handleDelete(item.name)" class="p-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:bg-red-500 hover:text-white transition-all transform hover:-translate-y-1"><Trash2 :size="18"/></button>
                          </div>
                        </div>
                        <div v-if="filteredProjects.length === 0" class="py-20 flex flex-col items-center justify-center text-gray-500/50 gap-3"><Search :size="40" stroke-width="1.5" /><p class="text-sm font-medium">未找到符合条件的作品</p></div>
                      </div>

                      <div v-if="filteredProjects.length > 0" class="py-6 flex justify-between items-center border-t border-white/5 px-4 mt-auto">
                        <div class="text-sm text-gray-500">显示第 <span class="text-white font-bold">{{ (currentPage - 1) * pageSize + 1 }}</span> 到 <span class="text-white font-bold">{{ Math.min(currentPage * pageSize, filteredProjects.length) }}</span> 条</div>
                        <div class="flex items-center gap-2">
                          <button @click="currentPage > 1 ? currentPage-- : null" :disabled="currentPage === 1" class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 text-sm hover:bg-white/10 hover:text-white transition-all disabled:opacity-50"><ChevronLeft :size="16" /> 上一页</button>
                          <span class="px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-bold min-w-[40px] text-center">{{ currentPage }}</span>
                          <button @click="currentPage < totalPages ? currentPage++ : null" :disabled="currentPage === totalPages" class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 text-sm hover:bg-white/10 hover:text-white transition-all disabled:opacity-50">下一页 <ChevronRight :size="16" /></button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="h-12"></div>
                </div>
              </template>
            </main>
          </div>
        </div>
      </div>

      <!-- 3. 创建空间弹窗 -->
      <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="closeModal"></div>
          <div class="relative w-full max-w-[480px] bg-[#18181b] rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden transform transition-all scale-100">
            <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-cyan-500 via-purple-500 to-cyan-500"></div>
            <div class="flex justify-between items-center p-6 pb-2"><h2 class="text-xl font-bold text-white tracking-wide">创建空间</h2><button @click="closeModal" class="text-gray-500 hover:text-white transition-colors"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button></div>
            <div class="p-8 pt-4 space-y-6">
              <div class="space-y-2"><label class="text-sm font-bold text-gray-400 flex justify-between"><span>* 空间名称</span><span class="text-xs text-gray-600">{{ form.name.length }} / 10</span></label><div class="relative group"><input type="text" v-model="form.name" maxlength="10" placeholder="请输入空间名称" class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" /></div></div>
              <div class="space-y-2 relative z-20"><label class="text-sm font-bold text-gray-400">项目类型</label><div class="relative"><button @click="showTypeSelect = !showTypeSelect; showRatioSelect = false" class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-left text-white flex justify-between items-center hover:border-white/20 transition-all"><span>{{ form.type }}</span><svg :class="{'rotate-180': showTypeSelect}" class="w-4 h-4 text-gray-500 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg></button><Transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95"><div v-if="showTypeSelect" class="absolute top-full left-0 w-full mt-2 bg-[#18181b] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-30"><div v-for="option in typeOptions" :key="option" @click="form.type = option; showTypeSelect = false" class="px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-cyan-400 cursor-pointer transition-colors flex items-center justify-between">{{ option }}<span v-if="form.type === option" class="text-cyan-400">✓</span></div></div></Transition></div></div>
              <div class="space-y-2 relative z-10"><label class="text-sm font-bold text-gray-400">视频比例</label><div class="relative"><button @click="showRatioSelect = !showRatioSelect; showTypeSelect = false" class="w-full bg-[#09090b] border border-white/10 rounded-xl px-4 py-3 text-left text-white flex justify-between items-center hover:border-white/20 transition-all"><span>{{ form.ratio }}</span><svg :class="{'rotate-180': showRatioSelect}" class="w-4 h-4 text-gray-500 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg></button><Transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95"><div v-if="showRatioSelect" class="absolute top-full left-0 w-full mt-2 bg-[#18181b] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-30"><div v-for="option in ratioOptions" :key="option" @click="form.ratio = option; showRatioSelect = false" class="px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-cyan-400 cursor-pointer transition-colors flex items-center justify-between">{{ option }}<span v-if="form.ratio === option" class="text-cyan-400">✓</span></div></div></Transition></div></div>
            </div>
            <div class="p-6 pt-2 flex gap-4"><button @click="closeModal" class="flex-1 py-3.5 rounded-xl bg-white/5 text-gray-400 font-bold hover:bg-white/10 hover:text-white transition-colors">取消</button><button @click="handleCreate" class="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-cyan-400 to-green-400 text-black font-black hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] active:scale-95 transition-all">立即创建</button></div>
          </div>
        </div>
      </Transition>

      <!-- 4. 二创动态漫弹窗 -->
      <SecondaryCreationModal
        :isOpen="showSecondaryModal"
        :projectName="currentProject?.name || ''"
        :projectId="currentProject?.id || ''"
        @close="showSecondaryModal = false"
        @extract="handleExtractSuccess"
        @next="enterWorkbench"
      />

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, Component, nextTick, onUnmounted, computed, watch } from 'vue';
import Login from './components/Login.vue';
import SecondaryCreationModal from './components/SecondaryCreationModal.vue';
import VideoGenerationWorkbench from './components/VideoGenerationWorkbench.vue';
// 🔥 1. 引入新组件
import YunManBanana from './components/YunManBanana.vue';

import GlobalToast from './components/GlobalToast.vue';
import { useToast } from './utils/toast';

const toast = useToast();
import {
  Home, Cloud, MonitorPlay, Box, MessageCircle, Mail, Settings,
  Megaphone, Bell, Plus, ArrowRight, Trash2, LogIn, Copy, Link,
  Search, Filter, Calendar, ListFilter, ChevronLeft, ChevronRight
} from 'lucide-vue-next';

// === 🔥 核心状态：视图控制 ===
// 默认为 'home'，点击侧边栏可以切换为 'banana'
const currentView = ref('home');

// 切换视图的函数
const switchView = (viewName: string) => {
  currentView.value = viewName;
};

// 🔥🔥🔥 新增：Sora 网页版跳转函数
const openSoraWeb = () => {
  // 使用 window.open 在新标签页打开网址
  // 这会自动调用用户的默认浏览器（如谷歌浏览器）打开
  window.open('http://yunybman.yijiarj.cn/index/sora2/index', '_blank');
};

let heartbeatTimer: any = null;
const pageLoading = ref(true);

onMounted(async () => {
  pageLoading.value = true;
  await checkLoginStatus();
  pageLoading.value = false;
});

const isLoggedIn = ref(false);
const expiryDate = ref('Loading...');
const isExpired = ref(false);
const projects = ref<Project[]>([]);
const loading = ref(true);
const machineId = ref('Unknown');
const bgCanvas = ref<HTMLCanvasElement | null>(null);
let animationId: number;

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

const openCreateModal = (type: string = '原创动态漫') => {
  form.value = { name: '', type: type, ratio: '16:9' };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  showTypeSelect.value = false;
  showRatioSelect.value = false;
};

const handleCreate = async () => {
  if (!form.value.name.trim()) {
    toast.warning("请输入空间名称");
    return;
  }

  // 🔥 新增：检查是否已存在同名项目
  const isDuplicate = projects.value.some(
    project => project.name.trim().toLowerCase() === form.value.name.trim().toLowerCase()
  );

  if (isDuplicate) {
    toast.error(`已存在名为 "${form.value.name}" 的空间，请使用其他名称`);
    return;
  }

  try {
    const payload = {
      name: form.value.name,
      type: form.value.type || '原创动态漫',
      ratio: form.value.ratio || '16:9',
      id: 0,
      created_at: ""
    };

    const response = await fetch('http://127.0.0.1:8000/api/create_project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      toast.error(`创建失败: ${errorData.detail}`);
      return;
    }

    closeModal();
    loading.value = true;

    // 刷新项目列表
    setTimeout(async () => {
      await fetchProjects();
    }, 500);

  } catch (e) {
    toast.error("连接后端失败");
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
  } finally {
    loading.value = false;
  }
};

const handleDelete = async (name: string) => {
  if(!confirm(`确定要永久删除项目 "${name}" 吗？`)) return;
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/delete_project/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      await fetchProjects();
    } else {
       toast.error("删除失败");
    }
  } catch(e) {
     toast.error("网络错误");
  }
};

const handleLoginSuccess = async () => {
  pageLoading.value = true;
  isLoggedIn.value = true;
  await nextTick();
  await fetchProjects();
  initCanvas();
  await checkLoginStatus();
  pageLoading.value = false;
};

onMounted(() => {
    checkLoginStatus();
});

onUnmounted(() => {
    cancelAnimationFrame(animationId);
    stopHeartbeat();
    window.removeEventListener('mousemove', () => {});
});

const checkLoginStatus = async (isBackground = false) => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/status');
    const data = await res.json();
    if (data.activated) {
      isLoggedIn.value = true;
      if (data.info && data.info.machine_id) {
          machineId.value = data.info.machine_id;
      } else {
          try {
             const idRes = await fetch('http://127.0.0.1:8000/api/machine_id');
             const idData = await idRes.json();
             machineId.value = idData.machine_id || "Unknown";
          } catch(e) { machineId.value = "Unknown"; }
      }
      if (data.info && data.info.expiry_date) {
        expiryDate.value = data.info.expiry_date;
        const today = new Date().toISOString().split('T')[0];
        const serverDate = String(data.info.expiry_date).substring(0, 10);
        if (serverDate < today) {
            handleKickOut("授权已过期");
            return;
        }
        isExpired.value = false;
      } else {
        expiryDate.value = '永久授权';
      }
      if (!isBackground) {
        await fetchProjects();
        await nextTick();
        if (!animationId) {
          initCanvas();
        }
      }
      if (!heartbeatTimer) startHeartbeat();
    } else {
      const reason = data.info && data.info.msg ? data.info.msg : "授权已失效";
      handleKickOut(reason);
    }
  } catch (e) {
  }
};

const handleKickOut = (reason: string) => {
    if (isLoggedIn.value) {
        stopHeartbeat();
        isLoggedIn.value = false;
         toast.error(`系统强制下线通知：\n${reason}`);
        projects.value = [];
    }
};

const startHeartbeat = () => {
    stopHeartbeat();
    heartbeatTimer = setInterval(() => {
        checkLoginStatus(true);
    }, 15000);
};

const stopHeartbeat = () => {
    if (heartbeatTimer) {
        clearInterval(heartbeatTimer);
        heartbeatTimer = null;
    }
};

const copyMachineId = async () => {
  try {
    await navigator.clipboard.writeText(machineId.value);
    toast.success('设备ID已复制到剪贴板！');
  } catch (err) {
  }
};

const filterForm = ref({
  keyword: '',
  type: '',
  status: '',
  date: ''
});

const filteredProjects = computed(() => {
  if (!projects.value) return [];
  return projects.value.filter(item => {
    const matchName = !filterForm.value.keyword ||
      item.name.toLowerCase().includes(filterForm.value.keyword.toLowerCase()) ||
      String(item.id).includes(filterForm.value.keyword);
    const matchType = !filterForm.value.type || item.type === filterForm.value.type;
    let matchStatus = true;
    if (filterForm.value.status === '已完成') {
       matchStatus = true;
    } else if (filterForm.value.status === '进行中') {
       matchStatus = false;
    }
    const matchDate = !filterForm.value.date || item.created_at.includes(filterForm.value.date);
    return matchName && matchType && matchStatus && matchDate;
  });
});

const currentPage = ref(1);
const pageSize = 10;

watch(filterForm, () => {
  currentPage.value = 1;
}, { deep: true });

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredProjects.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(filteredProjects.value.length / pageSize);
});

const showWorkbench = ref(false);
const showSecondaryModal = ref(false);
const currentProject = ref<Project | null>(null);
const currentClips = ref<any[]>([]);

const handleEnterProject = async (project: Project) => {
  currentProject.value = project;
  if (project.type === '二创动态漫' || project.type === 'secondary') {
    showSecondaryModal.value = true;
  } else {
     toast.info(`进入项目: ${project.name} (类型: ${project.type}) - 功能开发中`);
  }
};

const enterWorkbench = () => {
  showWorkbench.value = true;
  showSecondaryModal.value = false;
};

const exitWorkbench = () => {
  showWorkbench.value = false;
  currentClips.value = [];
  fetchProjects();
};

const handleExtractSuccess = (data: any) => {
  currentClips.value = data;
};

const initCanvas = () => {
  const canvas = document.getElementById('bgCanvas') as HTMLCanvasElement;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  let width: number, height: number;
  let particles: any[] = [];
  let mouse = { x: null as number | null, y: null as number | null, radius: 200 };
  const handleMouseMove = (event: MouseEvent) => {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
  };
  const handleMouseOut = () => {
    mouse.x = null;
    mouse.y = null;
  };
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('mouseout', handleMouseOut);
  const properties = {
    bgColor: 'rgba(5, 5, 5, 0)',
    particleColor: 'rgba(139, 92, 246, 0.8)',
    particleRadius: 2,
    particleCount: 150,
    particleVelocity: 0.8,
    lineLength: 120,
  };
  const initSize = () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  };
  class Particle {
    x: number; y: number; velocityX: number; velocityY: number; size: number;
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.velocityX = Math.random() * (properties.particleVelocity * 2) - properties.particleVelocity;
      this.velocityY = Math.random() * (properties.particleVelocity * 2) - properties.particleVelocity;
      this.size = Math.random() * 2 + 1;
    }
    position() {
      if(this.x > width || this.x < 0) this.velocityX *= -1;
      if(this.y > height || this.y < 0) this.velocityY *= -1;
      this.x += this.velocityX;
      this.y += this.velocityY;
    }
    reDraw() {
      if(!ctx) return;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.closePath();
      ctx.fillStyle = properties.particleColor;
      ctx.fill();
    }
  }
  const drawLines = () => {
    if(!ctx) return;
    let x1, y1, x2, y2, length, opacity;
    for (let i in particles) {
      for (let j in particles) {
        x1 = particles[i].x; y1 = particles[i].y;
        x2 = particles[j].x; y2 = particles[j].y;
        length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        if (length < properties.lineLength) {
          opacity = 1 - length / properties.lineLength;
          ctx.lineWidth = 0.5;
          ctx.strokeStyle = `rgba(139, 92, 246, ${opacity})`;
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
          ctx.stroke();
          ctx.closePath();
        }
      }
      if (mouse.x != null && mouse.y != null) {
        let mouseDist = Math.sqrt(Math.pow(mouse.x - particles[i].x, 2) + Math.pow(mouse.y - particles[i].y, 2));
        if (mouseDist < mouse.radius) {
          ctx.lineWidth = 1;
          ctx.strokeStyle = `rgba(59, 130, 246, ${1 - mouseDist/mouse.radius})`;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.stroke();
          ctx.closePath();
        }
      }
    }
  };
  const loop = () => {
    ctx!.clearRect(0, 0, width, height);
    for (let i in particles) {
      particles[i].position();
      particles[i].reDraw();
    }
    drawLines();
    animationId = requestAnimationFrame(loop);
  };
  const initParticles = () => {
    particles = [];
    let count = window.innerWidth > 1000 ? 150 : 80;
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
    loop();
  };
  initSize();
  window.addEventListener('resize', () => {
    initSize();
    initParticles();
  });
  initParticles();
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
    h('div', { class: 'absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 pointer-events-none' })
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
::-webkit-calendar-picker-indicator {
    filter: invert(1);
    opacity: 0.6;
    cursor: pointer;
}
::-webkit-calendar-picker-indicator:hover {
    opacity: 1;
}

.btn-quantum {
  position: relative;
  padding: 14px 36px;
  background: rgba(18, 18, 27, 0.6);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(34, 211, 238, 0.2);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.1), inset 0 0 20px rgba(34, 211, 238, 0.05);
}

.btn-quantum-content {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 1px;
  background: linear-gradient(to right, #fff, #cbd5e1);
  -webkit-background-clip: text;
  color: transparent;
  transition: all 0.3s ease;
}

.btn-quantum:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: rgba(34, 211, 238, 0.6);
  box-shadow:
    0 10px 40px rgba(34, 211, 238, 0.3),
    0 0 0 2px rgba(34, 211, 238, 0.1);
}

.btn-quantum:active {
  transform: scale(0.92);
  box-shadow: 0 2px 10px rgba(34, 211, 238, 0.2);
}

.btn-quantum-flow {
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.4), transparent);
  transform: skewX(-20deg);
  transition: left 0.5s;
}

.btn-quantum:hover .btn-quantum-flow {
  left: 100%;
  transition: left 0.6s ease-in-out;
}

.btn-quantum-glow {
  position: absolute;
  bottom: -20px; left: 50%;
  transform: translateX(-50%);
  width: 60%; height: 20px;
  background: rgba(34, 211, 238, 0.6);
  filter: blur(20px);
  opacity: 0;
  transition: opacity 0.4s;
}
.btn-quantum:hover .btn-quantum-glow { opacity: 1; }

.btn-quantum.pink-theme {
  border-color: rgba(236, 72, 153, 0.2);
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.1), inset 0 0 20px rgba(236, 72, 153, 0.05);
}
.btn-quantum.pink-theme:hover {
  border-color: rgba(236, 72, 153, 0.6);
  box-shadow: 0 10px 40px rgba(236, 72, 153, 0.3);
}
.btn-quantum.pink-theme .btn-quantum-flow {
  background: linear-gradient(90deg, transparent, rgba(236, 72, 153, 0.4), transparent);
}
.btn-quantum.pink-theme .btn-quantum-glow {
  background: rgba(236, 72, 153, 0.6);
}

.btn-liquid-shine {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 20px -10px rgba(79, 70, 229, 0.5);
}

.btn-liquid-shine:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 20px 30px -10px rgba(79, 70, 229, 0.6);
}

.btn-liquid-shine:active { transform: scale(0.95); }

.btn-social-flow {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ccc;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  transition: all 0.3s ease;
}

.btn-social-flow:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}
.btn-social-flow:active { transform: scale(0.95); }

.btn-social-flow.green-flow:hover {
  border-color: #22c55e;
  box-shadow: 0 0 15px rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

.btn-social-flow.blue-flow:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.btn-social-flow::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-25deg);
  transition: none;
}

.btn-social-flow:hover::after {
  animation: shine-flow 0.75s ease;
}

@keyframes shine-flow {
  0% { left: -100%; }
  100% { left: 200%; }
}

.glass-layout { backdrop-filter: blur(0px); }
.text-glow { text-shadow: 0 0 15px rgba(34, 211, 238, 0.6); }
.perspective-1000 { perspective: 1200px; }

@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient 3s ease-in-out infinite, float 3s ease-in-out infinite;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>