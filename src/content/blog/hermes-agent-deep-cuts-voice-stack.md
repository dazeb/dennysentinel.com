---
title: "Hermes Agent Deep Cuts: The Voice Stack — STT, TTS, and Voice Mode"
description: "Hermes ships a full speech pipeline — voice messages auto-transcribed, responses read aloud, and a voice-to-voice conversation mode — all configurable across six STT and seven TTS providers."
pubDate: "Jul 20 2026"
heroImage: "/hermes-agent-deep-cuts-voice-stack.jpg"
---

I'm running Hermes Agent v0.18.2, and this post is part of the Deep Cuts series exploring lesser-known features that ship with Hermes but don't get the spotlight they deserve.

Most Hermes users interact with the agent through text — the terminal CLI, Telegram DMs, or Discord channels. That's natural. It's an agent framework, not a voice assistant. But Hermes actually ships a **full speech pipeline** that covers both directions: transcribing spoken input (speech-to-text, STT) and speaking responses aloud (text-to-speech, TTS). It works across the CLI and every messaging platform. And unlike voice features bolted onto other agent frameworks, Hermes's stack is modular, provider-agnostic, and runs without any API key at all for the local path.

Here's what most people don't know: you can have a **full voice-to-voice conversation** with Hermes from the terminal by running `/voice on`, and it costs exactly $0 if you use the local stack. Voice messages sent on Telegram, Discord, WhatsApp, Slack, or Signal are auto-transcribed and injected as text into the conversation automatically. The agent sees the transcript as a normal user message.

## The STT Stack: Six Providers, Four Tiers of Friction

Speech-to-text is the inbound side — taking a voice recording and converting it to text that the agent can process. Hermes supports six providers, resolved by priority order:

**Tier 1 — Local (free, no API key):**
```
pip install faster-whisper
```
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) is a CTranslate2 reimplementation of OpenAI's Whisper. It runs entirely on-device, supports 99 languages, and requires no internet connection and no API key. Configured in `~/.hermes/config.yaml`:

```yaml
stt:
  enabled: true
  provider: local
  local:
    model: base   # tiny, base, small, medium, large-v3
```

This is the recommended starting point for most users. The `base` model runs comfortably on any machine with 4GB+ RAM and transcribes in roughly real-time.

**Tier 2 — Groq Whisper (free tier, cloud):**
Set `GROQ_API_KEY` in your `.env` and switch to `provider: groq`. Groq's hardware acceleration makes Whisper runs fast — often faster than real-time on short clips. The free tier is generous enough for light daily use.

**Tier 3 — OpenAI Whisper API (paid, cloud):**
Set `VOICE_TOOLS_OPENAI_KEY` in `.env`. OpenAI's hosted Whisper is the most accurate option, especially for accented or noisy audio. Costs $0.006/minute. Best for production deployments where accuracy matters more than cost.

**Tier 4 — Mistral Voxtral (paid):**
Set `MISTRAL_API_KEY` in `.env`. Mistral's Voxtral model handles both STT and TTS from a single model — a clean architectural choice if you're already using Mistral as your LLM provider.

**Auto-detection:** Hermes probes providers in priority order at startup. Set `stt.enabled: true` and it picks the first available backend without manual configuration.

## The TTS Stack: Seven Providers, from Free to Premium

Text-to-speech is the outbound side — converting the agent's text responses into spoken audio. Hermes supports seven TTS providers:

| Provider | Quality | Cost | Env Variable |
|---|---|---|---|
| Edge TTS | Good | Free | None |
| NeuTTS (local) | Moderate | Free | `pip install neutts[all]` + `espeak-ng` |
| Google Gemini TTS | Excellent | Free tier | `GEMINI_API_KEY` |
| OpenAI TTS | Excellent | Paid | `VOICE_TOOLS_OPENAI_KEY` |
| ElevenLabs | Premium | Paid | `ELEVENLABS_API_KEY` |
| MiniMax | Good | Paid | `MINIMAX_API_KEY` |
| Mistral Voxtral | Excellent | Paid | `MISTRAL_API_KEY` |

**Edge TTS** is the free default — no configuration needed. It uses Microsoft's neural TTS engine and produces natural-sounding speech. Good enough for daily use.

**ElevenLabs** is the premium option — its voice cloning and emotional range are unmatched. If you want Hermes to sound like a specific voice, this is the provider.

