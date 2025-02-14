<!-- src/components/chat/ChatView.vue -->
<template>
  <div class="relative h-full w-full">
<!-- Content -->
<div class="relative h-screen">
  <div class="py-10 lg:py-14">
    <!-- Title -->
    <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto text-center">
      <a class="inline-block mb-4 flex-none focus:outline-none focus:opacity-80" href="/" aria-label="SI Agent">
       
       <SILogo/>
      </a>

      <h1  class="text-3xl font-bold text-gray-800 sm:text-4xl dark:text-white">
        Welcome to SI Agents
      </h1>
      <p class="mt-3 text-gray-600 dark:text-neutral-400">
        Your AI-powered agent
      </p>
    </div>
    <!-- End Title -->
<!-- 
    <div v-for="msgItem in messagesData" 
        :key="msgItem.conversation_id"
        class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100">
        <div class="font-medium text-gray-800 truncate">
         Message  {{ msgItem.event	 }}
        </div>
        <div class="text-xs text-gray-500">
          {{msgItem.data }}
        </div>
      </div> -->
    <ul class="mt-16 space-y-5">
      <!-- Chat Bubble -->
      <li   v-for="msgItem in messagesData" 
      :key="msgItem.conversation_id"
       class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <ChatBubble :data="msgItem.data"  />
      </li>
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <SILogo/>

        <div class="space-y-3">
          <h2 class="font-medium text-gray-800 dark:text-white">
            How can we help?
          </h2>
          <div class="space-y-1.5">
            <p class="mb-1.5 text-sm text-gray-800 dark:text-white">
              You can ask questions like:
            </p>
            <ul class="list-disc list-outside space-y-1.5 ps-3.5">
              <li class="text-sm text-gray-800 dark:text-white">
                What's Preline UI?
              </li>

              <li class="text-sm text-gray-800 dark:text-white">
                How many Starter Pages & Examples are there?
              </li>

              <li class="text-sm text-gray-800 dark:text-white">
                Is there a PRO version?
              </li>
            </ul>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                what's preline ui?
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Preline UI is an open-source set of prebuilt UI components based on the utility-first Tailwind CSS framework.
            </p>
            <div class="space-y-1.5">
              <p class="text-sm text-gray-800 dark:text-white">
                Here're some links to get started
              </p>
              <ul>
                <li>
                  <a class="text-sm text-blue-600 decoration-2 hover:underline focus:outline-none focus:underline font-medium dark:text-blue-500 dark:hover:text-blue-400" href="../docs/index.html">
                    Installation Guide
                  </a>
                </li>
                <li>
                  <a class="text-sm text-blue-600 decoration-2 hover:underline focus:outline-none focus:underline font-medium dark:text-blue-500 dark:hover:text-blue-400" href="../docs/frameworks.html">
                    Framework Guides
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <!-- End Card -->

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                what's preline ui figma?
              </p>
              <div class="mt-3">
                <button type="button" class="p-2 inline-flex items-center gap-x-2 text-xs font-semibold rounded-lg border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-white dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  Voice message
                </button>
              </div>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Preline UI Figma is the largest free design system for Figma, crafted with Tailwind CSS styles and Preline UI components with extra top-notch additions.
            </p>
            <div class="space-y-1.5">
              <p class="text-sm text-gray-800 dark:text-white">
                With the features like:
              </p>
              <ul class="list-disc list-outside space-y-1.5 ps-3.5">
                <li class="text-sm text-gray-800 dark:text-white">
                  12-column Grid System
                </li>

                <li class="text-sm text-gray-800 dark:text-white">
                  Easily find UI elements
                </li>

                <li class="text-sm text-gray-800 dark:text-white">
                  Variants and Properties
                </li>

                <li class="text-sm text-gray-800 dark:text-white">
                  Tailwind CSS Color styles
                </li>

                <li class="text-sm text-gray-800 dark:text-white">
                  Auto layout and constraints
                </li>
              </ul>
            </div>
          </div>
          <!-- End Card -->

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                create a table example with preline using avatars, badges and progress bars
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Hold on a sec...
            </p>
          </div>
          <!-- End Card -->

          <!-- Table Section -->
          <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden dark:bg-neutral-900 dark:border-neutral-700">
            <!-- Table -->
            <div class="-m-1.5 overflow-x-auto">
              <div class="p-1.5 min-w-full inline-block align-middle">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-neutral-700">
                  <thead class="bg-gray-50 dark:bg-neutral-800">
                    <tr>
                      <th scope="col" class="px-6 py-3 text-start">
                        <div class="flex items-center gap-x-2">
                          <span class="text-xs font-semibold uppercase tracking-wide text-gray-800 dark:text-neutral-200">
                            Name
                          </span>
                        </div>
                      </th>

                      <th scope="col" class="px-6 py-3 text-start">
                        <div class="flex items-center gap-x-2">
                          <span class="text-xs font-semibold uppercase tracking-wide text-gray-800 dark:text-neutral-200">
                            Status
                          </span>
                        </div>
                      </th>

                      <th scope="col" class="px-6 py-3 text-start">
                        <div class="flex items-center gap-x-2">
                          <span class="text-xs font-semibold uppercase tracking-wide text-gray-800 dark:text-neutral-200">
                            Portfolio
                          </span>
                        </div>
                      </th>

                      <th scope="col" class="px-6 py-3 text-start">
                        <div class="flex items-center gap-x-2">
                          <span class="text-xs font-semibold uppercase tracking-wide text-gray-800 dark:text-neutral-200">
                            Created
                          </span>
                        </div>
                      </th>
                    </tr>
                  </thead>

                  <tbody class="divide-y divide-gray-200 dark:divide-neutral-700">
                    <tr>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <img class="inline-block size-[38px] rounded-full" src="https://images.unsplash.com/photo-1531927557220-a9e23c1e4794?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=300&h=300&q=80" alt="Avatar">
                            <div class="grow">
                              <span class="block text-sm font-semibold text-gray-800 dark:text-neutral-200">Christina Bersh</span>
                              <span class="block text-sm text-gray-500 dark:text-neutral-500">christina@site.com</span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="inline-flex items-center gap-1.5 py-0.5 px-2 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                            </svg>
                            Active
                          </span>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <span class="text-xs text-gray-500 dark:text-neutral-500">1/5</span>
                            <div class="flex w-full h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-neutral-700" role="progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100">
                              <div class="flex flex-col justify-center overflow-hidden bg-gray-800 text-xs text-white text-center whitespace-nowrap dark:bg-neutral-200" style="width: 25%"></div>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="text-sm text-gray-500 dark:text-neutral-500">28 Dec, 12:12</span>
                        </div>
                      </td>
                    </tr>

                    <tr>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <img class="inline-block size-[38px] rounded-full" src="https://images.unsplash.com/photo-1568602471122-7832951cc4c5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=facearea&facepad=2&w=300&h=300&q=80" alt="Avatar">
                            <div class="grow">
                              <span class="block text-sm font-semibold text-gray-800 dark:text-neutral-200">David Harrison</span>
                              <span class="block text-sm text-gray-500 dark:text-neutral-500">david@site.com</span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="inline-flex items-center gap-1.5 py-0.5 px-2 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
                            <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                            </svg>
                            Warning
                          </span>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <span class="text-xs text-gray-500 dark:text-neutral-500">3/5</span>
                            <div class="flex w-full h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-neutral-700" role="progressbar" aria-valuenow="78" aria-valuemin="0" aria-valuemax="100">
                              <div class="flex flex-col justify-center overflow-hidden bg-gray-800 text-xs text-white text-center whitespace-nowrap dark:bg-neutral-200" style="width: 78%"></div>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="text-sm text-gray-500 dark:text-neutral-500">20 Dec, 09:27</span>
                        </div>
                      </td>
                    </tr>

                    <tr>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <span class="inline-flex items-center justify-center size-[38px] rounded-full bg-gray-300 dark:bg-neutral-700">
                              <span class="font-medium text-gray-800 leading-none dark:text-neutral-200">A</span>
                            </span>
                            <div class="grow">
                              <span class="block text-sm font-semibold text-gray-800 dark:text-neutral-200">Anne Richard</span>
                              <span class="block text-sm text-gray-500 dark:text-neutral-500">anne@site.com</span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="inline-flex items-center gap-1.5 py-0.5 px-2 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                            </svg>
                            Active
                          </span>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <span class="text-xs text-gray-500 dark:text-neutral-500">5/5</span>
                            <div class="flex w-full h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-neutral-700" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100">
                              <div class="flex flex-col justify-center overflow-hidden bg-gray-800 text-xs text-white text-center whitespace-nowrap dark:bg-neutral-200" style="width: 100%"></div>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="text-sm text-gray-500 dark:text-neutral-500">18 Dec, 15:20</span>
                        </div>
                      </td>
                    </tr>

                    <tr>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <img class="inline-block size-[38px] rounded-full" src="https://images.unsplash.com/photo-1541101767792-f9b2b1c4f127?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&&auto=format&fit=facearea&facepad=3&w=300&h=300&q=80" alt="Avatar">
                            <div class="grow">
                              <span class="block text-sm font-semibold text-gray-800 dark:text-neutral-200">Samia Kartoon</span>
                              <span class="block text-sm text-gray-500 dark:text-neutral-500">samia@site.com</span>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="inline-flex items-center gap-1.5 py-0.5 px-2 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                            </svg>
                            Active
                          </span>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <div class="flex items-center gap-x-3">
                            <span class="text-xs text-gray-500 dark:text-neutral-500">0/5</span>
                            <div class="flex w-full h-1.5 bg-gray-200 rounded-full overflow-hidden dark:bg-neutral-700" role="progressbar" aria-valuenow="1" aria-valuemin="0" aria-valuemax="100">
                              <div class="flex flex-col justify-center overflow-hidden bg-gray-800 text-xs text-white text-center whitespace-nowrap dark:bg-neutral-200" style="width: 1%"></div>
                            </div>
                          </div>
                        </div>
                      </td>
                      <td class="size-px whitespace-nowrap">
                        <div class="px-6 py-3">
                          <span class="text-sm text-gray-500 dark:text-neutral-500">18 Dec, 15:20</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <!-- End Table -->
          </div>
          <!-- End Table Section -->

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                show me the code
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Of course!
            </p>
          </div>
          <!-- End Card -->

          <div class="mt-3 flex-none min-w-full bg-gray-800 font-mono text-sm p-5 rounded-lg dark:bg-neutral-800"><span class="text-red-500"><</span><span class="text-red-500">table <span class="text-gray-300">class="<span class="text-sky-400">min-w-full divide-y divide-gray-200 dark:divide-neutral-700</span>"</span><span class="text-red-500">></span><span class="block"></span>  <span class="ms-5 text-red-500"><</span><span class="text-red-500">thead <span class="text-gray-300">class="<span class="text-sky-400">bg-gray-50 dark:bg-neutral-800</span>"</span><span class="text-red-500">></span><span class="block"></span><span class="text-red-500">    <span class="ms-10 text-gray-500 dark:text-neutral-500">...</span></span></span></span></div>

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                quiz me about tailwindcss
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Sure!
            </p>
          </div>
          <!-- End Card -->

          <div>
            <button type="button" class="mb-2.5 me-1.5 py-2 px-3 inline-flex justify-center items-center gap-x-2 rounded-lg border border-blue-600 bg-white text-blue-600 align-middle hover:bg-blue-50 focus:outline-none focus:bg-blue-50 text-sm dark:bg-neutral-900 dark:text-blue-500 dark:border-blue-500 dark:hover:text-blue-400 dark:hover:border-blue-400 dark:focus:text-blue-400 dark:focus:border-blue-400">
              Is Tailwind CSS a free library?
            </button>
            <button type="button" class="mb-2.5 me-1.5 py-2 px-3 inline-flex justify-center items-center gap-x-2 rounded-lg border border-blue-600 bg-white text-blue-600 align-middle hover:bg-blue-50 focus:outline-none focus:bg-blue-50 text-sm dark:bg-neutral-900 dark:text-blue-500 dark:border-blue-500 dark:hover:text-blue-400 dark:hover:border-blue-400 dark:focus:text-blue-400 dark:focus:border-blue-400">
              What's the latest Tailwind CSS version?
            </button>
            <button type="button" class="mb-2.5 me-1.5 py-2 px-3 inline-flex justify-center items-center gap-x-2 rounded-lg border border-blue-600 bg-white text-blue-600 align-middle hover:bg-blue-50 focus:outline-none focus:bg-blue-50 text-sm dark:bg-neutral-900 dark:text-blue-500 dark:border-blue-500 dark:hover:text-blue-400 dark:hover:border-blue-400 dark:focus:text-blue-400 dark:focus:border-blue-400">
              Is it a utility-class based?
            </button>
          </div>

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                generate 3-dimensional abstract images
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Here you go...
            </p>
          </div>
          <!-- End Card -->

          <div class="grid grid-cols-2 gap-1 rounded-lg overflow-hidden">
            <div class="aspect-w-16 aspect-h-9">
              <img class="w-full object-cover" src="https://images.unsplash.com/photo-1677644334825-0eb411012ac0?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=560&q=80" alt="Deep Learning">
            </div>
            <div class="aspect-w-16 aspect-h-9">
              <img class="w-full object-cover" src="https://images.unsplash.com/photo-1680868543815-b8666dba60f7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=560&q=80" alt="Deep Learning">
            </div>
            <div class="aspect-w-16 aspect-h-9">
              <img class="w-full object-cover" src="https://images.unsplash.com/photo-1680193895115-b51b4ed5392f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=560&q=80" alt="Deep Learning">
            </div>
            <div class="aspect-w-16 aspect-h-9">
              <img class="w-full object-cover" src="https://images.unsplash.com/photo-1680587590161-3a1dd77a7609?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=560&q=80" alt="Deep Learning">
            </div>
          </div>

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                what's tailwindcss?
              </p>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="max-w-4xl py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <svg class="shrink-0 size-[38px] rounded-full" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="38" height="38" rx="6" fill="#2563EB"/>
          <path d="M10 28V18.64C10 13.8683 14.0294 10 19 10C23.9706 10 28 13.8683 28 18.64C28 23.4117 23.9706 27.28 19 27.28H18.25" stroke="white" stroke-width="1.5"/>
          <path d="M13 28V18.7552C13 15.5104 15.6863 12.88 19 12.88C22.3137 12.88 25 15.5104 25 18.7552C25 22 22.3137 24.6304 19 24.6304H18.25" stroke="white" stroke-width="1.5"/>
          <ellipse cx="19" cy="18.6554" rx="3.75" ry="3.6" fill="white"/>
        </svg>

        <div class="grow max-w-[90%] md:max-w-2xl w-full space-y-3">
          <!-- Card -->
          <div class="space-y-3">
            <p class="text-sm text-gray-800 dark:text-white">
              Tailwind CSS is an open source CSS framework. The main feature of this library is that, unlike other CSS frameworks like Bootstrap, it does not provide a series of predefined classes for elements such as buttons or tables.
            </p>
            <div class="space-y-1.5">
              <ul>
                <li>
                  <a class="text-sm text-blue-600 decoration-2 hover:underline focus:outline-none focus:underline font-medium dark:text-blue-500 dark:hover:text-blue-400" href="#">
                    Get started with Tailwind CSS
                  </a>
                </li>
                <li>
                  <a class="text-sm text-blue-600 decoration-2 hover:underline focus:outline-none focus:underline font-medium dark:text-blue-500 dark:hover:text-blue-400" href="#">
                    Tailwind CSS Installation guide
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <!-- End Card -->

          <!-- Button Group -->
          <div>
            <div class="sm:flex sm:justify-between">
              <div>
                <div class="inline-flex border border-gray-200 rounded-full p-0.5 dark:border-neutral-700">
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
                  </button>
                  <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-full text-gray-500 hover:bg-blue-100 hover:text-blue-800 focus:z-10 focus:outline-none focus:bg-blue-100 focus:text-blue-800 dark:text-neutral-500 dark:hover:bg-blue-900 dark:hover:text-blue-200 dark:focus:bg-blue-900 dark:focus:text-blue-200">
                    <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  </button>
                </div>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
                  Copy
                </button>
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                  Share
                </button>
              </div>

              <div class="mt-1 sm:mt-0">
                <button type="button" class="py-2 px-3 inline-flex items-center gap-x-2 text-sm rounded-full border border-transparent text-gray-500 hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:text-neutral-400 dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
                  <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
                  New answer
                </button>
              </div>
            </div>
          </div>
          <!-- End Button Group -->
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <div>
              <div class="text-end">
                <button type="button" class="ms-1.5 py-2 px-3 inline-flex justify-center items-center gap-x-2 rounded-lg border border-blue-600 bg-white text-blue-600 align-middle hover:bg-blue-50 focus:outline-none focus:bg-blue-50 text-sm dark:bg-neutral-900 dark:text-blue-500 dark:border-blue-500 dark:hover:text-blue-400 dark:hover:border-blue-400 dark:focus:text-blue-400 dark:focus:border-blue-400">
                  What is the use of Tailwind CSS?
                </button>
                <button type="button" class="ms-1.5 py-2 px-3 inline-flex justify-center items-center gap-x-2 rounded-lg border border-blue-600 bg-white text-blue-600 align-middle hover:bg-blue-50 focus:outline-none focus:bg-blue-50 text-sm dark:bg-neutral-900 dark:text-blue-500 dark:border-blue-500 dark:hover:text-blue-400 dark:hover:border-blue-400 dark:focus:text-blue-400 dark:focus:border-blue-400">
                  What is the difference between Tailwind CSS and CSS?
                </button>
              </div>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->

      <!-- Chat Bubble -->
      <li class="py-2 sm:py-4">
        <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto">
          <div class="max-w-2xl flex gap-x-2 sm:gap-x-4">
            <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
              <span class="text-sm font-medium text-white leading-none">AZ</span>
            </span>

            <div class="grow mt-2 space-y-3">
              <p class="text-gray-800 dark:text-neutral-200">
                2 files uploaded
              </p>

              <ul class="flex flex-col justify-end text-start -space-y-px">
                <li class="flex items-center gap-x-2 p-3 text-sm bg-white border text-gray-800 first:rounded-t-lg first:mt-0 last:rounded-b-lg dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-200">
                  <div class="w-full flex justify-between truncate">
                    <span class="me-3 flex-1 w-0 truncate">
                      resume_web_ui_developer.csv
                    </span>
                    <button type="button" class="flex items-center gap-x-2 text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600 whitespace-nowrap dark:text-neutral-500 dark:hover:text-blue-500 dark:focus:text-blue-500">
                      <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                      Download
                    </button>
                  </div>
                </li>
                <li class="flex items-center gap-x-2 p-3 text-sm bg-white border text-gray-800 first:rounded-t-lg first:mt-0 last:rounded-b-lg dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-200">
                  <div class="w-full flex justify-between truncate">
                    <span class="me-3 flex-1 w-0 truncate">
                      coverletter_web_ui_developer.pdf
                    </span>
                    <button type="button" class="flex items-center gap-x-2 text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600 whitespace-nowrap dark:text-neutral-500 dark:hover:text-blue-500 dark:focus:text-blue-500">
                      <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                      Download
                    </button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </li>
      <!-- End Chat Bubble -->
    </ul>
  </div>

  <div class="sticky bottom-0 z-10 bg-white border-t border-gray-200 pt-2 pb-3 sm:pt-4 sm:pb-6 dark:bg-neutral-900 dark:border-neutral-700">
    <!-- Textarea -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-0">
      <div class="flex justify-between items-center mb-3">
        <button type="button" class="inline-flex justify-center items-center gap-x-2 rounded-lg font-medium text-gray-800 hover:text-blue-600 focus:outline-none focus:text-blue-600 text-xs sm:text-sm dark:text-neutral-200 dark:hover:text-blue-500 dark:focus:text-blue-500">
          <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          New chat
        </button>

        <button type="button" class="py-1.5 px-2 inline-flex items-center gap-x-2 text-xs font-medium rounded-lg border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-white dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
          <svg class="size-3" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5z"/>
          </svg>
          Stop generating
        </button>
      </div>

      <!-- Input -->
      <div class="relative">
        <textarea class="p-4 pb-12 block w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600" placeholder="Ask me anything..."></textarea>

        <!-- Toolbar -->
        <div class="absolute bottom-px inset-x-px p-2 rounded-b-lg bg-white dark:bg-neutral-900">
          <div class="flex justify-between items-center">
            <!-- Button Group -->
            <div class="flex items-center">
              <!-- Mic Button -->
              <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-10 focus:outline-none focus:bg-gray-100 dark:text-neutral-500 dark:hover:bg-neutral-700 dark:focus:bg-neutral-700">
                <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><line x1="9" x2="15" y1="15" y2="9"/></svg>
              </button>
              <!-- End Mic Button -->

              <!-- Attach Button -->
              <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-10 focus:outline-none focus:bg-gray-100 dark:text-neutral-500 dark:hover:bg-neutral-700 dark:focus:bg-neutral-700">
                <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
              </button>
              <!-- End Attach Button -->
            </div>
            <!-- End Button Group -->

            <!-- Button Group -->
            <div class="flex items-center gap-x-1">
              <!-- Mic Button -->
              <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-10 focus:outline-none focus:bg-gray-100 dark:text-neutral-500 dark:hover:bg-neutral-700 dark:focus:bg-neutral-700">
                <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
              </button>
              <!-- End Mic Button -->

              <!-- Send Button -->
              <button type="button" class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-white bg-blue-600 hover:bg-blue-500 focus:z-10 focus:outline-none focus:bg-blue-500">
                <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083l6-15Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z"/>
                </svg>
              </button>
              <!-- End Send Button -->
            </div>
            <!-- End Button Group -->
          </div>
        </div>
        <!-- End Toolbar -->
      </div>
      <!-- End Input -->
    </div>
    <!-- End Textarea -->
  </div>
