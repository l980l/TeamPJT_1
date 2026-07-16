<template>
  <div class="chat-widget">
    <div class="chat-panel" v-if="open">
      <div class="chat-header">
        <div class="chat-header__avatar">🧭</div>
        <div class="chat-header__group">
          <div class="chat-header__title">LocalHub 도우미</div>
          <div class="chat-header__status"><span class="chat-header__dot"></span>서울 지역 정보 안내 중</div>
        </div>
        <button class="chat-header__close" @click="toggle" aria-label="닫기">✕</button>
      </div>

      <div class="chat-body" ref="msgBox">
        <div v-for="(m, i) in history" :key="i" :class="['msg', m.role === 'user' ? 'user' : 'bot']">
          <div v-if="m.role !== 'user'" class="msg__ava">🧭</div>
          <div class="msg__col">
            <div class="msg__bubble">{{ m.text }}</div>

            <div v-if="m.items && m.items.length" class="place-list">
              <a v-for="(it, idx) in m.items.slice(0, 3)" :key="idx" class="place-card" href="/map">
                <div class="place-card__img"><span class="place-card__tag">📍 추천 장소</span></div>
                <div class="place-card__body">
                  <div class="place-card__name">{{ placeName(it) }}</div>
                  <div class="place-card__addr" v-if="placeAddr(it)">📍 {{ placeAddr(it) }}</div>
                  <span class="place-card__map">🗺 지도에서 위치 보기</span>
                </div>
              </a>
            </div>
          </div>
        </div>

        <div class="quicks" v-if="!hasUserMessage">
          <button type="button" class="quick" v-for="q in quickReplies" :key="q" @click="sendQuick(q)">{{ q }}</button>
        </div>

        <div v-if="sending" class="msg bot">
          <div class="msg__ava">🧭</div>
          <div class="msg__bubble msg__bubble--typing">
            <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
          </div>
        </div>
      </div>

      <form class="chat-input" @submit.prevent="send">
        <input v-model="input" placeholder="궁금한 지역 정보를 물어보세요" />
        <button class="chat-send" type="submit" :disabled="sending" aria-label="전송">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z" stroke-linejoin="round"/></svg>
        </button>
      </form>
    </div>

    <div class="fab" v-else @click="toggle">
      <div class="fab__btn">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8"><path d="M4 12a8 8 0 1 1 3.2 6.4L4 20l1.2-3.6A7.96 7.96 0 0 1 4 12Z" stroke-linejoin="round"/></svg>
        <span class="fab__badge" v-if="showBadge">1</span>
      </div>
      <span class="fab__label">지역 안내 챗봇</span>
    </div>
  </div>
</template>

<script>
function timeNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const GREETING = '안녕하세요! 서울의 관광지·맛집·축제 정보를 안내해 드려요. 무엇이 궁금하세요?'

export default {
  name: "ChatWidget",
  props: {
    region: { type: String, default: null }
  },
  data() {
    return {
      open: false,
      hasOpenedOnce: false,
      input: "",
      history: [{ role: 'assistant', text: GREETING, time: timeNow() }],
      sending: false,
      quickReplies: ['🎉 이번 주 축제', '🍜 근처 맛집', '📍 관광지 추천']
    };
  },
  computed: {
    hasUserMessage() {
      return this.history.some(m => m.role === 'user')
    },
    showBadge() {
      return !this.hasOpenedOnce
    }
  },
  methods: {
    timeNow,
    toggle() {
      this.open = !this.open
      if (this.open) this.hasOpenedOnce = true
      this.$nextTick(this.scrollBottom)
    },
    scrollBottom() { const el = this.$refs.msgBox; if (el) el.scrollTop = el.scrollHeight; },
    placeName(it) { return (it || '').split(' — ')[0] || it },
    placeAddr(it) {
      const parts = (it || '').split(' — ')
      return parts.slice(1).join(' — ').trim()
    },
    sendQuick(q) {
      this.input = q.replace(/^\S+\s/, '')
      this.send()
    },
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
        this.history.push({ role: 'assistant', text: reply, time: this.timeNow(), items: data.items || [] });
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
.chat-widget {
  --coral: #ee7a52;
  --coral-soft: #f2946f;
  --purple: #4b3f9e;
  --purple-soft: #6b78e8;
  --purple-tint: #efeafb;
  --ink: #2b2b3a;
  --ink-soft: #6b6b7b;
  --ink-faint: #a6a6b4;
  --line: #ececf1;

  text-align: left;
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 2000;
  font-family: 'Pretendard', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* ===== floating button ===== */
.fab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.fab__btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--purple), var(--purple-soft));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 22px rgba(75, 63, 158, 0.4);
  position: relative;
  transition: transform .16s ease, box-shadow .16s ease;
}

