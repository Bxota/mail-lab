<script setup>
import { ref } from 'vue'
const to = ref('test1@dev.local')
const subject = ref('Hello from Vue')
const text = ref('Bonjour !')
const html = ref('<h2>Bonjour</h2>')
const smtpUser = ref('')
const smtpPass = ref('')
const files = ref([])
function onFiles(e) {
  files.value = Array.from(e.target.files || [])
}

async function send() {
  const fd = new FormData()
  fd.append('to', to.value)
  fd.append('subject', subject.value)
  fd.append('text', text.value)
  fd.append('html', html.value)
  fd.append('smtp_user', smtpUser.value)
  fd.append('smtp_pass', smtpPass.value)
  for (const f of files.value) fd.append('files', f)

  const r = await fetch('http://localhost:8000/mail/send_multipart', {
    method: 'POST',
    body: fd
  })
  if (!r.ok) {
    alert('Erreur envoi')
    return
  }
  alert('Envoyé')
}
</script>

<template>
  <div class="space-y-2">
    <input v-model="to" placeholder="to"/>
    <input v-model="subject" placeholder="subject"/>
    <textarea v-model="text" placeholder="text"></textarea>
    <textarea v-model="html" placeholder="html (optionnel)"></textarea>
    <div class="flex gap-2">
      <input v-model="smtpUser" placeholder="SMTP user (optionnel)"/>
      <input v-model="smtpPass" type="password" placeholder="SMTP pass (optionnel)"/>
    </div>
    <input type="file" multiple @change="onFiles" />
    <button @click="send">Envoyer</button>
  </div>
</template>