// Saved optimizer metrics, including resumed runs, must remain interpretable.
import test from 'node:test';
import assert from 'node:assert/strict';
import {latestStepMetrics, stepThroughput} from '../site/training-metrics.mjs';

const row = (step, tokens, seconds) => ({kind:'training_metrics', step,
  elapsed_seconds:seconds, metrics:{num_tokens:tokens, step_time:seconds, loss:.1}});

test('resumed throughput uses the token delta over the optimizer interval', () => {
  assert.equal(stepThroughput([row(1, 100, 20), row(2, 180, 10)]), 8);
});
test('final aggregate logs do not hide the last optimizer loss and throughput', () => {
  const events = [row(1, 100, 20), {kind:'training_metrics', step:1, metrics:{train_loss:.1}}];
  assert.equal(stepThroughput(events), 5);
  assert.equal(latestStepMetrics(events).metrics.loss, .1);
});
test('missing earlier steps and reset counters cannot fabricate throughput', () => {
  assert.equal(stepThroughput([row(2, 100, 10)]), null);
  assert.equal(stepThroughput([row(1, 100, 20), row(3, 300, 10)]), null);
  assert.equal(stepThroughput([row(1, 100, 20), row(2, 80, 10)]), null);
  assert.equal(stepThroughput([]), null);
});
