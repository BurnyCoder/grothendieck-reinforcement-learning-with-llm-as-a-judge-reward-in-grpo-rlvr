// TRL num_tokens is cumulative, while step_time describes one optimizer interval.
// https://huggingface.co/docs/trl/grpo_trainer#logged-metrics
export function latestStepMetrics(events) {
  return events.filter(e => e.kind === 'training_metrics' && Number.isFinite(e.metrics?.num_tokens)).at(-1);
}

export function stepThroughput(events) {
  const current = latestStepMetrics(events);
  if (!current || !(current.metrics.step_time > 0)) return null;
  const previous = events.filter(e => e.kind === 'training_metrics' && e.step === current.step - 1
    && Number.isFinite(e.metrics?.num_tokens)).at(-1);
  if (!previous && current.step !== 1) return null;
  const tokens = current.metrics.num_tokens - (previous?.metrics.num_tokens ?? 0);
  return tokens >= 0 ? tokens / current.metrics.step_time : null;
}