</div>
<!-- End Content -->
 
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { useRoute, useRouter } from 'vue-router'
import SILogo from '@/components/icons/SILogo.vue' 
import axios from 'axios'
import ChatBubble from '@/components/ChatMain/ChatBubble.vue'
const router = useRouter()
const route = useRoute() 


const props = defineProps({
  conversationId: {
    type: String,
    default: ''
  },
  userId: {
    type: String,
    default: 'anonymous'
  }
})

const messages = ref([])
const draftMessage = ref('')
const assistantThinking = ref(false)
const messagesContainer = ref(null)

// Observe conversation changes => reload
// watch(() => props.conversationId, async (newVal, oldVal) => {
//   if (newVal && newVal !== oldVal) {
//     messages.value = []
//     await loadFullHistory()
//   }
// })

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId) {
      loadPreviousChat(newId)
    }
  }
)

// On mount => load if we have conversation
onMounted(async () => {
  // if (props.conversationId) {
  //   await loadFullHistory()
  // }
})

async function loadFullHistory() {
  if (!props.conversationId) return
  try {
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/newsletter_chat/history/${props.conversationId}`,
      {
        headers: { 'x-user-id': props.userId }
      }
    )
    const data = resp.data
    if (Array.isArray(data.messages)) {
      messages.value = data.messages.map(parseMessage)
    } else {
      messages.value = []
    }
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('[ChatView] Error loading conversation history:', err)
    messages.value = []
  }
}
let userIdStatic="user_2sfDzHK9r5FkXrufqoAFjnjGNPk"
let convIdStatic="db5ff51c-2886-46f6-bbda-6f041ad69a41"
async function loadPreviousChat(convId) {
  try {
    // if (missingKeys.value.length > 0) {
    //   alert(`Missing required keys: ${missingKeys.value.join(', ')}`)
    //   return
    // }

    // const uid = userId.value || 'anonymous'
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/chat/history/${userIdStatic}/${convIdStatic}`, 
      {}, 
      
    )
      console.log(resp)
      filterChat(resp.data)
  } catch (err) {
    console.error('Error creating new chat:', err)
    alert('Failed to create new conversation. Check keys or console.')
  }
}

