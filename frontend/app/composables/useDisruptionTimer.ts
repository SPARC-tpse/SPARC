import { computed, onBeforeUnmount } from 'vue';

/**
 * Globaler Timer-Store (Nuxt useState), damit er beim Tabwechsel weiterläuft
 * Zeiten werden als epoch-ms gespeichert
 */
type PopoutPos = { x: number; y: number };

export function useDisruptionTimer() {
  const isRunning = useState<boolean>('disruption-timer:isRunning', () => false);
  const isPaused = useState<boolean>('disruption-timer:isPaused', () => false);

  const startMs = useState<number | null>('disruption-timer:startMs', () => null);
  const pauseStartedMs = useState<number | null>('disruption-timer:pauseStartedMs', () => null);
  const pausedAccumulatedMs = useState<number>('disruption-timer:pausedAccumulatedMs', () => 0);

  const endMs = useState<number | null>('disruption-timer:endMs', () => null);

  // Für UI-Refresh (rAF), echte Zeitberechnung kommt aus Date.now()
  const nowMs = useState<number>('disruption-timer:nowMs', () => Date.now());
  let rafId: number | null = null;

  const popoutVisible = useState<boolean>('disruption-timer:popoutVisible', () => false);
  const popoutPos = useState<PopoutPos>('disruption-timer:popoutPos', () => ({ x: 16, y: 16 }));

  const tick = () => {
    nowMs.value = Date.now();
    rafId = requestAnimationFrame(tick);
  };

  const ensureTicking = () => {
    if (rafId !== null) return;
    rafId = requestAnimationFrame(tick);
  };

  const stopTicking = () => {
    if (rafId === null) return;
    cancelAnimationFrame(rafId);
    rafId = null;
  };

  const elapsedMs = computed(() => {
    if (!startMs.value) return 0;

    const effectiveNow = isRunning.value ? nowMs.value : (endMs.value ?? nowMs.value);

    const total = effectiveNow - startMs.value;
    const paused = pausedAccumulatedMs.value + (isPaused.value && pauseStartedMs.value ? (effectiveNow - pauseStartedMs.value) : 0);

    return Math.max(0, total - paused);
  });

  const formatted = computed(() => {
    const total = elapsedMs.value;
    const sec = Math.floor(total / 1000) % 60;
    const min = Math.floor(total / 60000) % 60;
    const hrs = Math.floor(total / 3600000);
    return `${hrs.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  });

  const start = () => {
    if (isRunning.value) return;

    const now = Date.now();
    startMs.value = now;
    endMs.value = null;

    isRunning.value = true;
    isPaused.value = false;

    pauseStartedMs.value = null;
    pausedAccumulatedMs.value = 0;

    // popoutVisible.value = true;
    ensureTicking();
  };

  const pause = () => {
    if (!isRunning.value || isPaused.value || !startMs.value) return;
    isPaused.value = true;
    pauseStartedMs.value = Date.now();
    ensureTicking();
  };

  const resume = () => {
    if (!isRunning.value || !isPaused.value || !pauseStartedMs.value) return;
    const now = Date.now();
    pausedAccumulatedMs.value += now - pauseStartedMs.value;
    pauseStartedMs.value = null;
    isPaused.value = false;
    ensureTicking();
  };

  const stop = () => {
    if (!isRunning.value || !startMs.value) return;

    const now = Date.now();

    // Wenn im Pause-Modus, pausierte Zeit noch aufsummieren
    if (isPaused.value && pauseStartedMs.value) {
      pausedAccumulatedMs.value += now - pauseStartedMs.value;
      pauseStartedMs.value = null;
    }

    endMs.value = now;
    isRunning.value = false;
    isPaused.value = false;

    stopTicking();
  };

  const reset = () => {
    isRunning.value = false;
    isPaused.value = false;
    startMs.value = null;
    endMs.value = null;
    pauseStartedMs.value = null;
    pausedAccumulatedMs.value = 0;
    stopTicking();
  };

  const toDateTimeLocal = (ms: number) => {
    const d = new Date(ms);
    const pad = (n: number) => n.toString().padStart(2, '0');
    const yyyy = d.getFullYear();
    const MM = pad(d.getMonth() + 1);
    const dd = pad(d.getDate());
    const hh = pad(d.getHours());
    const mm = pad(d.getMinutes());
    const ss = pad(d.getSeconds());
    return `${yyyy}-${MM}-${dd}T${hh}:${mm}:${ss}`;
  };

  const hasNonEmpty = (v: unknown) => (v ?? '').toString().trim().length > 0;

  const stopAndMaybeApply = (target: { start: string; end: string }) => {
    stop();

    if (!startMs.value || !endMs.value) return;

    const hasExistingStart = hasNonEmpty(target.start);
    const hasExistingEnd = hasNonEmpty(target.end);

    if (hasExistingStart || hasExistingEnd) {
      const ok = window.confirm(
        `Start und/oder Endzeit sind bereits eingetragen.\nMöchtest du diese durch die Timer-Zeiten überschreiben?`
      );
      if (!ok) return;
    }

    target.start = toDateTimeLocal(startMs.value);
    target.end = toDateTimeLocal(endMs.value);

    reset()
  };

  onBeforeUnmount(() => {
    stopTicking();
  });

  return {
    // State
    isRunning,
    isPaused,
    startMs,
    endMs,
    elapsedMs,
    formatted,
    popoutVisible,
    popoutPos,

    // Actions
    start,
    pause,
    resume,
    stop,
    stopAndMaybeApply,
    reset,

    // Helpers
    toDateTimeLocal,
  };
}