**NeuTTS** is the fully local option. Install with `pip install neutts[all]` and system package `espeak-ng`. Lower quality but entirely offline.

Install the full voice stack with:
```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[voice]"
cd ~/.hermes/hermes-agent && uv pip install -e ".[tts-premium]"
```

The `.[voice]` extra installs the CLI recording and STT dependencies. `.[tts-premium]` pulls in ElevenLabs, OpenAI TTS, and MiniMax support.

## The Three Voice Modes

Hermes exposes three distinct voice experiences:

**`/voice on` — Full voice-to-voice conversation.** The agent listens to your microphone, transcribes what you said, processes it, and reads the response aloud. A bidirectional audio loop. Best for hands-free operations.

**`/voice tts` — Text-to-speech only.** You type your messages normally, but Hermes reads responses aloud. Useful when you want to keep your eyes on code while hearing the agent's analysis.

**`/voice off` — Text-only.** Disables all voice processing. The default.

On messaging platforms (Telegram, Discord), voice messages are **always auto-transcribed** when STT is enabled — no `/voice` toggle needed. Send a voice message to your Hermes bot and it arrives as text in the conversation. This is configured via `stt.enabled: true` and works with zero per-platform setup.

## A Hidden Gem: The CLI Recording Engine

The CLI voice mode includes a surprisingly sophisticated recording engine:

```yaml
voice:
  record_key: "ctrl+b"          # Key to start/stop recording
  max_recording_seconds: 120    # Maximum recording length
  auto_tts: false               # Auto-enable TTS when voice mode starts
  beep_enabled: true            # Play record start/stop beeps
  silence_threshold: 200        # RMS level (0-32767) for silence detection
  silence_duration: 3.0         # Seconds of silence before auto-stop
```

The silence detection is the killer feature here. Hit `Ctrl+B`, start speaking, and when you go silent for 3 seconds Hermes auto-stops the recording and processes what you said. You don't need to press a button to stop — the agent figures out when you're done.

Combined with automatic push-to-talk in the gateway, this means you can speak a question to Hermes on Telegram, get an answer back as TTS audio, and never type a single character.

## Why This Feature Is Obscure

Three reasons:

1. **The install step is non-obvious.** The `.[voice]` and `.[tts-premium]` extras aren't default. Pulling Hermes from PyPI or the install script doesn't include them. You have to explicitly install the voice extras from the source checkout.

2. **No runtime discovery.** There's no `/voice status` or `/voice list-providers` command to tell you which STT/TTS provider is active. You have to check `config.yaml` and your `.env` to know what's configured.

3. **The messaging platform story is invisible.** Voice message transcription "just works" on Telegram and Discord — but there's no indicator that it happened. The voice message arrives as text, and unless you know Hermes does STT, you'd assume the platform itself transcribed it.

## A Practical Scenario

You're deploying Hermes as an ops assistant on a home server. The server is headless — no monitor, no keyboard. You manage it from your phone via Telegram.

You're on the go and a cron job fires — a build failure, a disk alert, something time-sensitive. Instead of typing out the error, you open Telegram, hold the voice record button, and say: "Hermes, what just happened with the build? Summarize the last cron job."

Your voice message arrives at the Hermes gateway. The STT pipeline transcribes it (via local faster-whisper or Groq). The agent reads the cron logs and constructs a response. On Telegram, the response appears as both text and a playable audio file (via TTS). You listen while walking.

No typing required on either end. And if you're using Edge TTS or local STT, it costs zero dollars.

## A Gotcha: The Voice Extras Are Not in the PyPI Package

This is the one that trips people up. Running `pip install hermes-agent` or using the install script gives you a working agent, but voice features won't work until you explicitly install the extras from the source directory:

```bash
cd ~/.hermes/hermes-agent
uv pip install -e ".[voice]"
uv pip install -e ".[tts-premium]"
```

The installer's `.hermes/hermes-agent/` directory is a full git clone, so `uv pip install -e ".[voice]"` works — it just doesn't happen automatically. Also note: on some platforms the `[voice]` extra conflicts with the bundled `pip` in the Hermes venv, which is stripped for distribution. Using `uv` instead of `pip` avoids that issue.

The full voice documentation lives at [Voice & TTS](https://hermes-agent.nousresearch.com/docs/user-guide/features/tts) and [Voice Mode](https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode) on the Hermes Agent docs site, including the detailed config reference and the per-platform messaging voice behavior.
