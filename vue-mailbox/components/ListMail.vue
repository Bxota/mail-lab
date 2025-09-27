<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
const mails = ref([])
const selected = ref(null)
const attachments = computed(() => (selected.value?.attachments || []))
const user = ref('test1')
const password = ref('pass1')
let timer = null
let debounce = null

async function load() {
  const params = new URLSearchParams({ user: user.value, password: password.value })
  const r = await fetch(`http://localhost:8000/mail/messages?${params.toString()}`)
  const json = await r.json()
  mails.value = json.messages
}
async function openMail(id) {
  const params = new URLSearchParams({ user: user.value, password: password.value })
  const r = await fetch(`http://localhost:8000/mail/messages/${id}?${params.toString()}`)
  selected.value = await r.json()
}

function downloadAttachment(idx) {
  const params = new URLSearchParams({ user: user.value, password: password.value })
  const url = `http://localhost:8000/mail/messages/${selected.value.id}/attachments/${idx}?${params.toString()}`
  // open in new tab to trigger download
  window.open(url, '_blank')
}

function parseEmail(raw) {
  if (!raw) return { headers: {}, subject: '', from: '', to: '', date: '', isHtml: false, body: '' }
  const text = String(raw)
  // Split headers/body
  const sep = /\r?\n\r?\n/
  const parts = text.split(sep)
  const headerText = parts[0] || ''
  const bodyText = parts.slice(1).join('\n\n')

  // Unfold headers (lines starting with space or tab are continuations)
  const lines = headerText.split(/\r?\n/)
  const unfolded = []
  for (const line of lines) {
    if (/^[\t ]/.test(line) && unfolded.length) {
      unfolded[unfolded.length - 1] += ' ' + line.trim()
    } else {
      unfolded.push(line)
    }
  }

  const headers = {}
  for (const l of unfolded) {
    const idx = l.indexOf(':')
    if (idx > -1) {
      const k = l.slice(0, idx).trim()
      const v = l.slice(idx + 1).trim()
      headers[k.toLowerCase()] = v
    }
  }
  const subject = headers['subject'] || ''
  const from = headers['from'] || ''
  const to = headers['to'] || ''
  const date = headers['date'] || ''

  // Simple heuristic: render HTML if it looks like HTML
  const isHtml = /<html[\s>]|<body[\s>]|<div[\s>]|<p[\s>]/i.test(bodyText)
  return { headers, subject, from, to, date, isHtml, body: bodyText }
}

const parsed = computed(() => parseEmail(selected.value?.raw))
onMounted(() => {
  load()
  timer = setInterval(load, 5000)
})

watch([user, password], () => {
  // Clear current selection when switching account
  selected.value = null
  if (debounce) clearTimeout(debounce)
  debounce = setTimeout(load, 300)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="grid grid-cols-2 gap-4">
    <div>
      <h3>Inbox</h3>
      <div class="mb-2 flex gap-2 items-end">
        <label class="flex flex-col text-sm">
          <span>Login</span>
          <input v-model="user" placeholder="ex: test1" class="border px-2 py-1" />
        </label>
        <label class="flex flex-col text-sm">
          <span>Password</span>
          <input v-model="password" type="password" placeholder="pass1" class="border px-2 py-1" />
        </label>
        <button @click="load" class="border px-2 py-1">Refresh</button>
      </div>
      <ul>
        <li v-for="m in mails" :key="m.id">
          <button @click="openMail(m.id)">{{ m.subject }} — {{ m.from }}</button>
        </li>
      </ul>
    </div>
    <div v-if="selected" class="space-y-3">
      <div>
        <h3 class="text-lg font-semibold">{{ parsed.subject || '(sans sujet)' }}</h3>
        <div class="text-sm text-gray-600">
          <div><span class="font-medium">From:</span> {{ parsed.from }}</div>
          <div><span class="font-medium">To:</span> {{ parsed.to }}</div>
          <div v-if="parsed.date"><span class="font-medium">Date:</span> {{ parsed.date }}</div>
        </div>
      </div>

      <div class="border rounded p-3 bg-white">
        <template v-if="parsed.isHtml">
          <div v-html="parsed.body"></div>
        </template>
        <template v-else>
          <pre style="white-space: pre-wrap; margin: 0;">{{ parsed.body }}</pre>
        </template>
      </div>

      <div v-if="attachments.length" class="space-y-1">
        <h4 class="font-medium">Pièces jointes</h4>
        <ul class="list-disc pl-5">
          <li v-for="att in attachments" :key="att.index">
            <button class="underline" @click="downloadAttachment(att.index)">
              {{ att.filename }} ({{ att.content_type }}, {{ att.size }} o)
            </button>
          </li>
        </ul>
      </div>

      <details class="text-sm">
        <summary class="cursor-pointer select-none">Afficher les en-têtes</summary>
        <pre class="mt-2 p-2 bg-gray-50 border rounded" style="white-space: pre-wrap;">{{ selected.raw.split(/\r?\n\r?\n/)[0] }}</pre>
      </details>
    </div>
  </div>
</template>