const emit = defineEmits(['agentThoughtsDataChanged'])

const messagesData = ref([])
const agentThoughtsData = ref([])

const filterChat=(msgData)=>{

  messagesData.value=msgData.messages.filter(message => message.event === "completion");

  agentThoughtsData.value=msgData.messages.filter(message => message.event === "think");


  emit('agentThoughtsDataChanged', agentThoughtsData.value)


}

// Marked config => GFM, line breaks, highlight
function renderMarkdown(content) {
  marked.setOptions({
    gfm: true,
    breaks: true,
    smartypants: true,
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value
      }
      return hljs.highlightAuto(code).value
    }
  })
  return marked(content || '')
}

function parseMessage(msg) {
  return {
    ...msg,
    typing: false,
    formattedContent: renderMarkdown(msg.content)
  }
}

// Submit user message => call API => push assistant reply
async function sendMessage() {
  const txt = draftMessage.value.trim()
  if (!txt || !props.conversationId) return

  const userMsg = {
    role: 'user',
    content: txt,
    typing: false,
    formattedContent: renderMarkdown(txt)
  }
  messages.value.push(userMsg)
  draftMessage.value = ''
  assistantThinking.value = true
  await nextTick()
  scrollToBottom()

  try {
    const resp = await axios.post(
      `${import.meta.env.VITE_API_URL}/newsletter_chat/message/${props.conversationId}`,
      { message: txt },
      {
        headers: { 'x-user-id': props.userId }
      }
    )
    const assistantReply = resp.data.assistant_response || ''
    const assistantMsg = {
      role: 'assistant',
      content: assistantReply,
      typing: false,
      formattedContent: renderMarkdown(assistantReply)
    }
    messages.value.push(assistantMsg)
  } catch (err) {
    console.error('[ChatView] Error sending message:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Error: Could not process your message.',
      typing: false,
      formattedContent: 'Error: Could not process your message.'
    })
  } finally {
    assistantThinking.value = false
    await nextTick()
    scrollToBottom()
  }
}

// Scroll after rendering
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
/* Loader animation for 'typing' placeholder */
.loader-dots {
  width: 15px;
  height: 3px;
  position: relative;
}
.loader-dots::before,
.loader-dots::after,
.loader-dots > div {
  content: '';
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #9ca3af;
  position: absolute;
  animation: loader-dots 0.8s infinite ease-in-out;
}
.loader-dots::before {
  left: 0;
}
.loader-dots > div {
  left: 6px;
}
.loader-dots::after {
  left: 12px;
}
@keyframes loader-dots {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Syntax highlighting background, code block style */
.hljs {
  background: #f9fafb;
  padding: 0.5em;
  border-radius: 4px;
  overflow-x: auto;
}

/* For <h1>, <h2>, <h3> etc. plus paragraphs, lists, etc. using tailwind typography */
.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}
.prose p {
  margin: 0.5rem 0;
}
.prose ul, .prose ol {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}
.prose li {
  margin: 0.25rem 0;
}

.hljs-keyword {
  color: #7c3aed;
  font-weight: bold;
}
.hljs-string {
  color: #15803d;
}
</style>