.fab:hover .fab__btn {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(75, 63, 158, 0.48);
}

.fab__badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--coral);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
}

.fab__label {
  font-size: 11px;
  color: var(--ink-faint);
  font-weight: 500;
  background: #fff;
  padding: 3px 9px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(40, 30, 90, 0.08);
}

/* ===== chat panel ===== */
.chat-panel {
  width: 360px;
  max-width: calc(100vw - 36px);
  height: 560px;
  max-height: calc(100vh - 100px);
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 18px 44px rgba(40, 30, 90, 0.2);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
}

.chat-header {
  background: linear-gradient(120deg, #5647ab, #4257c0);
  color: #fff;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 11px;
  flex-shrink: 0;
}

.chat-header__avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  flex-shrink: 0;
}

.chat-header__group { flex: 1; min-width: 0; }

.chat-header__title {
  font-size: 15px;
  font-weight: 700;
}

.chat-header__status {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 1px;
}

.chat-header__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6ee7a8;
  flex-shrink: 0;
}

.chat-header__close {
  background: rgba(255, 255, 255, 0.16);
  border: none;
  color: #fff;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  cursor: pointer;
  font-size: 15px;
  flex-shrink: 0;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px 16px;
  background: #faf9fd;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg {
  display: flex;
  gap: 8px;
  max-width: 90%;
}

.msg.user {
  align-self: flex-end;
  max-width: 78%;
}

.msg__ava {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--purple-tint);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.msg__col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.msg__bubble {
  font-size: 13.5px;
  line-height: 1.6;
  padding: 11px 14px;
  border-radius: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg.bot .msg__bubble {
  background: #fff;
  color: var(--ink);
  border: 1px solid var(--line);
  border-top-left-radius: 4px;
}

.msg.user .msg__bubble {
  background: var(--purple);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg__bubble--typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 13px 16px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ink-faint);
  animation: typing-bounce 1.1s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: .15s; }
.typing-dot:nth-child(3) { animation-delay: .3s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: .5; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* place card inside bot answer */
.place-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.place-card {
  display: block;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  text-decoration: none;
  color: inherit;
  transition: transform .12s ease, box-shadow .12s ease;
}

.place-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(40, 30, 90, 0.1);
}

.place-card__img {
  height: 60px;
  background: linear-gradient(135deg, #cfd3f2, #e6dcf0);
  position: relative;
}

.place-card__tag {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 10.5px;
  font-weight: 600;
  color: #fff;
  background: rgba(43, 34, 60, 0.7);
  padding: 3px 8px;
  border-radius: 12px;
}

.place-card__body {
  padding: 10px 12px;
}

.place-card__name {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink);
}

.place-card__addr {
  font-size: 11.5px;
  color: var(--ink-soft);
  margin-top: 2px;
}

.place-card__map {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--purple);
  background: var(--purple-tint);
  padding: 5px 10px;
  border-radius: 8px;
}

/* quick replies */
.quicks {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding: 0 4px;
}

.quick {
  font-size: 12.5px;
  color: var(--purple);
  background: #fff;
  border: 1px solid #ded8f5;
  border-radius: 16px;
  padding: 7px 13px;
  cursor: pointer;
  font-family: inherit;
}

.quick:hover { background: var(--purple-tint); }

.chat-input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--line);
  background: #fff;
  flex-shrink: 0;
}

.chat-input input {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 11px 16px;
  font-family: inherit;
  font-size: 13px;
  background: #faf9fd;
  min-width: 0;
}

.chat-input input:focus {
  outline: none;
  border-color: var(--purple-soft);
}

.chat-send {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background: var(--coral-soft);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background .12s ease;
}

.chat-send:hover:not(:disabled) { background: var(--coral); }
.chat-send:disabled { opacity: .6; cursor: not-allowed; }

/* responsive: fullscreen on mobile */
@media (max-width: 600px) {
  .chat-widget { right: 14px; bottom: 14px; }

  .chat-panel {
    position: fixed;
    top: var(--nav-height, 56px);
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    max-width: 100%;
    height: auto;
    max-height: none;
    border-radius: 0;
  }

  .fab__btn { width: 52px; height: 52px; }
}
</style>
