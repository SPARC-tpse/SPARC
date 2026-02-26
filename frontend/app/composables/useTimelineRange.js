export const TIMELINE_RANGE_OPTIONS = [
  { value: 'today', label: 'Heute' },
  { value: '7d', label: '7 Tage' },
  { value: '14d', label: '14 Tage' },
  { value: '1m', label: '1 Monat' }
]

const VALID_RANGES = new Set(TIMELINE_RANGE_OPTIONS.map(option => option.value))

export function normalizeTimelineRange(rawValue) {
  const value = String(rawValue || '').trim()
  return VALID_RANGES.has(value) ? value : '7d'
}

export function buildTimelineWindow(rangeValue, referenceMs = Date.now()) {
  const range = normalizeTimelineRange(rangeValue)
  let spanHours = 7 * 24
  let tickStepHours = 12

  if (range === 'today') {
    spanHours = 24
    tickStepHours = 2
  } else if (range === '7d') {
    spanHours = 7 * 24
    tickStepHours = 12
  } else if (range === '14d') {
    spanHours = 14 * 24
    tickStepHours = 24
  } else {
    spanHours = 30 * 24
    tickStepHours = 48
  }

  const halfSpanMs = (spanHours * 60 * 60 * 1000) / 2
  const startMs = Math.round(referenceMs - halfSpanMs)
  const endMs = Math.round(referenceMs + halfSpanMs)

  return {
    startMs,
    endMs,
    tickStepHours
  }
}
