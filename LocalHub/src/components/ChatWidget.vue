<template>
  <div class="chat-widget" :class="{ open }">
    <button class="chat-toggle" @click="toggle">
      <span v-if="!open">💬</span>
      <span v-else>✕</span>
    </button>

    <div class="chat-panel" v-if="open">
      <div class="chat-header">LocalHub 챗봇</div>

      <div class="messages" ref="msgBox">
        <div v-for="(m, i) in history" :key="i" :class="['msg', m.role]">
          <img v-if="m.role==='assistant'" class="avatar" src="/public/avatar-bot.png" alt="bot"/>
          <div class="bubble">
            <div class="text">{{ m.text }}</div>
            <div class="meta">{{ m.time }}</div>
          </div>
          <img v-if="m.role==='user'" class="avatar user-avatar" src="/public/avatar-user.png" alt="me"/>
        </div>
      </div>

      <form class="chat-input" @submit.prevent="send">
        <input v-model="input" placeholder="질문을 입력하세요. 예: '강남 맛집 추천'" />
        <button :disabled="sending">{{ sending ? '전송중...' : '전송' }}</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChatWidget",
  props: {
    region: { type: String, default: null }
  },
  data() {
    return {
      open: false,
      input: "",
      history: [],
      sending: false
    };
  },
  methods: {
    toggle() { this.open = !this.open; this.$nextTick(this.scrollBottom); },
    timeNow() { return new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}); },
    scrollBottom() { const el = this.$refs.msgBox; if(el) el.scrollTop = el.scrollHeight; },
    async send() {
      if (!this.input.trim()) return;
      const text = this.input.trim();
      this.history.push({ role: 'user', text, time: this.timeNow() });
      this.input = "";
      this.sending = true;
      this.scrollBottom();

      try {
        const payload = { message: text, history: this.history.map(h=>({role:h.role, text:h.text})), region: this.region };
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        const reply = data.reply || "응답이 없습니다.";
        this.history.push({ role: 'assistant', text: reply, time: this.timeNow() });
        this.$emit('chat-reply', data);
      } catch (e) {
        this.history.push({ role: 'assistant', text: "서버 오류가 발생했습니다.", time: this.timeNow() });
      } finally {
        this.sending = false;
        this.$nextTick(this.scrollBottom);
      }
    }
  }
};
</script>

<style scoped>
.chat-widget { position: fixed; right: 18px; bottom: 18px; z-index: 2000; font-family: "Helvetica Neue", Arial, sans-serif; }
.chat-toggle {
  width: 56px; height: 56px; border-radius: 28px; background:#ffcd00; color:#3b2f2f; border:none;
  box-shadow: 0 8px 20px rgba(0,0,0,0.2); cursor:pointer; display:flex; align-items:center; justify-content:center;
}
.chat-panel {
  width: 360px; max-width: calc(100vw - 36px); height: 580px;
  background:#fff; border-radius:12px; box-shadow:0 18px 40px rgba(0,0,0,0.25);
  display:flex; flex-direction:column; overflow:hidden; margin-bottom:12px;
}
.chat-header { padding:12px 16px; background:#f7f9fb; font-weight:700; border-bottom:1px solid #eee; color:#333; }
.messages { flex:1; padding:16px; overflow:auto; display:flex; flex-direction:column; gap:12px; background: linear-gradient(#fff,#fbfbfd); }
.msg { display:flex; align-items:flex-end; gap:10px; width:100%; }
.msg.assistant { justify-content:flex-start; }
.msg.user { justify-content:flex-end; }

.avatar { width:36px; height:36px; border-radius:18px; object-fit:cover; }
.user-avatar { border: 2px solid rgba(0,0,0,0.06); }

.bubble {
  max-width: 72%; padding:10px 12px; border-radius:14px; display:inline-block; position:relative;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}
.msg.assistant .bubble {
  margin-right: auto;
  background: #c8e0ff; /* 연한 블루 */
  color: #072a49;      /* 진한 블루 텍스트 */
  border-bottom-left-radius: 6px;
}

.msg.user .bubble {
  margin-left: auto;
  background: #ffb3d6; /* 연한 핑크 */
  color: #2a0a2a;      /* 어두운 텍스트 */
  border-bottom-right-radius: 6px;
}

/* small meta/time under message */
.meta { font-size:11px; color:rgba(0,0,0,0.45); margin-top:6px; text-align:right; }

/* input area */
.chat-input { display:flex; gap:8px; padding:12px; border-top:1px solid #eee; background:#fff; }
.chat-input input { flex:1; padding:10px 12px; border-radius:20px; border:1px solid #e6e6e6; outline:none; }
.chat-input button { padding:8px 14px; background:#ffcd00; color:#3b2f2f; border:none; border-radius:12px; cursor:pointer; }

/* responsive */
@media (max-width:600px) {
  .chat-panel { width: calc(100vw - 24px); height: 60vh; right:12px; bottom:12px; }
  .chat-toggle { width:48px; height:48px; border-radius:24px; }
}
</style>